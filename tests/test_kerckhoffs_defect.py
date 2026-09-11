"""Unit tests for Kerckhoffs defect models, Shuvalof ranking errors, and book keywords."""

from __future__ import annotations

import pytest

from projects.dagapeyeff.kerckhoffs_defect import (
    BOOK_KEYWORDS,
    get_historical_shuvalof_ranks,
    get_standard_key_order,
    apply_columnar_transposition_direction,
    apply_double_kerckhoffs_transposition,
)
from projects.dagapeyeff.clerical_repair import (
    apply_row0_correction,
    strip_column_14_margin,
    strip_row_14_margin,
    get_all_row0_variants,
)
from projects.dagapeyeff.corpus import get_digit_pairs


def test_book_keywords_catalog() -> None:
    """Verify presence of documented historical keywords."""
    assert "SCHUVALOF_BOOK_TEXT" in BOOK_KEYWORDS
    assert "ORDNANCE_SURVEY" in BOOK_KEYWORDS
    assert "DAGAPEYEFF" in BOOK_KEYWORDS
    assert len(BOOK_KEYWORDS) >= 12


def test_shuvalof_ranking_discrepancy() -> None:
    """Verify the exact ranking discrepancy between Kerckhoffs and D'Agapeyeff."""
    ranks = get_historical_shuvalof_ranks()
    
    err_rank = ranks["dagapeyeff_erroneous_schuvalof"]
    corr_rank = ranks["mathematically_correct_schuvalof"]
    
    # In D'Agapeyeff's erroneous ranking, F received rank 8 (0-indexed highest)
    assert err_rank[-1] == 8
    # In mathematically correct ranking of SCHUVALOF, F receives rank 2
    assert corr_rank[-1] == 2
    assert err_rank != corr_rank


def test_kerckhoffs_direction_inversion() -> None:
    """Verify that decryption and encryption directions produce different outputs (not self-inverse)."""
    pairs = get_digit_pairs()[:28]  # 2 rows of 14
    # Non-involution cyclic shift: [1, 2, 3, ... 13, 0]
    key = list(range(1, 14)) + [0]
    
    enc = apply_columnar_transposition_direction(pairs, key, mode="standard_encryption")
    dec = apply_columnar_transposition_direction(pairs, key, mode="kerckhoffs_decryption")
    
    assert len(enc) == 28
    assert len(dec) == 28
    # Proves the operation is not self-inverse
    assert enc != dec


def test_row0_and_column14_repairs() -> None:
    """Verify Row 0 substitution and Column 14 stripping."""
    pairs = get_digit_pairs()
    assert pairs[97] == "04"
    
    corrected = apply_row0_correction(pairs, replacement="74")
    assert corrected[97] == "74"
    assert "04" not in corrected  # Row 0 now has zero occurrences!
    
    stripped_col = strip_column_14_margin(pairs, width=14)
    assert len(stripped_col) == 182  # 14 x 13
    assert "04" not in stripped_col  # Pair 97 was in column 14, now removed!
    
    variants = get_all_row0_variants(pairs)
    assert len(variants) >= 8
    assert "pos97_to_74" in variants
    assert "col14_stripped_182" in variants
