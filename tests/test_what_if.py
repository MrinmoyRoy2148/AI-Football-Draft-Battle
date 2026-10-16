import pytest
from app.models.game import GameState, Team
from app.engine.what_if_engine import simulate_what_if
from app.engine.player_tools import load_players

@pytest.fixture(autouse=True)
def init_data():
    load_players()

def test_what_if_validation_and_state_preservation():
    # Setup completed game state
    game = GameState(
        game_id="whatif_test_session",
        teams={
            "A": Team(team_id="A", name="Team A", player_ids=["P001", "P006", "P014", "P023", "P024"], formation="1-1-1-2"),
            "B": Team(team_id="B", name="Team B", player_ids=["P002", "P007", "P015", "P025", "P026"], formation="1-1-1-2"),
        },
        available_player_ids=["P003", "P008", "P016", "P027", "P028"],
        current_turn="A",
        status="completed"
    )

    # 1. Invalid outgoing player (not on team A)
    with pytest.raises(ValueError, match="not currently on Team A"):
        simulate_what_if(game, "A", player_out="P002", player_in="P027")

    # 2. Invalid incoming player (already on Team B)
    with pytest.raises(ValueError, match="currently on opponent Team B"):
        simulate_what_if(game, "A", player_out="P023", player_in="P025")

    # 3. Invalid incoming player (already on Team A)
    with pytest.raises(ValueError, match="already on Team A"):
        simulate_what_if(game, "A", player_out="P023", player_in="P001")

    # 4. Valid substitution: swap P024 (Haaland) for P027 (Vinicius)
    res = simulate_what_if(game, "A", player_out="P024", player_in="P027")

    assert res["target_team_id"] == "A"
    assert res["player_out"]["id"] == "P024"
    assert res["player_in"]["id"] == "P027"

    # Verify probability delta is computed
    assert "probability_delta" in res
    assert "strength_delta" in res

    # 5. ABSOLUTE PROOF that the actual game was NEVER mutated
    assert game.teams["A"].player_ids == ["P001", "P006", "P014", "P023", "P024"]
    assert game.teams["B"].player_ids == ["P002", "P007", "P015", "P025", "P026"]
    assert "P027" in game.available_player_ids
