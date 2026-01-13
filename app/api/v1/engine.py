from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/v1/engine", tags=["Engine"])

@router.get("/status", summary="Get the current status of the SyncStream Engine")
async def get_engine_status(request: Request):
    """Retrieve the current status of the SyncStream Engine."""
    engine = request.app.state.engine
    try:
        active_strategy = await engine.strategy_manager.get_active_strategy()
        return {
            "active_strategy_id": active_strategy.id,
            "is_running": not engine._stop_event.is_set(),
            "last_evaluation": engine.last_evaluation if hasattr(engine, 'last_evaluation') else None,
            "current_track": engine.current_track if hasattr(engine, 'current_track') else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", summary="Manually trigger strategy evaluation")
async def evaluate_strategy(request: Request):
    """Manually trigger the strategy evaluation process."""
    engine = request.app.state.engine
    try:
        await engine.apply_strategy()
        return {
            "status": "success",
            "message": "Strategy evaluation triggered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))