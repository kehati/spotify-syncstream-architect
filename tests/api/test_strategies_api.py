import pytest
from app.models.strategy import StrategyConfig

# Helper to create dummy strategies
def create_strategy(id: str, active: bool = True):
    return StrategyConfig(
        id=id,
        name=f"Test {id}",
        description=f"A {id} strategy for testing purposes",
        is_active=active,
        parameters={"param1": "value1", "param2": 10}
    )

@pytest.mark.asyncio
async def test_get_catalog_returns_list(client, mock_strategy_manager):
    """
    Scenario: GET /api/v1/strategies/
    Expected: Returns 200 OK and a JSON list of strategies.
    """
    mock_strategy_manager.get_catalog.return_value = [
        create_strategy("s1"),
        create_strategy("s2")
    ]

    response = await client.get("/api/v1/strategies/")
    assert response.status_code == 200
    strategies = response.json()
    assert isinstance(strategies, list)
    assert len(strategies) == 2
    assert strategies[0]["id"] == "s1"
    assert strategies[1]["id"] == "s2"

@pytest.mark.asyncio
async def test_set_active_strategy(client, mock_strategy_manager):
    """
    Scenario: POST /api/v1/strategies/active
    Expected: Sets the active strategy and returns 200 OK with the active strategy details.
    """
    mock_strategy_manager.set_active_strategy.return_value = None
    mock_strategy_manager.get_active_strategy.return_value = create_strategy("s1")

    payload = {"id": "s1"}
    response = await client.post("/api/v1/strategies/active", json=payload)
    assert response.status_code == 200
    active_strategy = response.json()
    assert active_strategy["id"] == "s1"

@pytest.mark.asyncio
async def test_get_active_strategy(client, mock_strategy_manager):
    """
    Scenario: GET /api/v1/strategies/active
    Expected: Returns 200 OK and the currently active strategy.
    """
    mock_strategy_manager.get_active_strategy.return_value = create_strategy("s1")

    response = await client.get("/api/v1/strategies/active")
    assert response.status_code == 200
    active_strategy = response.json()
    assert active_strategy["id"] == "s1"

@pytest.mark.asyncio
async def test_get_active_strategy_not_found(client, mock_strategy_manager):
    """
    Scenario: GET /api/v1/strategies/active when no active strategy is set.
    Expected: Returns 404 Not Found.
    """
    mock_strategy_manager.get_active_strategy.side_effect = ValueError("No active strategy configured")

    response = await client.get("/api/v1/strategies/active")
    assert response.status_code == 404
    error_detail = response.json()
    assert "No active strategy configured" in error_detail["detail"]

@pytest.mark.asyncio
async def test_update_strategy(client, mock_strategy_manager):
    """
    Scenario: PUT /api/v1strategies/{strategy_id}
    Expected: Updates the strategy and returns 200 OK with the updated strategy details.
    """
    strategy = create_strategy("s1")
    mock_strategy_manager.upsert_strategy.return_value = None

    payload = {
        "id": "s1",
        "name": "Updated Strategy",
        "description": "An updated strategy for testing purposes",
        "is_active": True,
        "parameters": {"param1": "new_value", "param2": 20}
    }
    response = await client.put("/api/v1/strategies/s1", json=payload)
    assert response.status_code == 200
    updated_strategy = response.json()
    assert updated_strategy["id"] == "s1"
    assert updated_strategy["name"] == "Updated Strategy"

