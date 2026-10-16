from app.config import POSITION_WEIGHTS, SUPPORTED_FORMATIONS, DEFAULT_FORMATION
from app.engine.player_tools import get_player
from app.models.player import Player

def analyze_team(
    team_list: list[str],
    formation: str = DEFAULT_FORMATION,
    team_id: str = "A",
    team_name: str = ""
) -> dict:
    """
    Deterministic team analysis engine.
    Calculates weighted attack, midfield, defense, average overall, balance, and strength.
    """
    if not team_list:
        raise ValueError("Team is empty")
    if len(team_list) > 5:
        raise ValueError("Team cannot exceed five players")
    if len(set(team_list)) != len(team_list):
        raise ValueError("Duplicate players are not allowed")

    if formation not in SUPPORTED_FORMATIONS:
        # Default fallback if formation not explicitly recognized
        formation = DEFAULT_FORMATION

    players: list[Player] = [get_player(pid) for pid in team_list]

    weighted_attack = 0.0
    weighted_midfield = 0.0
    weighted_defense = 0.0

    weight_att_total = 0.0
    weight_mid_total = 0.0
    weight_def_total = 0.0

    overall_sum = 0.0

    for p in players:
        weights = POSITION_WEIGHTS.get(
            p.position,
            {"attack": 0.33, "midfield": 0.33, "defense": 0.33}
        )
        w_att = weights["attack"]
        w_mid = weights["midfield"]
        w_def = weights["defense"]

        weighted_attack += p.attack * w_att
        weighted_midfield += p.midfield * w_mid
        weighted_defense += p.defense * w_def

        weight_att_total += w_att
        weight_mid_total += w_mid
        weight_def_total += w_def

        overall_sum += p.overall

    # Normalized category ratings (0-100)
    a_team = weighted_attack / weight_att_total if weight_att_total > 0 else 0.0
    m_team = weighted_midfield / weight_mid_total if weight_mid_total > 0 else 0.0
    d_team = weighted_defense / weight_def_total if weight_def_total > 0 else 0.0
    o_team = overall_sum / len(players)

    # Balance formula from proposal:
    # Balance = 100 - (|A - M| + |M - D| + |D - A|) / 3, clamped to 0-100
    spread = (abs(a_team - m_team) + abs(m_team - d_team) + abs(d_team - a_team)) / 3.0
    balance = max(0.0, min(100.0, 100.0 - spread))

    # Strength formula from proposal:
    # Strength = 0.35 * A + 0.30 * M + 0.25 * D + 0.10 * Balance
    strength = (0.35 * a_team) + (0.30 * m_team) + (0.25 * d_team) + (0.10 * balance)

    return {
        "team_id": team_id,
        "team_name": team_name or f"Team {team_id}",
        "formation": formation,
        "player_count": len(players),
        "attack": round(a_team, 2),
        "midfield": round(m_team, 2),
        "defense": round(d_team, 2),
        "overall": round(o_team, 2),
        "balance": round(balance, 2),
        "strength": round(strength, 2),
        "players": [p.model_dump() for p in players]
    }
