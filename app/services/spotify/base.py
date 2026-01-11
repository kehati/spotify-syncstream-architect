from typing import Protocol
from app.models.spotify import PlaybackState, AudioFeatures


class SpotifyService(Protocol):
    """
    Interface for Spotify interactions
    """

    async def get_current_playback(self) -> PlaybackState | None:
        """GET /v1/me/player"""

    async def get_audio_features(self, track_id: str) -> AudioFeatures | None:
        """GET /v1/audio-features/{id}"""

    async def skip_next(self) -> bool:
        """POST /v1/me/player/next"""
