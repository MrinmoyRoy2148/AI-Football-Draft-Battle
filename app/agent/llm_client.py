import json
import logging
from typing import Optional
from app.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL
from app.agent.prompts import SYSTEM_PROMPT, MATCH_ANALYSIS_USER_TEMPLATE, WHAT_IF_USER_TEMPLATE
from app.models.analysis import AIAnalysis

logger = logging.getLogger("football_agent")

def generate_heuristic_match_analysis(
    comparison: dict,
    probabilities: dict,
    team_a_name: str = "Team Alpha",
    team_b_name: str = "Team Beta"
) -> AIAnalysis:
    """
    Intelligent deterministic football analyst fallback.
    Produces reasoned, mathematically consistent tactical feedback when no LLM key is configured.
    """
    stats_a = comparison["team_a_stats"]
    stats_b = comparison["team_b_stats"]
    p_a = probabilities["team_a_win"]
    p_b = probabilities["team_b_win"]

    leader = comparison["leader"]
    str_diff = comparison["strength_diff"]
    att_diff = comparison["attack_diff"]
    mid_diff = comparison["midfield_diff"]
    def_diff = comparison["defense_diff"]
    bal_diff = comparison["balance_diff"]

    # Executive Summary
    if abs(p_a - p_b) < 6.0:
        summary = (
            f"A razor-thin matchup between {team_a_name} ({p_a}%) and {team_b_name} ({p_b}%). "
            f"Both squads demonstrate remarkable parity, with tactical execution likely determining the outcome."
        )
    elif p_a > p_b:
        summary = (
            f"{team_a_name} enters this clash as the calculated favorite with a {p_a}% win expectation against "
            f"{team_b_name} ({p_b}%), driven by superior aggregate strength (+{str_diff:.1f})."
        )
    else:
        summary = (
            f"{team_b_name} holds the statistical initiative at {p_b}% win probability over "
            f"{team_a_name} ({p_a}%), establishing a {abs(str_diff):.1f} composite strength advantage."
        )

    # Team A Assessment
    strengths_a = []
    weaknesses_a = []
    if stats_a["attack"] >= 88:
        strengths_a.append("devastating offensive firepower")
    elif stats_a["attack"] < 75:
        weaknesses_a.append("modest conversion rate in the final third")

    if stats_a["midfield"] >= 88:
        strengths_a.append("exceptional midfield transition and tempo control")
    elif stats_a["midfield"] < 75:
        weaknesses_a.append("potential vulnerability in ball retention")

    if stats_a["defense"] >= 88:
        strengths_a.append("rock-solid backline organization")
    elif stats_a["defense"] < 75:
        weaknesses_a.append("fragility under aggressive wing penetration")

    if stats_a["balance"] >= 85:
        strengths_a.append(f"outstanding tactical harmony (balance index {stats_a['balance']})")
    else:
        weaknesses_a.append(f"uneven distribution across phases (balance index {stats_a['balance']})")

    str_a_text = ", ".join(strengths_a) if strengths_a else "steady all-round consistency"
    weak_a_text = ", ".join(weaknesses_a) if weaknesses_a else "no glaring structural weaknesses"
    team_a_assessment = f"{team_a_name} displays {str_a_text}, though they must manage {weak_a_text}."

    # Team B Assessment
    strengths_b = []
    weaknesses_b = []
    if stats_b["attack"] >= 88:
        strengths_b.append("lethal offensive threat")
    elif stats_b["attack"] < 75:
        weaknesses_b.append("limited penetration against deep blocks")

    if stats_b["midfield"] >= 88:
        strengths_b.append("authoritative playmaking in central areas")
    elif stats_b["midfield"] < 75:
        weaknesses_b.append("susceptibility to counter-pressing in midfield")

    if stats_b["defense"] >= 88:
        strengths_b.append("resolute defensive solidity")
    elif stats_b["defense"] < 75:
        weaknesses_b.append("occasional defensive gaps on fast transitions")

    if stats_b["balance"] >= 85:
        strengths_b.append(f"high tactical synergy (balance index {stats_b['balance']})")
    else:
        weaknesses_b.append(f"disproportionate phase reliance (balance index {stats_b['balance']})")

    str_b_text = ", ".join(strengths_b) if strengths_b else "disciplined foundational attributes"
    weak_b_text = ", ".join(weaknesses_b) if weaknesses_b else "tight operational margins"
    team_b_assessment = f"{team_b_name} boasts {str_b_text}, but face challenges with {weak_b_text}."

    # Key Matchups
    matchup_notes = []
    if abs(mid_diff) >= 4.0:
        dominant_mid = team_a_name if mid_diff > 0 else team_b_name
        matchup_notes.append(f"Midfield supremacy tilts towards {dominant_mid} (delta: {abs(mid_diff):+.1f}), crucial for dictating possession.")
    else:
        matchup_notes.append("The central midfield encounter is evenly contested, turning second-ball recoveries into vital transition triggers.")

    if stats_a["attack"] > stats_b["defense"] + 3.0:
        matchup_notes.append(f"{team_a_name}'s attacking line ({stats_a['attack']}) poses a severe examination for {team_b_name}'s defense ({stats_b['defense']}).")
    elif stats_b["attack"] > stats_a["defense"] + 3.0:
        matchup_notes.append(f"{team_b_name}'s forward unit ({stats_b['attack']}) holds an offensive advantage over {team_a_name}'s defensive core ({stats_a['defense']}).")
    else:
        matchup_notes.append("Both defensive cores match up well against the opposing strike forces, predicting a tight physical contest.")

    key_matchups = " ".join(matchup_notes)

    # Tactical Verdict
    if leader != "Tied":
        tactical_verdict = (
            f"{leader} claims the edge through superior overall balance ({bal_diff:+.1f}) and collective strength ({str_diff:+.1f}). "
            f"The deterministic logistic model projects a {max(p_a, p_b)}% win probability for {leader}."
        )
    else:
        tactical_verdict = (
            "Neither squad holds a decisive statistical edge. "
            "Individual moments of technical brilliance or set-piece execution are expected to decide the victor."
        )

    return AIAnalysis(
        summary=summary,
        team_a_assessment=team_a_assessment,
        team_b_assessment=team_b_assessment,
        key_matchups=key_matchups,
        tactical_verdict=tactical_verdict,
        source="heuristic_engine"
    )

