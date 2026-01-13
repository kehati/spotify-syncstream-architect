import asyncio

from app.core.logging import logger


async def refresh_token_task(spotify_service, interval_seconds: int = 2700):
    """
    Periodically refreshes the Spotify access token
    """
    while True:
        try:
            await spotify_service.apply_refresh_token()
            logger.info("Spotify access token refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing Spotify access token: {e}")
        await asyncio.sleep(interval_seconds)