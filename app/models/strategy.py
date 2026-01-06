from typing import Any
from pydantic import BaseModel, Field


class StrategyConfig(BaseModel):
    """
    A persistent model for a Playback Strategy.
    Stored as a Redis Hash.
    """
    id: str = Field(..., description="Unique identifier for the strategy")
    name: str = Field(..., description="Display name of the strategy")
    description: str = Field(..., description="Detailed description of the strategy")
    is_active: bool = Field(default=True, description="Indicates whether the strategy is currently active")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Custom parameters for the strategy")