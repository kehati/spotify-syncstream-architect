import asyncio

from app.core.logging import logger
from app.services.spotify.base import SpotifyService
from app.services.strategy_manager import StrategyManager
from app.strategies.base import StrategyAction
from app.strategies.strategy_factory import StrategyFactory


class SyncStreamEngine:
    """
    The SyncStream Architect Engine.
    It polls the current playback and applies the active strategy policy.
    """
    def __init__(self, spotify: SpotifyService, strategy_manager: StrategyManager, poll_interval: int = 10):
        self.spotify = spotify
        self.strategy_manager = strategy_manager
        self.poll_interval = poll_interval
        self._stop_event = asyncio.Event()

    async def run(self):
        logger.info("Engine lifecycle started", provider=type(self.spotify).__name__, interval=f"{self.poll_interval}s")

        while not self._stop_event.is_set():
            try:
                await self.apply_strategy()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error("Engine encountered an error during execution", error=str(e))
                await asyncio.sleep(self.poll_interval)


    async def apply_strategy(self):
        """Evaluates the current track against active strategies and takes action."""
        playback = await self.spotify.get_current_playback()
        if not playback or not playback.item or not playback.is_playing:
            logger.info("No active playback found or playback is paused")
            return

        track = playback.item

        active_strategy = await self.strategy_manager.get_active_strategy()
        if not active_strategy:
            logger.warn("No active strategy configured")
            return

        if not track.features:
            track.features = await self.spotify.get_audio_features(track.id)
            if not track.features:
                logger.warning("Missing audio features, cannot evaluate strategy", track_id=track.id)
                return

        action = await StrategyFactory.make(active_strategy).evaluate(track)
        if action == StrategyAction.SKIP:
            logger.info("Policy violated, skipping track", track_name=track.name, track_id=track.id, strategy=active_strategy.__class__.__name__)
            await self.spotify.skip_next()
