from app.core.logging import logger
from app.models.spotify import SpotifyTrack
from app.strategies.base import StrategyAction


class FocusGuardStrategy:
    """
    Ensures that only tracks suitable for focused work are kept in the playback
    Logic: High Instrumentalness and Low Energy = Deep Work
    """

    def __init__(self, instrumental_threshold: int = 0.7, energy_threshold: float = 0.5):
        self.instrumental_threshold = instrumental_threshold
        self.energy_threshold = energy_threshold

    def evaluate(self, track: SpotifyTrack) -> StrategyAction:
        if not track.features:
            logger.warning("FocusGuard: Missing audio features, keeping track by default", track_id=track.id)
            return StrategyAction.KEEP

        features = track.features

        focus_condition = (
            features.instrumentalness >= self.instrumental_threshold and
            features.energy <= self.energy_threshold
        )
        if focus_condition:
            return StrategyAction.KEEP
        else:
            logger.info("FocusGuard: Non-focus track detected",
                        track_id=track.id,
                        name=track.name,
                        instrumentalness=features.instrumentalness,
                        energy=features.energy)
            return StrategyAction.SKIP