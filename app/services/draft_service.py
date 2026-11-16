from app.engine.player_tools import get_all_players
from app.services.game_state import get_game
from app.models.game import GameState

def process_draft_pick(game_id: str, player_id: str) -> GameState:
    """
    Authoritative backend draft execution:
    - Validates game status
    - Validates player availability
    - Adds to current player's roster (up to 5)
    - Toggles turn between A and B
    - Sets game status to 'completed' once both teams have 5 players
    """
    game = get_game(game_id)
    all_players = get_all_players()

    if game.status != "drafting":
        raise ValueError("Draft is already completed for this game")

    if player_id not in all_players:
        raise ValueError(f"Player {player_id} does not exist in dataset")

    if player_id not in game.available_player_ids:
        raise ValueError(f"Player {player_id} is no longer available to draft")

    current_team_id = game.current_turn
    current_team = game.teams[current_team_id]

    if len(current_team.player_ids) >= 5:
        raise ValueError(f"Team {current_team_id} already has a full 5-player squad")

    # Perform draft selection
    current_team.player_ids.append(player_id)
    game.available_player_ids.remove(player_id)
    game.last_drafted_player_id = player_id
    game.last_drafted_by = current_team_id

    # Check if both teams are full (5 players each = 10 total picks)
    team_a_count = len(game.teams["A"].player_ids)
    team_b_count = len(game.teams["B"].player_ids)
    total_picked = team_a_count + team_b_count

    if team_a_count == 5 and team_b_count == 5:
        game.status = "completed"
    else:
        # Determine next turn based on draft mode
        if game.draft_mode == "snake" and game.draft_order and total_picked < len(game.draft_order):
            game.current_turn = game.draft_order[total_picked]
        else:
            # Alternate turn
            game.current_turn = "B" if current_team_id == "A" else "A"
        game.draft_round += 1

    return game
