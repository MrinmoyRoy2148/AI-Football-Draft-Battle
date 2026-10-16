from app.config import DEFAULT_FORMATION
from app.engine.team_analyzer import analyze_team

def compare_teams(
    team_a_ids: list[str],
    team_b_ids: list[str],
    formation_a: str = DEFAULT_FORMATION,
    formation_b: str = DEFAULT_FORMATION,
    team_a_name: str = "Team A",
    team_b_name: str = "Team B"
) -> dict:
    """
    Compares two drafted teams across all deterministic dimensions.
    Returns individual statistics and category deltas (Team A minus Team B).
    """
    stats_a = analyze_team(team_a_ids, formation=formation_a, team_id="A", team_name=team_a_name)
    stats_b = analyze_team(team_b_ids, formation=formation_b, team_id="B", team_name=team_b_name)

    attack_diff = round(stats_a["attack"] - stats_b["attack"], 2)
    midfield_diff = round(stats_a["midfield"] - stats_b["midfield"], 2)
    defense_diff = round(stats_a["defense"] - stats_b["defense"], 2)
    overall_diff = round(stats_a["overall"] - stats_b["overall"], 2)
    balance_diff = round(stats_a["balance"] - stats_b["balance"], 2)
    strength_diff = round(stats_a["strength"] - stats_b["strength"], 2)

    if strength_diff > 0.05:
        leader = team_a_name or "Team A"
    elif strength_diff < -0.05:
        leader = team_b_name or "Team B"
    else:
        leader = "Tied"

    return {
        "team_a_stats": stats_a,
        "team_b_stats": stats_b,
        "attack_diff": attack_diff,
        "midfield_diff": midfield_diff,
        "defense_diff": defense_diff,
        "overall_diff": overall_diff,
        "balance_diff": balance_diff,
        "strength_diff": strength_diff,
        "leader": leader
    }
