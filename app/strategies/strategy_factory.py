from app.models.strategy import StrategyConfig
from app.strategies.implementations.energy_floor import EnergyFloorStrategy
from app.strategies.implementations.focus_guard import FocusGuardStrategy
from app.strategies.implementations.vibe_shift import VibeShiftStrategy


class StrategyFactory:
    @staticmethod
    def make(config: StrategyConfig):
        """
        Instantiates the strategy implementation from a strategy config
        """
        params = config.parameters or {}

        if config.id == "focus":
            return FocusGuardStrategy(
                instrumental_threshold=params.get("instrumentalness", 0.75),
                energy_threshold=params.get("energy", 0.5)
            )
        elif config.id == "energy":
            return EnergyFloorStrategy(
                energy_floor=params.get("energy_floor", 0.7)
            )
        elif config.id == "vibe":
            return VibeShiftStrategy(
                min_valence=params.get("min_valence", 0.6),
                max_valence=params.get("max_valence", 1.0)
            )

        raise ValueError(f"No implementation found for strategy: {config.id}")