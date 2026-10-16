import pytest
from app.services.game_state import create_game, get_game, clear_all_games
from app.services.draft_service import process_draft_pick

@pytest.fixture(autouse=True)
def clean_storage():
    clear_all_games()

def test_full_alternating_draft_flow():
    game = create_game("draft_test_1", team_a_name="Reds", team_b_name="Blues")
    assert game.status == "drafting"
    assert game.current_turn == "A"
    assert game.draft_round == 1

    # 10 picks alternating
    # Team A picks P001 (GK)
    game = process_draft_pick("draft_test_1", "P001")
    assert "P001" in game.teams["A"].player_ids
    assert "P001" not in game.available_player_ids
    assert game.current_turn == "B"
    assert game.draft_round == 2

    # Team B picks P002 (GK)
    game = process_draft_pick("draft_test_1", "P002")
    assert "P002" in game.teams["B"].player_ids
    assert game.current_turn == "A"

    # Turn 3: A picks P006
    game = process_draft_pick("draft_test_1", "P006")
    # Turn 4: B picks P007
    game = process_draft_pick("draft_test_1", "P007")
    # Turn 5: A picks P014
    game = process_draft_pick("draft_test_1", "P014")
    # Turn 6: B picks P015
    game = process_draft_pick("draft_test_1", "P015")
    # Turn 7: A picks P023
    game = process_draft_pick("draft_test_1", "P023")
    # Turn 8: B picks P024
    game = process_draft_pick("draft_test_1", "P024")
    # Turn 9: A picks P025 (Team A now has 5 players)
    game = process_draft_pick("draft_test_1", "P025")
    assert len(game.teams["A"].player_ids) == 5
    assert len(game.teams["B"].player_ids) == 4
    assert game.status == "drafting"
    assert game.current_turn == "B"

    # Turn 10: B picks P026 (Team B now has 5 players)
    game = process_draft_pick("draft_test_1", "P026")
    assert len(game.teams["B"].player_ids) == 5
    assert game.status == "completed"

def test_cannot_pick_already_drafted_player():
    create_game("draft_test_2")
    process_draft_pick("draft_test_2", "P001")

    # Team B tries to pick P001 again
    with pytest.raises(ValueError, match="no longer available"):
        process_draft_pick("draft_test_2", "P001")

def test_cannot_pick_after_draft_complete():
    game = create_game("draft_test_3")
    picks = ["P001", "P002", "P006", "P007", "P014", "P015", "P023", "P024", "P025", "P026"]
    for pid in picks:
        game = process_draft_pick("draft_test_3", pid)

    assert game.status == "completed"

    with pytest.raises(ValueError, match="already completed"):
        process_draft_pick("draft_test_3", "P027")
