from collections import deque

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import logger


class RedisManager:
    def __init__(self):
        self.pool: redis.ConnectionPool | None = None

    async def connect(self):
        """Initialize the Connection Pool and the primary client"""
        logger.info("Initializing Redis connection pool", url=str(settings.REDIS_URL))
        try:
            self.pool = redis.ConnectionPool.from_url(settings.REDIS_URL,
                                                      encoding="utf-8",
                                                      decode_responses=True,
                                                      max_connections=20)

            # Perform a health check
            client = redis.Redis(connection_pool=self.pool)
            await client.ping()
            logger.info("Redis connection pool initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Redis connection pool", error=str(e))
            raise e

    async def disconnect(self):
        """Close the Connection Pool and all associated connections"""
        try:
            await self.pool.disconnect()
            logger.info("Redis connection pool disconnected successfully")
        except Exception as e:
            logger.error("Failed to disconnect Redis connection pool", error=str(e))
            raise e

    def get_client(self) -> redis.Redis:
        """Returns a Redis client instance"""
        if not self.pool:
            raise RuntimeError("Redis connection pool is not initialized. Call connect() first.")
        return redis.Redis(connection_pool=self.pool)


redis_manager = RedisManager()
