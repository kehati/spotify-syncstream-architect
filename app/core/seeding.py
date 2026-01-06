from app.core.logging import logger
from app.models.strategy import StrategyConfig
from app.services.strategy_manager import StrategyManager


async def seed_strategies():
    manager = StrategyManager()

    strategies = [
        StrategyConfig(
            id="focus",
            name="Focus Guard",
            description="Skips songs with lyrics or high energy.",
            parameters={"instrumentalness": 0.75, "energy": 0.5},
            is_active=True  # Default to enabled
        ),
        StrategyConfig(
            id="energy",
            name="Energy Floor",
            description="Ensures music energy stays high.",
            parameters={"energy_floor": 0.7},
            is_active=True
        ),
        StrategyConfig(
            id="vibe",
            name="Vibe Shift",
            description="Maintains a positive emotional atmosphere.",
            parameters={"min_valence": 0.6},
            is_active=False  # Seed one as disabled for testing
        )
    ]

    logger.info("Populating strategies in Redis")
    for strategy in strategies:
        await manager.upsert_strategy(strategy)