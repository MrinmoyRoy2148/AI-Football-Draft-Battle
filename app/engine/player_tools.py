import json
from app.config import DATA_PATH
from app.models.player import Player

_PLAYERS_CACHE: dict[str, Player] = {}

def load_players() -> dict[str, Player]:
    """Loads all footballers from the static JSON dataset."""
    global _PLAYERS_CACHE
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Player dataset file not found at {DATA_PATH}")
    
    with open(DATA_PATH, mode="r", encoding="utf-8") as f:
        data = json.load(f)
        _PLAYERS_CACHE = {item["id"]: Player(**item) for item in data}
    return _PLAYERS_CACHE

def get_all_players() -> dict[str, Player]:
    """Returns the cached players dictionary, loading if empty."""
    if not _PLAYERS_CACHE:
        return load_players()
    return _PLAYERS_CACHE

def get_player(player_id: str) -> Player:
    """Finds a single player by ID or raises ValueError if not found."""
    players = get_all_players()
    player = players.get(player_id)
    if player is None:
        raise ValueError(f"Unknown player: {player_id}")
    return player

def get_player_stats(player_id: str) -> dict:
    """Returns player stats dictionary for tool-calling/API use."""
    player = get_player(player_id)
    return player.model_dump()
