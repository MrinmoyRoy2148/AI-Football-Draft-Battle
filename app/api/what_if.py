from fastapi import APIRouter, HTTPException, status
from app.models.game import WhatIfRequest
from app.models.analysis import WhatIfResponse
from app.services.game_state import get_game
from app.services.analyst_service import analyze_what_if

router = APIRouter(prefix="/api", tags=["What-If Strategy"])

@router.post("/what-if", response_model=WhatIfResponse, summary="Simulate hypothetical player/formation changes")
async def api_what_if(request: WhatIfRequest):
    try:
        game = get_game(request.game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        response = await analyze_what_if(
            game=game,
            team_id=request.team_id,
            player_out=request.player_out,
            player_in=request.player_in,
            formation=request.formation,
        )
        return response
    except ValueError as e:
        err_msg = str(e)
        if "not found" in err_msg.lower() or "unknown player" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Simulation failed: {str(e)}")
