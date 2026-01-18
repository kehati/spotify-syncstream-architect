from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.engine import SyncStreamEngine
from app.services.strategy_manager import StrategyManager

@pytest.fixture
def mock_strategy_manager():
    """
    Provides a mocked StrategyManager for API tests.
    """
    mock_manager = AsyncMock(spec=StrategyManager)
    mock_manager.get_active_strategy.return_value = None
    mock_manager.get_catalog.return_value = []
    mock_manager.set_active_strategy.return_value = None
    return mock_manager

@pytest.fixture
def mock_engine():
    """
    Provides a mocked SyncStreamEngine for API tests.
    """
    mock_engine = AsyncMock(spec=SyncStreamEngine)

    # 1. Attach the Strategy Manager Mock (Critical Fix)
    mock_engine.strategy_manager = mock_strategy_manager

    # 2. Mock the _stop_event
    # The router calls: not engine._stop_event.is_set()
    mock_engine._stop_event = Mock()
    mock_engine._stop_event.is_set.return_value = False  # Default to "Running"

    # 3. Attributes accessed by the router
    mock_engine.last_evaluation = "2023-10-27T10:00:00"
    mock_engine.current_track = {"name": "Test Track"}

    # 4. Methods
    mock_engine.apply_strategy = AsyncMock(return_value=None)

    return mock_engine

@pytest.fixture
async def client(mock_engine, mock_strategy_manager):
    """
    Provides a FastAPI test client with the StrategyManager and SyncStreamEngine mocked.
    """

    # 1. Define a dummy lifespan that does NOTHING
    @asynccontextmanager
    async def noop_lifespan(app: FastAPI):
        yield

    # 2. Save original lifespan to restore later
    original_lifespan = app.router.lifespan_context

    # 3. OVERRIDE: Stop real startup logic
    app.router.lifespan_context = noop_lifespan

    # 4. INJECT STATE DIRECTLY (The Fix 💉)
    # We force the mock into the state immediately, guaranteeing it exists.
    app.state.engine = mock_engine

    # 5. Patch the StrategyManager instance in the router
    # (Make sure this path matches your router's import exactly)
    target_object = "app.api.v1.strategies.manager"

    with patch(target_object, mock_strategy_manager):
        transport = ASGITransport(app=app)

        # 6. Start the Client
        # 'async with' triggers the lifespan (our noop_lifespan),
        # but since we already injected the state, we are safe.
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    # 7. Cleanup
    app.router.lifespan_context = original_lifespan
    if hasattr(app.state, "engine"):
        del app.state.engine


