import logging
from app.engine.team_comparator import compare_teams
from app.engine.probability import calculate_win_probability
from app.engine.what_if_engine import simulate_what_if
from app.agent.prompts import MATCH_ANALYSIS_USER_TEMPLATE, WHAT_IF_USER_TEMPLATE
from app.agent.llm_client import (
    call_llm_analyst,
    generate_heuristic_match_analysis,
    generate_heuristic_what_if_analysis,
)
from app.models.analysis import (
    AnalysisResponse,
    AIAnalysis,
    WhatIfResponse,
    WhatIfComparison,
    TeamComparison,
    ProbabilityResult,
)
from app.models.game import GameState

logger = logging.getLogger("football_analyst_service")

async def analyze_match(game: GameState) -> AnalysisResponse:
    """
    Coordinates the full match analysis:
    1. Deterministic team comparison via Python engine
    2. Deterministic win probability via logistic formula
    3. AI Game Analyst commentary (via LLM or heuristic engine)
    """
    team_a = game.teams.get("A")
    team_b = game.teams.get("B")

    if not team_a or not team_b:
        raise ValueError("Both Team A and Team B must exist")

    if len(team_a.player_ids) != 5 or len(team_b.player_ids) != 5:
        raise ValueError("Both teams must draft exactly 5 players before match analysis")

    # 1. Deterministic comparison
    raw_comparison = compare_teams(
        team_a_ids=team_a.player_ids,
        team_b_ids=team_b.player_ids,
        formation_a=team_a.formation,
        formation_b=team_b.formation,
        team_a_name=team_a.name or "Team Alpha",
        team_b_name=team_b.name or "Team Beta",
    )

    # 2. Deterministic win probability
    raw_probabilities = calculate_win_probability(
        raw_comparison["team_a_stats"],
        raw_comparison["team_b_stats"],
    )

    stats_a = raw_comparison["team_a_stats"]
    stats_b = raw_comparison["team_b_stats"]

    # 3. AI Game Analyst commentary
    ai_analysis_obj: AIAnalysis | None = None

    # Construct prompt for LLM
    roster_a_str = ", ".join(f"{p['name']} ({p['position']})" for p in stats_a["players"])
    roster_b_str = ", ".join(f"{p['name']} ({p['position']})" for p in stats_b["players"])

    prompt = MATCH_ANALYSIS_USER_TEMPLATE.format(
        game_id=game.game_id,
        team_a_name=stats_a["team_name"],
        formation_a=stats_a["formation"],
        team_a_roster=roster_a_str,
        a_att=stats_a["attack"],
        a_mid=stats_a["midfield"],
        a_def=stats_a["defense"],
        a_ovr=stats_a["overall"],
        a_bal=stats_a["balance"],
        a_str=stats_a["strength"],
        team_b_name=stats_b["team_name"],
        formation_b=stats_b["formation"],
        team_b_roster=roster_b_str,
        b_att=stats_b["attack"],
        b_mid=stats_b["midfield"],
        b_def=stats_b["defense"],
        b_ovr=stats_b["overall"],
        b_bal=stats_b["balance"],
        b_str=stats_b["strength"],
        att_diff=raw_comparison["attack_diff"],
        mid_diff=raw_comparison["midfield_diff"],
        def_diff=raw_comparison["defense_diff"],
        bal_diff=raw_comparison["balance_diff"],
        str_diff=raw_comparison["strength_diff"],
        prob_a=raw_probabilities["team_a_win"],
        prob_b=raw_probabilities["team_b_win"],
        leader=raw_comparison["leader"],
    )

    llm_output = await call_llm_analyst(prompt, is_what_if=False)
    if isinstance(llm_output, dict):
        try:
            ai_analysis_obj = AIAnalysis(
                summary=llm_output.get("summary", ""),
                team_a_assessment=llm_output.get("team_a_assessment", ""),
                team_b_assessment=llm_output.get("team_b_assessment", ""),
                key_matchups=llm_output.get("key_matchups", ""),
                tactical_verdict=llm_output.get("tactical_verdict", ""),
                source="llm",
            )
        except Exception:
            ai_analysis_obj = None

    if ai_analysis_obj is None:
        ai_analysis_obj = generate_heuristic_match_analysis(
            comparison=raw_comparison,
            probabilities=raw_probabilities,
            team_a_name=stats_a["team_name"],
            team_b_name=stats_b["team_name"],
        )

    return AnalysisResponse(
        comparison=TeamComparison(**raw_comparison),
        probabilities=ProbabilityResult(**raw_probabilities),
        ai_analysis=ai_analysis_obj,
    )

async def analyze_what_if(
    game: GameState,
    team_id: str,
    player_out: str,
    player_in: str,
    formation: str | None = None
) -> WhatIfResponse:
    """
    Coordinates What-If scenario analysis:
    1. Executes simulation on isolated copy
    2. Generates tactical reasoning for the delta
    """
    raw_what_if = simulate_what_if(game, team_id, player_out, player_in, formation)

    # Prepare prompt for LLM
    p_out = raw_what_if["player_out"]
    p_in = raw_what_if["player_in"]
    orig_s = raw_what_if["original_stats"]
    hypo_s = raw_what_if["hypothetical_stats"]
    orig_p = raw_what_if["original_probabilities"]
    hypo_p = raw_what_if["hypothetical_probabilities"]

    t_key = f"team_{team_id.lower()}_win"
    orig_prob = orig_p[t_key]
    hypo_prob = hypo_p[t_key]

    prompt = WHAT_IF_USER_TEMPLATE.format(
        team_name=orig_s["team_name"],
        team_id=team_id,
        player_out_name=p_out["name"],
        player_out_pos=p_out["position"],
        out_att=p_out["attack"],
        out_mid=p_out["midfield"],
        out_def=p_out["defense"],
        out_ovr=p_out["overall"],
        player_in_name=p_in["name"],
        player_in_pos=p_in["position"],
        in_att=p_in["attack"],
        in_mid=p_in["midfield"],
        in_def=p_in["defense"],
        in_ovr=p_in["overall"],
        formation=raw_what_if["hypothetical_stats"]["formation"],
        orig_str=orig_s["strength"],
        hypo_str=hypo_s["strength"],
        str_delta=raw_what_if["strength_delta"],
        orig_prob=orig_prob,
        hypo_prob=hypo_prob,
        prob_delta=raw_what_if["probability_delta"],
        att_delta=round(hypo_s["attack"] - orig_s["attack"], 2),
        mid_delta=round(hypo_s["midfield"] - orig_s["midfield"], 2),
        def_delta=round(hypo_s["defense"] - orig_s["defense"], 2),
        bal_delta=round(hypo_s["balance"] - orig_s["balance"], 2),
    )

    ai_text = await call_llm_analyst(prompt, is_what_if=True)
    source = "llm"
    if not isinstance(ai_text, str) or not ai_text.strip():
        ai_text = generate_heuristic_what_if_analysis(raw_what_if)
        source = "heuristic_engine"

    raw_what_if["analysis_text"] = ai_text
    raw_what_if["source"] = source

    return WhatIfResponse(
        results=WhatIfComparison(**raw_what_if),
        ai_analysis=ai_text,
    )