def generate_heuristic_what_if_analysis(what_if_data: dict) -> str:
    """Intelligent fallback for What-If scenario tactical explanations."""
    p_out = what_if_data["player_out"]
    p_in = what_if_data["player_in"]
    target_id = what_if_data["target_team_id"]
    team_name = what_if_data["original_stats"]["team_name"] or f"Team {target_id}"

    str_delta = what_if_data["strength_delta"]
    prob_delta = what_if_data["probability_delta"]

    orig_att = what_if_data["original_stats"]["attack"]
    hypo_att = what_if_data["hypothetical_stats"]["attack"]
    orig_mid = what_if_data["original_stats"]["midfield"]
    hypo_mid = what_if_data["hypothetical_stats"]["midfield"]
    orig_def = what_if_data["original_stats"]["defense"]
    hypo_def = what_if_data["hypothetical_stats"]["defense"]
    orig_bal = what_if_data["original_stats"]["balance"]
    hypo_bal = what_if_data["hypothetical_stats"]["balance"]

    lines = []
    lines.append(
        f"Substituting {p_out['name']} ({p_out['position']}) for {p_in['name']} ({p_in['position']}) "
        f"shifts {team_name}'s composite strength by {str_delta:+.2f} points, "
        f"resulting in a {prob_delta:+.2f}% delta in winning probability."
    )

    if prob_delta > 1.0:
        lines.append(
            f"This represents an advantageous tactical adjustment. "
            f"{p_in['name']}'s introduction elevates {team_name}'s ratings "
            f"(Attack: {hypo_att - orig_att:+.1f}, Midfield: {hypo_mid - orig_mid:+.1f}, Defense: {hypo_def - orig_def:+.1f})."
        )
    elif prob_delta < -1.0:
        lines.append(
            f"This modification introduces tactical compromise. While altering the squad profile, "
            f"the team suffers a {abs(prob_delta):.1f}% reduction in expected win rate, primarily due to "
            f"disruption in team balance (Balance delta: {hypo_bal - orig_bal:+.1f})."
        )
    else:
        lines.append(
            f"The substitution has a neutral overall effect on the team's outcome probability ({prob_delta:+.2f}%), "
            f"reallocating attribute strengths without fundamentally altering squad superiority."
        )

    return " ".join(lines)

async def call_llm_analyst(user_prompt: str, is_what_if: bool = False) -> Optional[dict | str]:
    """
    Attempts to query the OpenAI LLM API if key is present.
    Returns parsed dictionary / string or None if unconfigured / failed.
    """
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import AsyncOpenAI
        client_kwargs = {"api_key": OPENAI_API_KEY}
        if OPENAI_BASE_URL:
            client_kwargs["base_url"] = OPENAI_BASE_URL

        client = AsyncOpenAI(**client_kwargs)

        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if not is_what_if else None,
            temperature=0.4,
            timeout=15.0
        )

        content = response.choices[0].message.content
        if is_what_if:
            return content.strip()
        else:
            return json.loads(content)
    except Exception as e:
        logger.warning(f"LLM API call failed or timed out: {e}. Falling back to deterministic analyst.")
        return None
