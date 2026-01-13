from typing import Any, Optional, Dict
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

class ActiveStrategyUpdate(BaseModel):
    """
    Model for updating the active strategy.
    """
    id: str = Field(..., description="The ID of the strategy to be set as active")

class EngineStatus(BaseModel):
    """
    Model representing the status of the playback engine.
    """
    active_strategy_id: str
    is_running: bool
    last_evaluation: Optional[Dict[str, Any]] = None
    current_track: Optional[Dict[str, Any]] = None