SYSTEM_PROMPT = """
You are the official AI Football Game Analyst Agent for the CSE 3202 AI Sessional project.
Your purpose is to provide intelligent, decision-oriented tactical commentary for a 5-player football match draft.

GUIDELINES & CONSTRAINTS:
1. Ground your analysis strictly on the deterministic numerical calculations provided by the Python engine.
2. DO NOT invent ratings, change statistics, or alter calculated probabilities.
3. Highlight each team's tactical strengths, vulnerabilities, key player matchups, and midfield control.
4. Acknowledge when the matchup is extremely close or if one team holds a decisive edge.
5. In What-If scenarios, clearly explain the tactical trade-offs and deltas (e.g., gain in attack at the cost of defensive stability).
6. Maintain an engaging, professional, broadcast-analyst tone.
"""

MATCH_ANALYSIS_USER_TEMPLATE = """
Game ID: {game_id}
Team A: {team_a_name} (Formation: {formation_a})
Roster A: {team_a_roster}
Stats A: Attack={a_att}, Midfield={a_mid}, Defense={a_def}, Overall={a_ovr}, Balance={a_bal}, Strength={a_str}

Team B: {team_b_name} (Formation: {formation_b})
Roster B: {team_b_roster}
Stats B: Attack={b_att}, Midfield={b_mid}, Defense={b_def}, Overall={b_ovr}, Balance={b_bal}, Strength={b_str}

Head-to-Head Deltas (Team A - Team B):
Attack Diff: {att_diff}, Midfield Diff: {mid_diff}, Defense Diff: {def_diff}, Balance Diff: {bal_diff}, Strength Diff: {str_diff}

Calculated Win Probability:
{team_a_name}: {prob_a}%
{team_b_name}: {prob_b}%
Calculated Leader: {leader}

Please analyze this matchup and provide your response as a valid JSON object with the following fields:
- summary: A concise 2-sentence executive summary of the encounter.
- team_a_assessment: Tactical strengths and weaknesses of Team A.
- team_b_assessment: Tactical strengths and weaknesses of Team B.
- key_matchups: Specific clash areas (e.g., attack vs defense, midfield superiority).
- tactical_verdict: Decisive factors that lead to the predicted winning probability.
"""

WHAT_IF_USER_TEMPLATE = """
Tactical Simulation Context:
Target Team: {team_name} (Team {team_id})
Substituted Out: {player_out_name} ({player_out_pos}) - Att: {out_att}, Mid: {out_mid}, Def: {out_def}, Ovr: {out_ovr}
Substituted In: {player_in_name} ({player_in_pos}) - Att: {in_att}, Mid: {in_mid}, Def: {in_def}, Ovr: {in_ovr}
Formation: {formation}

Numerical Changes for {team_name}:
Original Strength: {orig_str} -> Hypothetical Strength: {hypo_str} (Delta: {str_delta:+0.2f})
Original Win Probability: {orig_prob}% -> Hypothetical Win Probability: {hypo_prob}% (Delta: {prob_delta:+0.2f}%)
Stat Changes: Attack {att_delta:+0.2f}, Midfield {mid_delta:+0.2f}, Defense {def_delta:+0.2f}, Balance {bal_delta:+0.2f}

Provide a concise, insightful tactical evaluation of whether this substitution is strategically beneficial for {team_name}.
Explain how the swap affects the team's balance, counter-attacking ability or defensive solidity against their opponent.
"""
