from enum import Enum
from typing import Protocol, runtime_checkable

from app.models.spotify import SpotifyTrack


class StrategyAction(Enum):
    KEEP = "keep"
    SKIP = "skip"

@runtime_checkable
class PlaybackStrategy(Protocol):
    """
    Any object that can evaluate a track and return an action
    is a valid PlaybackStrategy.
    """
    async def evaluate(self, track: SpotifyTrack) -> StrategyAction:
        """This method should evaluate whether a track should be kept or skipped"""
