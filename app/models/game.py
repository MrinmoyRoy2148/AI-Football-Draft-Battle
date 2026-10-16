from typing import Literal, Optional
from pydantic import BaseModel, Field

Turn = Literal["A", "B"]
GameStatus = Literal["drafting", "completed"]

class Team(BaseModel):
    team_id: Literal["A", "B"]
    name: str = ""
    player_ids: list[str] = Field(default_factory=list, max_length=5)
    formation: str = "1-1-1-2"

    def is_full(self) -> bool:
        return len(self.player_ids) == 5

class GameState(BaseModel):
    game_id: str
    teams: dict[str, Team]
    available_player_ids: list[str]
    current_turn: Turn = "A"
    draft_round: int = 1
    status: GameStatus = "drafting"
    last_drafted_player_id: Optional[str] = None
    last_drafted_by: Optional[str] = None

class CreateGameRequest(BaseModel):
    game_id: Optional[str] = None
    team_a_name: Optional[str] = "Team Alpha"
    team_b_name: Optional[str] = "Team Beta"
    formation_a: Optional[str] = "1-1-1-2"
    formation_b: Optional[str] = "1-1-1-2"

class DraftRequest(BaseModel):
    game_id: str
    player_id: str

class WhatIfRequest(BaseModel):
    game_id: str
    team_id: Literal["A", "B"]
    player_out: str
    player_in: str
    formation: Optional[str] = None

class AnalyzeRequest(BaseModel):
    game_id: str
