import uuid
from app.config import DEFAULT_FORMATION
from app.engine.player_tools import get_all_players
from app.models.game import GameState, Team

# In-memory storage for active game sessions
_GAMES: dict[str, GameState] = {}

def create_game(
    game_id: str | None = None,
    team_a_name: str = "Team Alpha",
    team_b_name: str = "Team Beta",
    formation_a: str = DEFAULT_FORMATION,
    formation_b: str = DEFAULT_FORMATION,
    first_turn: str = "A",
    draft_mode: str = "alternating",
) -> GameState:
    """Initializes and stores a fresh two-player drafting session."""
    if not game_id:
        game_id = f"game_{uuid.uuid4().hex[:8]}"

    # Populate available pool from full player catalog
    all_players = get_all_players()
    available_ids = list(all_players.keys())

    if draft_mode == "snake":
        if first_turn == "B":
            draft_order = ["B", "A", "A", "B", "B", "A", "A", "B", "B", "A"]
        else:
            draft_order = ["A", "B", "B", "A", "A", "B", "B", "A", "A", "B"]
        starting_turn = draft_order[0]
    else:
        draft_order = None
        starting_turn = first_turn

    game = GameState(
        game_id=game_id,
        teams={
            "A": Team(team_id="A", name=team_a_name, player_ids=[], formation=formation_a),
            "B": Team(team_id="B", name=team_b_name, player_ids=[], formation=formation_b),
        },
        available_player_ids=available_ids,
        current_turn=starting_turn,
        draft_round=1,
        status="drafting",
        draft_mode=draft_mode,
        draft_order=draft_order,
    )
    _GAMES[game_id] = game
    return game

def get_game(game_id: str) -> GameState:
    """Retrieves an existing game state by ID."""
    game = _GAMES.get(game_id)
    if game is None:
        raise ValueError(f"Game not found with ID: {game_id}")
    return game

def reset_game(game_id: str) -> GameState:
    """Resets an existing game session while keeping the same ID and team names."""
    old_game = get_game(game_id)
    return create_game(
        game_id=game_id,
        team_a_name=old_game.teams["A"].name,
        team_b_name=old_game.teams["B"].name,
        formation_a=old_game.teams["A"].formation,
        formation_b=old_game.teams["B"].formation,
    )

def clear_all_games() -> None:
    """Clears all games from memory (useful for test resets)."""
    _GAMES.clear()
