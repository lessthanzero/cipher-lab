"""Unit tests for Incipit Crib Constraint Engine."""

from projects.dagapeyeff.incipit_crib_solver import (
    CANDIDATE_INCIPITS,
    build_crib_constrained_alphabet,
    check_vertical_twosquare_crib_consistency,
)
from projects.dagapeyeff.two_square_annealer import STANDARD_ALPHABET


def test_candidate_incipits_loaded():
    assert len(CANDIDATE_INCIPITS) >= 10
    assert "ORDNANCESURVEY" in CANDIDATE_INCIPITS
    assert "PATENTSPECIFICATION" in CANDIDATE_INCIPITS


def test_crib_consistency_logic():
    # Construct artificial coordinates where 'OR' maps consistently
    # P[0] = 'O', P[1] = 'R'.
    # In Vertical Two-Square:
    # C[0] = (r1, c2), C[1] = (r2, c1)
    # So 'O' in Sq1 at (r1, c1), 'R' in Sq2 at (r2, c2).
    # If r1=1, c1=2, r2=3, c2=4:
    # C[0] = (1, 4), C[1] = (3, 2).
    coords = [(1, 4), (3, 2)] * 10
    res = check_vertical_twosquare_crib_consistency("OROR", coords, dual_alphabets=True)
    assert res.is_consistent is True
    assert "O" in res.pinned_cells_sq1
    assert res.pinned_cells_sq1["O"] == (1, 2)
    assert "R" in res.pinned_cells_sq2
    assert res.pinned_cells_sq2["R"] == (3, 4)

    # Inconsistent case: conflicting coordinates for 'O'
    conflicting_coords = [(1, 4), (3, 2), (2, 4), (3, 2)]  # 'O' second time gets row 2 instead of 1
    res_conflict = check_vertical_twosquare_crib_consistency("OROR", conflicting_coords, dual_alphabets=True)
    assert res_conflict.is_consistent is False
    assert "Sq1 conflict" in res_conflict.rejection_reason


def test_build_crib_constrained_alphabet():
    pinned = {"O": (1, 2), "R": (3, 4)}
    alpha = build_crib_constrained_alphabet(pinned)
    assert len(alpha) == 25
    assert len(set(alpha)) == 25
    assert alpha[1 * 5 + 2] == "O"
    assert alpha[3 * 5 + 4] == "R"
