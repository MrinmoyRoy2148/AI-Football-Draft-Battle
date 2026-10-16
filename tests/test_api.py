import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.game_state import clear_all_games

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_state():
    clear_all_games()

def test_health_and_players_endpoints():
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "AI FOOTBALL BATTLE" in res_index.text

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_players = client.get("/api/players")
    assert res_players.status_code == 200
    players = res_players.json()
    assert len(players) >= 30
    assert any(p["id"] == "P001" for p in players)

def test_game_creation_and_incomplete_analysis():
    # Create game
    res_create = client.post("/api/game/create", json={"team_a_name": "Galacticos", "team_b_name": "Legends"})
    assert res_create.status_code == 200
    game_data = res_create.json()
    game_id = game_data["game_id"]
    assert game_data["teams"]["A"]["name"] == "Galacticos"
    assert game_data["teams"]["B"]["name"] == "Legends"

    # Analyze should fail because teams are empty
    res_analyze = client.post("/api/analyze", json={"game_id": game_id})
    assert res_analyze.status_code == 400
    assert "must draft exactly 5 players" in res_analyze.json()["detail"]

def test_full_draft_and_analysis_and_what_if_flow():
    # 1. Create game
    res_create = client.post("/api/game/create", json={"team_a_name": "Red Devils", "team_b_name": "Sky Blues"})
    game_id = res_create.json()["game_id"]

    # 2. Draft 10 players
    draft_picks = [
        "P001", "P002",  # Courtois (A), Alisson (B)
        "P006", "P007",  # Van Dijk (A), Dias (B)
        "P014", "P015",  # De Bruyne (A), Bellingham (B)
        "P023", "P024",  # Mbappe (A), Haaland (B)
        "P025", "P026",  # Messi (A), Ronaldo (B)
    ]

    for pid in draft_picks:
        res_draft = client.post("/api/draft", json={"game_id": game_id, "player_id": pid})
        assert res_draft.status_code == 200

    # Game should now be completed
    game_state = client.get(f"/api/game/{game_id}").json()
    assert game_state["status"] == "completed"
    assert len(game_state["teams"]["A"]["player_ids"]) == 5
    assert len(game_state["teams"]["B"]["player_ids"]) == 5

    # 3. Analyze complete teams
    res_analyze = client.post("/api/analyze", json={"game_id": game_id})
    assert res_analyze.status_code == 200
    analysis = res_analyze.json()
    assert "comparison" in analysis
    assert "probabilities" in analysis
    assert "ai_analysis" in analysis

    probs = analysis["probabilities"]
    assert round(probs["team_a_win"] + probs["team_b_win"], 2) == 100.00
    assert len(analysis["ai_analysis"]["summary"]) > 0
    assert len(analysis["ai_analysis"]["tactical_verdict"]) > 0

    # 4. Perform What-If simulation
    # Swap P025 (Messi) on Team A for P027 (Vinicius Jr) which is an undrafted player
    res_what_if = client.post("/api/what-if", json={
        "game_id": game_id,
        "team_id": "A",
        "player_out": "P025",
        "player_in": "P027"
    })
    assert res_what_if.status_code == 200
    what_if = res_what_if.json()
    assert "results" in what_if
    assert "ai_analysis" in what_if
    assert what_if["results"]["player_out"]["id"] == "P025"
    assert what_if["results"]["player_in"]["id"] == "P027"
    assert "delta" in str(what_if["ai_analysis"]).lower() or len(what_if["ai_analysis"]) > 20

    # 5. Verify actual game state remains unchanged
    game_state_after = client.get(f"/api/game/{game_id}").json()
    assert "P025" in game_state_after["teams"]["A"]["player_ids"]
    assert "P027" not in game_state_after["teams"]["A"]["player_ids"]
