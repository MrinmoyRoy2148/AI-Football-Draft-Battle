from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Position = Literal["GK", "DEF", "MID", "FWD"]

class Player(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    position: Position
    attack: int = Field(ge=0, le=100, description="Attack rating 0-100")
    midfield: int = Field(ge=0, le=100, description="Midfield rating 0-100")
    defense: int = Field(ge=0, le=100, description="Defense rating 0-100")
    overall: int = Field(ge=0, le=100, description="Overall rating 0-100")
