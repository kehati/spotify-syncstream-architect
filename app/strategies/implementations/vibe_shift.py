from app.strategies.base import StrategyAction
from app.models.spotify import SpotifyTrack
from app.core.logging import logger


class VibeShiftStrategy:
    """
    Maintains a specific emotional tone
    Logic: Filters based on 'Valence' (0.0 = Sad/Gloomy, 1.0 = Happy/Cheerful)
    """

    def __init__(self, min_valence: float = 0.0, max_valence: float = 1.0):
        self.min_valence = min_valence
        self.max_valence = max_valence

    def evaluate(self, track: SpotifyTrack) -> StrategyAction:
        if not track.features:
            return StrategyAction.KEEP

        valence = track.features.valence

        if self.min_valence <= valence <= self.max_valence:
           return StrategyAction.KEEP

        logger.info(
            "VibeShift: Skipping out-of-vibe track",
            name=track.name,
            valence=valence,
            range=f"{self.min_valence}-{self.max_valence}"
        )
        return StrategyAction.SKIP