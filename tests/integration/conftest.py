import os
from unittest.mock import patch

import pytest
import redis.asyncio as redis

from app.core.redis import redis_manager
from app.services.strategy_manager import StrategyManager


@pytest.fixture
async def redis_client():
    """
    Provides a clean, real Redis connection for integration tests.
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))

    client = redis.Redis(host=host, port=port, db=1, encoding="utf-8", decode_responses=True)

    await client.flushdb()  # Ensure a clean state before tests
    yield client
    await client.aclose()  # Clean up after tests

@pytest.fixture(autouse=True)
def patch_global_redis_manager(redis_client):
    """
    Patch the global redis_manager to use the test redis_client.
    """
    with patch.object(redis_manager, 'get_client', return_value=redis_client):
        yield

@pytest.fixture
def strategy_manager():
    """
    Provides a StrategyManager instance ready for testing.
    """
    return StrategyManager()
