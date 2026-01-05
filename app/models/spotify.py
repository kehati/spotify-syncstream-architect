from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class SpotifyImage(BaseModel):
    url: str
    height: Optional[int] = None
    width: Optional[int] = None

class AudioFeatures(BaseModel):
    """
    Official Spotify Audio Features Object.
    Documentation: https://developer.spotify.com/documentation/web-api/reference/get-audio-features
    """
    id: str
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    time_signature: int

class SpotifyArtist(BaseModel):
    id: str
    name: str
    external_urls: Dict[str, str]

class SpotifyAlbum(BaseModel):
    id: str
    name: str
    images: List[SpotifyImage]
    release_date: Optional[str] = None

class SpotifyTrack(BaseModel):
    """
    Official Spotify Track Object (Simplified).
    Documentation: https://developer.spotify.com/documentation/web-api/reference/get-track
    """
    id: str
    name: str
    uri: str
    duration_ms: int
    explicit: bool
    popularity: int
    artists: List[SpotifyArtist]
    album: SpotifyAlbum
    features: Optional[AudioFeatures] = None

class PlaybackState(BaseModel):
    """
    Official Spotify Currently Playing Object.
    Documentation: https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback
    """
    timestamp: int
    is_playing: bool
    progress_ms: Optional[int] = None
    item: Optional[SpotifyTrack] = None  # The track currently playing
    currently_playing_type: str  # 'track' or 'episode'