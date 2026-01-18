import pytest
from app.models.strategy import StrategyConfig
from app.services.strategy_manager import StrategyManager


# Helper to create dummy strategies
def create_strategy(id: str, active: bool = True):
    return StrategyConfig(
        id=f"{id}",
        name=f"Test {id}",
        description=f"A {id} strategy for testing purposes",
        is_active=active,
        parameters={"param1": "value1", "param2": 10}
    )

@pytest.mark.asyncio
class TestStrategyManager:

    async def test_create_and_update_strategy(self, strategy_manager, redis_client):
        strategy = create_strategy("focus")
        await strategy_manager.upsert_strategy(strategy)
        saved_strategy = await redis_client.hget(StrategyManager.STRATEGIES_CATALOG_KEY, strategy.id)
        assert saved_strategy is not None
        assert StrategyConfig.model_validate_json(saved_strategy).id == strategy.id

    async def test_get_catalog(self, strategy_manager):
        strategy1 = create_strategy("s1")
        strategy2 = create_strategy("s2", active=False)
        await strategy_manager.upsert_strategy(strategy1)
        await strategy_manager.upsert_strategy(strategy2)

        catalog = await strategy_manager.get_catalog(only_active=True)
        assert len(catalog) == 1
        assert catalog[0].id == "s1"

    async def test_set_and_get_active_strategy(self, strategy_manager, redis_client):
        await strategy_manager.upsert_strategy(create_strategy("my_vibe", active=True))

        await strategy_manager.set_active_strategy("my_vibe")

        active_id = await redis_client.get("strategies:active_id")
        assert active_id == "my_vibe"
