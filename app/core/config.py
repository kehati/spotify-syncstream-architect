from typing import Optional

from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Spotify SyncStream Architect"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Redis Settings
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"

    # Spotify Settings
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    MOCK_MODE: bool = True

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

settings = Settings()
