from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging, logger

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    logger.info(
        "Application starting up",
        mode="Mock" if settings.MOCK_MODE else "PROD",
        redis_url=str(settings.REDIS_URL)
    )

    # This is where the Redis Pool should be initialized
    # app.state.redis = await init_redis_pool()

    yield

    # --- Shutdown Logic ---
    logger.info("Application shutting down")
    # await app.state.redis.close()

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Spotify SyncStream Architect is live",
        "status": "online"
    }
