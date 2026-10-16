import pytest
from app.engine.player_tools import load_players, get_player, get_player_stats
from app.engine.team_analyzer import analyze_team
from app.engine.team_comparator import compare_teams
from app.engine.probability import calculate_win_probability
from app.engine.what_if_engine import simulate_what_if
from app.models.game import GameState, Team

@pytest.fixture(autouse=True)
def init_players():
    load_players()

def test_dataset_loaded_and_valid():
    players = load_players()
    assert len(players) >= 30
    for pid, p in players.items():
        assert 0 <= p.attack <= 100
        assert 0 <= p.midfield <= 100
        assert 0 <= p.defense <= 100
        assert 0 <= p.overall <= 100
        assert p.position in ("GK", "DEF", "MID", "FWD")

def test_player_lookup():
    p = get_player("P001")
    assert p.id == "P001"
    assert p.name == "Thibaut Courtois"
    assert p.position == "GK"

    with pytest.raises(ValueError, match="Unknown player"):
        get_player("P999")

def test_team_analyzer_validations():
    # Empty team
    with pytest.raises(ValueError, match="Team is empty"):
        analyze_team([])

    # Exceed five players
    with pytest.raises(ValueError, match="cannot exceed five players"):
        analyze_team(["P001", "P006", "P014", "P023", "P024", "P025"])

    # Duplicate players
    with pytest.raises(ValueError, match="Duplicate players are not allowed"):
        analyze_team(["P001", "P006", "P006", "P014", "P023"])

def test_team_analyzer_ratings_bounds():
    sample_team = ["P001", "P006", "P014", "P023", "P024"]
    stats = analyze_team(sample_team)
    
    assert 0 <= stats["attack"] <= 100
    assert 0 <= stats["midfield"] <= 100
    assert 0 <= stats["defense"] <= 100
    assert 0 <= stats["overall"] <= 100
    assert 0 <= stats["balance"] <= 100
    assert 0 <= stats["strength"] <= 100
    assert stats["player_count"] == 5

def test_probability_calculation():
    stats_a = {"strength": 88.0}
    stats_b = {"strength": 76.0}
    probs = calculate_win_probability(stats_a, stats_b)

    # Probabilities must sum to 100
    assert round(probs["team_a_win"] + probs["team_b_win"], 2) == 100.00
    # Team A has higher strength so P(A) > P(B)
    assert probs["team_a_win"] > probs["team_b_win"]
    assert probs["team_a_win"] > 50.0

def test_what_if_isolation():
    game = GameState(
        game_id="test_game",
        teams={
            "A": Team(team_id="A", name="Team A", player_ids=["P001", "P006", "P014", "P023", "P024"]),
            "B": Team(team_id="B", name="Team B", player_ids=["P002", "P007", "P015", "P025", "P026"]),
        },
        available_player_ids=["P003", "P004", "P027", "P028"],
        current_turn="A",
        status="completed"
    )

    # Capture deep copy of initial state
    initial_a_ids = list(game.teams["A"].player_ids)
    initial_b_ids = list(game.teams["B"].player_ids)

    # Simulate swapping P024 (Haaland) with P027 (Vinicius Jr)
    result = simulate_what_if(
        game=game,
        team_id="A",
        player_out="P024",
        player_in="P027"
    )

    # Assert results are produced
    assert result["target_team_id"] == "A"
    assert result["player_out"]["id"] == "P024"
    assert result["player_in"]["id"] == "P027"

    # CRITICAL: Verify game state was NOT mutated
    assert game.teams["A"].player_ids == initial_a_ids
    assert game.teams["B"].player_ids == initial_b_ids
