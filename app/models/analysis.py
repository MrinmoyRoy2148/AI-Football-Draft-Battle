from typing import Optional
from pydantic import BaseModel, Field
from app.models.player import Player

class TeamStats(BaseModel):
    team_id: str
    team_name: str = ""
    formation: str
    player_count: int
    attack: float = Field(description="Normalized team attack rating (0-100)")
    midfield: float = Field(description="Normalized team midfield rating (0-100)")
    defense: float = Field(description="Normalized team defense rating (0-100)")
    overall: float = Field(description="Average team overall rating (0-100)")
    balance: float = Field(description="Team balance rating (0-100)")
    strength: float = Field(description="Composite team strength rating")
    players: list[Player] = Field(default_factory=list)

class ProbabilityResult(BaseModel):
    team_a_win: float = Field(description="Win probability percentage for Team A (0-100)")
    team_b_win: float = Field(description="Win probability percentage for Team B (0-100)")

class TeamComparison(BaseModel):
    team_a_stats: TeamStats
    team_b_stats: TeamStats
    attack_diff: float = Field(description="Team A attack minus Team B attack")
    midfield_diff: float = Field(description="Team A midfield minus Team B midfield")
    defense_diff: float = Field(description="Team A defense minus Team B defense")
    overall_diff: float = Field(description="Team A overall minus Team B overall")
    balance_diff: float = Field(description="Team A balance minus Team B balance")
    strength_diff: float = Field(description="Team A strength minus Team B strength")
    leader: str = Field(description="'Team A', 'Team B', or 'Tied'")

class AIAnalysis(BaseModel):
    summary: str
    team_a_assessment: str
    team_b_assessment: str
    key_matchups: str
    tactical_verdict: str
    source: str = "llm"  # "llm" or "heuristic_engine"

class AnalysisResponse(BaseModel):
    comparison: TeamComparison
    probabilities: ProbabilityResult
    ai_analysis: AIAnalysis

class WhatIfComparison(BaseModel):
    target_team_id: str
    player_out: Player
    player_in: Player
    original_stats: TeamStats
    hypothetical_stats: TeamStats
    original_probabilities: ProbabilityResult
    hypothetical_probabilities: ProbabilityResult
    strength_delta: float
    probability_delta: float
    analysis_text: Optional[str] = None
    source: str = "llm"

class WhatIfResponse(BaseModel):
    results: WhatIfComparison
    ai_analysis: str
