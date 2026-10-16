import math
from app.config import PROBABILITY_K

def calculate_win_probability(team_a_stats: dict, team_b_stats: dict) -> dict:
    """
    Calculates deterministic win probabilities using logistic sigmoid function:
    P(A) = 1 / (1 + e^(-(Strength_A - Strength_B) / k))
    P(B) = 1 - P(A)
    """
    diff = team_a_stats["strength"] - team_b_stats["strength"]
    k = float(PROBABILITY_K)

    # Sigmoid calculation with numerical safety clamp
    clamped_val = max(-60.0, min(60.0, -diff / k))
    p_a = 1.0 / (1.0 + math.exp(clamped_val))
    p_a_pct = round(p_a * 100.0, 2)
    p_b_pct = round(100.0 - p_a_pct, 2)

    return {
        "team_a_win": p_a_pct,
        "team_b_win": p_b_pct
    }
