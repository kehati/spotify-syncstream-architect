import pytest
from unittest.mock import AsyncMock
from app.models.strategy import StrategyConfig


# --- Helper ---
def create_strategy(id="test"):
    return StrategyConfig(
        id=id,
        name=f"Test {id}",
        description=f"A {id} strategy for testing purposes",
        is_active=True,
        parameters={"param1": "value1", "param2": 10}
    )

@pytest.mark.asyncio
async def test_get_engine_status_running(client, mock_engine, mock_strategy_manager):
    """
    Scenario: GET /api/v1/engine/status
    Expected: Returns 200 OK with JSON reflecting a running engine state.
    """
    mock_strategy_manager.get_active_strategy.return_value = create_strategy("vibes")

    mock_engine._stop_event.is_set.return_value = False  # False means "Running"
    mock_engine.current_track = {
        "id": "trk123",
        "name": "Bohemian Rhapsody",
        "artist": "Queen"
    }

    response = await client.get("/api/v1/engine/status")

    assert response.status_code == 200
    data = response.json()

    assert data["active_strategy_id"] == "vibes"
    assert data["is_running"] is True
    assert data["current_track"]["name"] == "Bohemian Rhapsody"


@pytest.mark.asyncio
async def test_get_engine_status_stopped(client, mock_engine, mock_strategy_manager):
    """
    Scenario: GET /api/v1/engine/status when stopped.
    Expected: Returns 200 OK with is_running=False.
    """
    mock_strategy_manager.get_active_strategy.return_value = create_strategy("vibes")
    mock_engine._stop_event.is_set.return_value = True  # True means "Stopped"
    mock_engine.current_track = None

    response = await client.get("/api/v1/engine/status")

    assert response.status_code == 200
    data = response.json()
    assert data["is_running"] is False
    assert data["current_track"] is None


@pytest.mark.asyncio
async def test_evaluate_strategy_trigger(client, mock_engine):
    """
    Scenario: POST /api/v1/engine/evaluate
    Expected: Triggers engine.apply_strategy() and returns success.
    """
    response = await client.post("/api/v1/engine/evaluate")

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"

    mock_engine.apply_strategy.assert_called_once()


@pytest.mark.asyncio
async def test_evaluate_strategy_error_handling(client, mock_engine):
    """
    Scenario: POST /api/v1/engine/evaluate when engine fails.
    Expected: Returns 500 Internal Server Error.
    """
    mock_engine.apply_strategy.side_effect = RuntimeError("Spotify API Down")
    response = await client.post("/api/v1/engine/evaluate")

    assert response.status_code == 500
    assert "Spotify API Down" in response.json()["detail"]