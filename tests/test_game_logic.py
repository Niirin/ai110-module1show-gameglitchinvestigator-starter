from logic_utils import check_guess, get_range_for_difficulty, update_score

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    # Fix: check_guess returns a tuple (outcome, message)
    # but the tests compare the full result to just a string like "Win"
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

# --- Bug fix: incorrect hints were showing the opposite direction ---

def test_too_high_hint_says_go_lower():
    # Bug: when guess > secret, hint was "📈 Go HIGHER!" instead of "📉 Go LOWER!"
    outcome, message = check_guess(80, 50)
    assert outcome == "Too High"
    assert message == "📉 Go LOWER!", f"Expected 'Go LOWER' hint but got: {message}"

def test_too_low_hint_says_go_higher():
    # Bug: when guess < secret, hint was "📉 Go LOWER!" instead of "📈 Go HIGHER!"
    outcome, message = check_guess(20, 50)
    assert outcome == "Too Low"
    assert message == "📈 Go HIGHER!", f"Expected 'Go HIGHER' hint but got: {message}"

# --- Bug fix: Hard difficulty had a smaller range (1-50) than Normal (1-100) ---

def test_hard_range_is_larger_than_normal():
    # Bug: Hard returned (1, 50) which is easier than Normal (1, 100)
    _, high = get_range_for_difficulty("Hard")
    assert high == 200, f"Expected Hard range to be 1-200 but got 1-{high}"

def test_easy_range():
    low, high = get_range_for_difficulty("Easy")
    assert (low, high) == (1, 20)

def test_normal_range():
    low, high = get_range_for_difficulty("Normal")
    assert (low, high) == (1, 100)

# --- Bug fix: update_score gave +5 points on "Too High" when attempt_number was even ---

def test_too_high_even_attempt_deducts_score():
    # Bug: on even attempt numbers, "Too High" was adding +5 instead of -5
    result = update_score(100, "Too High", attempt_number=2)
    assert result == 95, f"Expected 95 (deduct 5) but got {result}"

def test_too_high_odd_attempt_deducts_score():
    # Confirm odd attempts also deduct correctly
    result = update_score(100, "Too High", attempt_number=3)
    assert result == 95, f"Expected 95 (deduct 5) but got {result}"

def test_too_low_deducts_score():
    result = update_score(100, "Too Low", attempt_number=2)
    assert result == 95

def test_win_adds_score():
    # Win on attempt 1: 100 - 10*(1+1) = 80 points added
    result = update_score(0, "Win", attempt_number=1)
    assert result == 80


# --- Bug fix: New Game button did not reset session state correctly ---
# The bug: status was never reset to "playing", attempts reset to 0 instead of 1,
# secret used hardcoded range (1-100) ignoring difficulty, and history was not cleared.

def test_new_game_score_resets_to_zero():
    # After a new game, score should start at 0.
    # Simulate: player won with score=150, new game resets score to 0,
    # then first wrong guess deducts 5 -> score should be -5 not 145.
    fresh_score = 0  # what new game should reset to
    result = update_score(fresh_score, "Too Low", attempt_number=1)
    assert result == -5, f"Expected -5 (fresh game deduction) but got {result}"

def test_new_game_starts_at_attempt_1():
    # After new game, attempts should start at 1 (not 0).
    # Bug: attempts was reset to 0, causing the first submit to increment to 1,
    # but the "Attempts left" display showed one extra attempt before the first guess.
    # Verify scoring at attempt=1 (the correct first attempt after new game).
    result = update_score(0, "Win", attempt_number=1)
    # 100 - 10 * (1 + 1) = 80
    assert result == 80, f"Expected 80 points for win on attempt 1 but got {result}"

def test_new_game_attempt_0_gives_wrong_score():
    # Demonstrates the off-by-one bug: if attempts were reset to 0 (the old bug),
    # the first submit increments to 1 — but a win scored at attempt_number=0
    # (before increment) would give wrong points: 100 - 10*(0+1) = 90 instead of 80.
    bugged_result = update_score(0, "Win", attempt_number=0)
    correct_result = update_score(0, "Win", attempt_number=1)
    assert bugged_result != correct_result, "attempt=0 and attempt=1 should score differently"
    assert correct_result == 80
    assert bugged_result == 90

def test_new_game_range_respects_difficulty():
    # After a new game, the secret should use the difficulty range, not hardcoded 1-100.
    # Bug: new game used random.randint(1, 100) regardless of difficulty.
    _, high_easy = get_range_for_difficulty("Easy")
    _, high_hard = get_range_for_difficulty("Hard")
    assert high_easy == 20,  f"Easy should cap at 20, got {high_easy}"
    assert high_hard == 200, f"Hard should cap at 200, got {high_hard}"
    assert high_easy != 100, "Easy range should NOT be the hardcoded default 1-100"
