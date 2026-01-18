import pytest
import asyncio

from app.models.spotify import AudioFeatures, SpotifyTrack
from app.strategies.base import StrategyAction
from app.strategies.implementations.energy_floor import EnergyFloorStrategy
from app.strategies.implementations.focus_guard import FocusGuardStrategy
from app.strategies.implementations.vibe_shift import VibeShiftStrategy


@pytest.fixture
def mock_track_factory():
    """Returns a factory function to create AudioFeatures object"""
    def _create_track(instrumentalness=0.5, energy=0.5, valence=0.5):
         return SpotifyTrack(
            id="test_track",
            name="Test Track",
            uri="spotify:track:test_track",
            duration_ms=200000,
            explicit=False,
            popularity=50,
            artists=[],
            album=None,
            features=AudioFeatures(
                id="test_features",
                instrumentalness=instrumentalness,
                energy=energy,
                valence=valence,
                danceability=0.5,
                tempo=120.0
            )
        )
    return _create_track

class TestFocusGuardStrategy:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "instrumental,energy,expected_action", [
            (0.80, 0.40, StrategyAction.KEEP),  # Perfect focus track
            (0.70, 0.40, StrategyAction.SKIP),  # Too many lyrics (low instrumentalness)
            (0.90, 0.60, StrategyAction.SKIP),  # Too high energy
            (0.10, 0.90, StrategyAction.SKIP),  # High energy lyrical pop
        ])
    async def test_focus_guard_strategy(self, mock_track_factory, instrumental, energy, expected_action):
        strategy = FocusGuardStrategy(instrumental_threshold=0.75, energy_threshold=0.5)
        track = mock_track_factory(instrumentalness=instrumental, energy=energy)
        action = await strategy.evaluate(track)
        assert action == expected_action

class TestEnergyFloorStrategy:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "energy,expected_action", [
            (0.80, StrategyAction.KEEP),  # Above energy floor
            (0.60, StrategyAction.SKIP),  # Below energy floor
        ])
    async def test_energy_floor_strategy(self, mock_track_factory, energy, expected_action):
        strategy = EnergyFloorStrategy(energy_floor=0.7)
        track = mock_track_factory(energy=energy)
        action = await strategy.evaluate(track)
        assert action == expected_action

class TestVibeShftStrategy:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "valence,expected_action", [
            (0.80, StrategyAction.KEEP),  # Happy vibe
            (0.40, StrategyAction.SKIP),  # Sad vibe
        ])
    async def test_vibe_shift_strategy(self, mock_track_factory, valence, expected_action):
        strategy = VibeShiftStrategy(min_valence=0.7, max_valence=0.9)
        track = mock_track_factory(valence=valence)
        action = await strategy.evaluate(track)
        assert action == expected_action