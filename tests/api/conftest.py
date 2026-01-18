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
def mock_engine(mock_strategy_manager):
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
    mock_engine.last_evaluation = None
    mock_engine.current_track = None

    # 4. Methods
    mock_engine.run = AsyncMock(return_value=None)
    mock_engine.stop = Mock(return_value=None)
    mock_engine.apply_strategy = AsyncMock(return_value=None)

    return mock_engine

@pytest.fixture
async def client(mock_engine, mock_strategy_manager):
    """
    Provides a FastAPI test client with the StrategyManager and SyncStreamEngine mocked.
    """

    @asynccontextmanager
    async def noop_lifespan(app: FastAPI):
        yield

    original_lifespan = app.router.lifespan_context
    app.router.lifespan_context = noop_lifespan
    app.state.engine = mock_engine
    target_object = "app.api.v1.strategies.manager"

    with patch(target_object, mock_strategy_manager):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.router.lifespan_context = original_lifespan
    if hasattr(app.state, "engine"):
        del app.state.engine