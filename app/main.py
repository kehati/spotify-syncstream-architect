import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import strategies, engine
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.redis import redis_manager
from app.core.seeding import seed_strategies
from app.services.engine import SyncStreamEngine
from app.services.spotify.mock import MockSpotifyService
from app.services.spotify.prod import ProdSpotifyService
from app.services.strategy_manager import StrategyManager

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown sequence of SyncStream Architect.
    """

    # Initialize the Redis connection pool
    await redis_manager.connect()
    logger.info("Redis connection pool initialized")

    # Seed strategies in Redis
    await seed_strategies()

    # Initialize Spotify service
    if settings.SPOTIFY_MOCK_MODE:
        spotify_service = MockSpotifyService()
    else:
        if not all([settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET, settings.SPOTIFY_REFRESH_TOKEN]):
            raise ValueError("Spotify credentials are not properly configured in settings")
        spotify_service = ProdSpotifyService(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            refresh_token=settings.SPOTIFY_REFRESH_TOKEN
        )
    if not spotify_service:
        raise RuntimeError("Spotify service initialization failed")
    logger.info("Spotify service initialized", mode="Mock" if settings.SPOTIFY_MOCK_MODE else "PROD")

    # Initialize the engine
    strategy_manager = StrategyManager()
    engine = SyncStreamEngine(spotify=spotify_service, strategy_manager=strategy_manager, poll_interval=settings.ENGINE_POLL_INTERVAL)
    app.state.engine = engine

    # Run the engine as a non-blocking background task
    engine_task = asyncio.create_task(engine.run())
    logger.info("Engine initialized successfully")

    yield

    logger.info("Shutdown sequence initiated")

    # Gracefully stop the Engine loop
    engine.stop()
    await engine_task
    logger.info("Engine stopped successfully")

    # Close Redis connection pool
    await redis_manager.disconnect()
    logger.info("Redis connection pool closed")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan, debug=settings.DEBUG)
app.include_router(strategies.router, prefix="/api")
app.include_router(engine.router, prefix="/api")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Spotify SyncStream Architect is live",
        "status": "online"
    }
