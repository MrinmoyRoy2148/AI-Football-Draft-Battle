from fastapi import APIRouter, HTTPException, status
from app.models.game import CreateGameRequest, DraftRequest, GameState, UpdateFormationRequest
from app.engine.player_tools import get_all_players
from app.services.game_state import create_game, get_game, reset_game
from app.services.draft_service import process_draft_pick

router = APIRouter(prefix="/api", tags=["Draft & Game"])

@router.get("/players", summary="Get all football players in catalog")
def list_players():
    players = get_all_players()
    return [p.model_dump() for p in players.values()]

@router.post("/game/create", response_model=GameState, summary="Create a new draft game session")
def api_create_game(request: CreateGameRequest):
    game = create_game(
        game_id=request.game_id,
        team_a_name=request.team_a_name or "Team Alpha",
        team_b_name=request.team_b_name or "Team Beta",
        formation_a=request.formation_a or "1-1-1-2",
        formation_b=request.formation_b or "1-1-1-2",
        first_turn=request.first_turn or "A",
        draft_mode=request.draft_mode or "alternating",
    )
    return game

@router.post("/game/{game_id}/formation", response_model=GameState, summary="Update team formations")
def api_update_formation(game_id: str, request: UpdateFormationRequest):
    try:
        game = get_game(game_id)
        if request.formation_a:
            game.teams["A"].formation = request.formation_a
        if request.formation_b:
            game.teams["B"].formation = request.formation_b
        return game
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/game/{game_id}", response_model=GameState, summary="Get current game state")
def api_get_game(game_id: str):
    try:
        return get_game(game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/game/{game_id}/reset", response_model=GameState, summary="Reset an active game session")
def api_reset_game(game_id: str):
    try:
        return reset_game(game_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/draft", response_model=GameState, summary="Draft a player for the current turn")
def api_draft_player(request: DraftRequest):
    try:
        updated_game = process_draft_pick(request.game_id, request.player_id)
        return updated_game
    except ValueError as e:
        # Match blueprint status codes: 404 for missing player, 400 for rules violations
        err_msg = str(e)
        if "not found" in err_msg.lower() or "does not exist" in err_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
