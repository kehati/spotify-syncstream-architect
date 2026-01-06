from app.core.redis import redis_manager
from app.models.strategy import StrategyConfig


class StrategyManager:
    STRATEGIES_CATALOG_KEY = "strategies:catalog"
    ACTIVE_STRATEGY_KEY = "strategies:active_id"

    async def get_catalog(self, only_active: bool = False) -> list[StrategyConfig]:
        """Retrieve all strategy configurations"""
        client = redis_manager.get_client()
        strategies = await client.hgetall(self.STRATEGIES_CATALOG_KEY)
        strategies_catalog = [StrategyConfig.model_validate_json(strategy) for strategy in strategies.values()]
        if only_active:
            return [strategy for strategy in strategies_catalog if strategy.is_active]
        return strategies_catalog

    async def set_active_strategy(self, strategy_id: str):
        """Set an active strategy"""
        client = redis_manager.get_client()
        strategy = await client.hget(self.STRATEGIES_CATALOG_KEY, strategy_id)
        if not strategy:
            raise ValueError(f"Strategy id: '{strategy_id}' does not exist")
        if not StrategyConfig.model_validate_json(strategy).is_active:
            raise ValueError(f"Strategy id: '{strategy_id}' is dsabled")
        await client.set(self.ACTIVE_STRATEGY_KEY, strategy_id)

    async def get_active_strategy(self) -> StrategyConfig:
        """Get the currently active strategy configuration"""
        client = redis_manager.get_client()
        return await client.get(self.ACTIVE_STRATEGY_KEY)

    async def upsert_strategy(self, strategy: StrategyConfig):
        """Create or update a strategy configuration"""
        client = redis_manager.get_client()
        await client.hset(self.STRATEGIES_CATALOG_KEY, strategy.id, strategy.model_dump_json())
