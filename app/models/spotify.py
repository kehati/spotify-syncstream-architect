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
    energy: float
    instrumentalness: float
    valence: float

    danceability: Optional[float] = 0.5
    key: Optional[int] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    acousticness: Optional[float] = None
    liveness: Optional[float] = None
    tempo: Optional[float] = None
    duration_ms: Optional[int] = None
    time_signature: Optional[int] = None

class SpotifyArtist(BaseModel):
    id: str
    name: str
    external_urls: Optional[Dict[str, str]] = None

class SpotifyAlbum(BaseModel):
    id: str
    name: str
    images: List[SpotifyImage] = []
    release_date: Optional[str] = None
    uri: Optional[str] = None
    duration_ms: Optional[int] = 0
    explicit: Optional[bool] = False
    popularity: Optional[int] = 0
    artists: List[SpotifyArtist] = []
    features: Optional[AudioFeatures] = None

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
    timestamp: Optional[int] = Field(default=0)
    is_playing: bool = False
    progress_ms: Optional[int] = None
    item: Optional[SpotifyTrack] = None
    currently_playing_type: Optional[str] = "track"