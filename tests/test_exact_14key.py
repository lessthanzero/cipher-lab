"""Unit tests for Exact 14-Key Double Transposition Sweep."""

from projects.dagapeyeff.exact_14key_sweep import (
    apply_generalized_double_transposition,
    EXACT_14_CANDIDATE_KEYS,
)
from projects.dagapeyeff.kerckhoffs_defect import get_standard_key_order


def test_candidate_keys_properties():
    assert "ORDNANCESURVEY" in EXACT_14_CANDIDATE_KEYS
    assert len("ORDNANCESURVEY") == 14
    ranks = get_standard_key_order("ORDNANCESURVEY")
    assert len(ranks) == 14
    assert sorted(ranks) == list(range(14))


def test_generalized_double_transposition_roundtrip():
    pairs = [f"{r}{c}" for r in range(5) for c in range(5)][:16]  # 4x4 grid = 16 pairs
    col_order = [2, 0, 3, 1]
    row_order = [1, 3, 0, 2]

    # Transposition preserves all elements as a permutation
    t_pairs = apply_generalized_double_transposition(
        pairs,
        col_order=col_order,
        row_order=row_order,
        mode="kerckhoffs_decryption",
        order="col_then_row",
    )
    assert len(t_pairs) == 16
    assert sorted(t_pairs) == sorted(pairs)

    # Test reverse order row_then_col
    t_pairs_rc = apply_generalized_double_transposition(
        pairs,
        col_order=col_order,
        row_order=row_order,
        mode="standard_encryption",
        order="row_then_col",
    )
    assert len(t_pairs_rc) == 16
    assert sorted(t_pairs_rc) == sorted(pairs)
