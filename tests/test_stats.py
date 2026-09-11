import pytest
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_empirical_p_value,
    calculate_index_of_coincidence,
    calculate_shannon_entropy,
    check_unicity_distance,
)


def test_index_of_coincidence():
    # Natural English text (non-pangram) with typical letter repetition
    english_sample = (
        "TOBEORNOTTOBETHATISTHEQUESTIONWHETHERTISNOBLERINTHEMINDTOSUFFER"
        "THESLINGSANDARROWSOFOUTRAGEOUSFORTUNEORTOTAKEARMSAGAINSTASEAOF"
        "TROUBLESANDBYOPPOSINGENDTHEMTODIETOSLEEPNOMORE"
    )
    ic_eng = calculate_index_of_coincidence(english_sample)
    assert 0.055 < ic_eng < 0.085

    # Highly uniform / random text has lower IC
    random_sample = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ic_rand = calculate_index_of_coincidence(random_sample)
    assert ic_rand == 0.0  # All unique characters -> sum(count*(count-1)) == 0

def test_shannon_entropy():
    # Uniform 4-character string
    tokens = ["A", "B", "C", "D"]
    assert calculate_shannon_entropy(tokens) == 2.0
    # Single character
    assert calculate_shannon_entropy(["A"] * 10) == 0.0

def test_unicity_distance():
    # Short text (8 chars) with 26-letter alphabet (key space ~88 bits)
    check = check_unicity_distance(payload_len=8, alphabet_size=26, key_space_bits=88.0)
    assert check.is_underdetermined is True
    assert check.warning is not None
    assert check.unicity_distance_chars == pytest.approx(88.0 / 3.2, 0.1)

    # Long text (500 chars)
    check_long = check_unicity_distance(payload_len=500, alphabet_size=26, key_space_bits=88.0)
    assert check_long.is_underdetermined is False

def test_empirical_p_value():
    observed = 10.0
    null_dist = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    p_val = calculate_empirical_p_value(observed, null_dist, higher_is_better=True)
    # observed is strictly greater than all null scores -> 1 / (9 + 1) = 0.1
    assert p_val == pytest.approx(0.1, 0.01)

def test_quadgram_scorer():
    scorer = QuadgramScorer()
    # Coherent English quadgram string
    eng_score = scorer.score("THISISANENGLISHSTRING")
    gibberish_score = scorer.score("QXJZVKWPZFXJ")
    assert eng_score > gibberish_score
