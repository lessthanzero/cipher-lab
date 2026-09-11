from projects.dagapeyeff.corpus import get_digit_pairs, get_stripped_14x13_pairs
from projects.dagapeyeff.kerckhoffs import KerckhoffsEngine


def test_kerckhoffs_decode():
    engine = KerckhoffsEngine()
    # Test decoding known pair stream: row 6-0 -> 1-5, col 1-5
    # (6, 1) -> (1, 1) -> A, (6, 2) -> (1, 2) -> B
    pairs = ["61", "62", "63", "64", "65"]
    text = engine.decode_pair_stream(pairs)
    assert text == "ABCDE"

def test_kerckhoffs_double_transposition():
    engine = KerckhoffsEngine()
    pairs = get_digit_pairs()
    assert len(pairs) == 196
    
    row_key = list(range(14))
    col_key = list(range(14))
    
    # Test identity transposition
    res = engine.apply_reversed_kerckhoffs_double_transposition(pairs, row_key, col_key, width=14)
    assert len(res) == 196

def test_position_97_correction():
    engine = KerckhoffsEngine()
    pairs = get_digit_pairs()
    corrected = engine.apply_position_97_correction(pairs, replacement="75")
    assert corrected[97] == "75"

def test_stripped_14x13_grid():
    stripped = get_stripped_14x13_pairs()
    assert len(stripped) == 182  # 14 x 13
