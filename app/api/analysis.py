from fastapi import APIRouter, HTTPException, status
from app.models.game import AnalyzeRequest
from app.models.analysis import AnalysisResponse
from app.services.game_state import get_game
from app.services.analyst_service import analyze_match

router = APIRouter(prefix="/api", tags=["Analysis"])

@router.post("/analyze", response_model=AnalysisResponse, summary="Analyze completed 5-player teams")
async def api_analyze_match(request: AnalyzeRequest):
    try:
        game = get_game(request.game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    try:
        response = await analyze_match(game)
        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {str(e)}")
