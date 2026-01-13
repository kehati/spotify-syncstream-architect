from typing import List

from fastapi import APIRouter, HTTPException

from app.models.strategy import StrategyConfig, ActiveStrategyUpdate
from app.services.strategy_manager import StrategyManager

router = APIRouter(prefix="/v1/strategies", tags=["strategies"])
manager = StrategyManager()

@router.get("/", response_model=List[StrategyConfig], summary="Get all strategies")
async def get_strategies():
    """Retrieve a list of all available strategies."""
    try:
        return await manager.get_catalog()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active", response_model=StrategyConfig, summary="Get the currently active strategy")
async def get_active_strategy():
    """Retrieve the currently active strategy."""
    try:
        return await manager.get_active_strategy()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/active", response_model=StrategyConfig, summary="Set the active strategy")
async def set_active_strategy(payload: ActiveStrategyUpdate):
    """Set a strategy as the active one."""
    try:
        await manager.set_active_strategy(payload.id)
        return await manager.get_active_strategy()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{strategy_id}", response_model=StrategyConfig, summary="Update a strategy")
async def update_strategy(strategy_id: str, payload: StrategyConfig):
    """Uudate a strategy configuration."""
    try:
        if strategy_id != payload.id:
            raise HTTPException(status_code=400, detail="Strategy ID in path and payload do not match")
        await manager.upsert_strategy(payload)
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



