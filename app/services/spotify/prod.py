import asyncio
from typing import Any

import httpx
from httpx import AsyncClient, HTTPStatusError, HTTPError

from app.core.logging import logger
from app.core.redis import redis_manager
from app.models.spotify import PlaybackState, AudioFeatures


class ProdSpotifyService:
    """
    Production-grade Spotify client
    """

    ACCESS_TOKEN_KEY = "spotify:access_token"
    API_BASE_URL = "https://api.spotify.com/v1"
    AUTH_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token

    async def _get_access_token(self) -> str:
        """Fetch an access token from cache"""
        client = redis_manager.get_redis_client()
        access_token = client.get(self.ACCESS_TOKEN_KEY)
        return access_token.decode("utf-8") if access_token else None

    async def apply_refresh_token(self) -> str:
        """
        Refreshes the Spotify access token and updates the cache
        """
        async with AsyncClient() as client:
            try:
                response = await client.post(
                    self.AUTH_URL,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self.refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                data = response.json()
                access_token = data["access_token"]
                client = redis_manager.get_redis_client()
                await client.set(self.ACCESS_TOKEN_KEY, access_token)
                return access_token
            except HTTPStatusError as e:
                logger.error("Failed to refresh Spotify access token")
                raise

    async def _request(self, method: str, endpoint: str, retry_on_401: bool = True, **kwargs) -> Any:
        """
        Internal request wrapper with error handling and token management
        """
        token = await self._get_access_token()
        if not token:
            token = await self.apply_refresh_token()

        headers = {"Authorization": f"Bearer {token}"}

        async with AsyncClient(base_url=self.API_BASE_URL, headers=headers) as client:
            try:
                response = await client.request(method, endpoint, **kwargs)

                # Handle 401 Unauthorized
                if response.status_code == 401 and retry_on_401:
                    logger.warning("Spotify token expired (401). Retrying with fresh token...")
                    await self.apply_refresh_token()
                    return await self._request(method, endpoint, retry_on_401=False, **kwargs)

                # Handle Rate Limiting - 429 Too Many Requests
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Spotify Rate Limit hit. Backing off for {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._request(method, endpoint, **kwargs)

                response.raise_for_status()

                # Spotify returns 204 No Content for successful skips/commands
                if response.status_code == 204:
                    return True

                return response.json()

            except HTTPError as e:
                logger.error(f"Spotify API request failed: {method} {endpoint}", exc_info=e)
                raise

    async def get_current_playback(self) -> PlaybackState | None:
        """Fetches the user's current playback state"""
        data = self._request("GET", "/me/player")
        if data is None:
            return None
        return PlaybackState(**data)

    async def get_audio_features(self, track_id: str) -> AudioFeatures | None:
        """Fetches audio features of a track"""
        data = await self._request("GET", f"/audio-features/{track_id}")
        if data is None:
            return None
        return AudioFeatures(**data)

    async def skip_next(self) -> bool:
        """Issues the skip command to the active device"""
        return await self._request("POST", "/me/player/next")