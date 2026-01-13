from app.strategies.base import StrategyAction
from app.models.spotify import SpotifyTrack
from app.core.logging import logger


class EnergyFloorStrategy:
    """
    Ensures a high-intensity environment
    Logic: Energy must be >= floor
    """

    def __init__(self, energy_floor: float = 0.7):
        self.energy_floor = energy_floor

    async def evaluate(self, track: SpotifyTrack) -> StrategyAction:
        if not track.features:
            return StrategyAction.KEEP

        energy = track.features.energy

        if energy >= self.energy_floor:
            return StrategyAction.KEEP

        logger.info(
            "EnergyFloor: Skipping low-energy track",
            name=track.name,
            energy=energy,
            floor=self.energy_floor
        )
        return StrategyAction.SKIP