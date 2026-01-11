import random
from typing import Optional
from app.models.spotify import (
    PlaybackState, SpotifyTrack, AudioFeatures,
    SpotifyArtist, SpotifyAlbum, SpotifyImage
)


class MockSpotifyService:
    """
    Spotify API Mock
    """

    async def get_current_playback(self) -> PlaybackState | None:
        # Simulate 'nothing playing' state (5% chance)
        if random.random() < 0.05:
            return None

        # Determine if we're simulating a 'Focus' or 'Non-Focus' track
        is_focus = random.choice([True, False])

        return PlaybackState(
            device={"id": "mock_device", "is_active": True, "name": "Web Player"},
            repeat_state="off",
            shuffle_state=False,
            timestamp=1736240427000,  # Mock 2026 Unix ms
            progress_ms=45000,
            is_playing=True,
            currently_playing_type="track",  # Valid types: track, episode, ad, unknown
            item=SpotifyTrack(
                id=f"mock_id_{'focus' if is_focus else 'noise'}",
                name="Deep Work Focus" if is_focus else "High Energy Vocal Mix",
                uri="spotify:track:mock_uri",
                duration_ms=210000,
                explicit=False,
                popularity=85,
                external_urls={"spotify": "https://open.spotify.com/track/mock"},
                artists=[
                    SpotifyArtist(
                        id="artist_1",
                        name="The SyncStream Architect",
                        external_urls={"spotify": "https://open.spotify.com/artist/1"}
                    )
                ],
                album=SpotifyAlbum(
                    id="album_1",
                    name="Architecture Vol 1",
                    images=[SpotifyImage(url="https://placehold.co/640x640", height=640, width=640)]
                )
            )
        )

    async def get_audio_features(self, track_id: str) -> AudioFeatures | None:
        """Returns features matching the ID hint from get_current_playback."""
        if "focus" in track_id:
            return AudioFeatures(
                id=track_id,
                instrumentalness=0.85,  # High instrumental
                energy=0.3,  # Low energy
                valence=0.4,
                danceability=0.2,
                tempo=110.0,
                loudness=-12.5,
                speechiness=0.02,
                acousticness=0.7
            )

        # 'Noise' track features (triggering skip in Focus Guard)
        return AudioFeatures(
            id=track_id,
            instrumentalness=0.05,  # Vocals present
            energy=0.88,  # High energy
            valence=0.8,
            danceability=0.75,
            tempo=140.0,
            loudness=-5.2,
            speechiness=0.1,
            acousticness=0.1
        )

    async def skip_next(self) -> bool:
        return True