import copy
from app.engine.player_tools import get_player
from app.engine.team_analyzer import analyze_team
from app.engine.probability import calculate_win_probability
from app.models.game import GameState

def simulate_what_if(
    game: GameState,
    team_id: str,
    player_out: str,
    player_in: str,
    formation: str | None = None
) -> dict:
    """
    Simulates a hypothetical roster or formation change.
    Operates on an isolated deep copy without mutating the actual GameState.
    """
    if team_id not in ("A", "B"):
        raise ValueError(f"Invalid team_id: {team_id}")

    target_team = game.teams.get(team_id)
    opponent_id = "B" if team_id == "A" else "A"
    opponent_team = game.teams.get(opponent_id)

    if not target_team or not opponent_team:
        raise ValueError("Both teams must exist in the game state")

    if len(target_team.player_ids) != 5 or len(opponent_team.player_ids) != 5:
        raise ValueError("Both teams must have full 5-player rosters to run What-If simulations")

    # Verification: player_out must be in target_team
    if player_out not in target_team.player_ids:
        raise ValueError(f"Player {player_out} is not currently on Team {team_id}")

    # Verification: player_in must not be on either team
    if player_in in target_team.player_ids:
        raise ValueError(f"Replacement player {player_in} is already on Team {team_id}")
    if player_in in opponent_team.player_ids:
        raise ValueError(f"Replacement player {player_in} is currently on opponent Team {opponent_id}")

    # Verify both players exist in dataset
    p_out_obj = get_player(player_out)
    p_in_obj = get_player(player_in)

    # Isolated temporary copy of the target team's players
    hypothetical_player_ids = copy.deepcopy(target_team.player_ids)
    hypo_formation = formation if formation else target_team.formation

    # Perform swap only in copy
    swap_index = hypothetical_player_ids.index(player_out)
    hypothetical_player_ids[swap_index] = player_in

    # Calculate original stats & probability
    original_target_stats = analyze_team(
        target_team.player_ids,
        formation=target_team.formation,
        team_id=team_id,
        team_name=target_team.name or f"Team {team_id}"
    )
    opponent_stats = analyze_team(
        opponent_team.player_ids,
        formation=opponent_team.formation,
        team_id=opponent_id,
        team_name=opponent_team.name or f"Team {opponent_id}"
    )

    if team_id == "A":
        original_probs = calculate_win_probability(original_target_stats, opponent_stats)
    else:
        # If target is B, calculate A vs B then keep perspective
        raw_probs = calculate_win_probability(opponent_stats, original_target_stats)
        original_probs = {"team_a_win": raw_probs["team_a_win"], "team_b_win": raw_probs["team_b_win"]}

    # Calculate hypothetical stats & probability
    hypothetical_target_stats = analyze_team(
        hypothetical_player_ids,
        formation=hypo_formation,
        team_id=team_id,
        team_name=target_team.name or f"Team {team_id}"
    )

    if team_id == "A":
        hypothetical_probs = calculate_win_probability(hypothetical_target_stats, opponent_stats)
        strength_delta = round(hypothetical_target_stats["strength"] - original_target_stats["strength"], 2)
        prob_delta = round(hypothetical_probs["team_a_win"] - original_probs["team_a_win"], 2)
    else:
        hypothetical_probs = calculate_win_probability(opponent_stats, hypothetical_target_stats)
        strength_delta = round(hypothetical_target_stats["strength"] - original_target_stats["strength"], 2)
        prob_delta = round(hypothetical_probs["team_b_win"] - original_probs["team_b_win"], 2)

    return {
        "target_team_id": team_id,
        "player_out": p_out_obj.model_dump(),
        "player_in": p_in_obj.model_dump(),
        "original_stats": original_target_stats,
        "hypothetical_stats": hypothetical_target_stats,
        "original_probabilities": original_probs,
        "hypothetical_probabilities": hypothetical_probs,
        "strength_delta": strength_delta,
        "probability_delta": prob_delta,
    }
