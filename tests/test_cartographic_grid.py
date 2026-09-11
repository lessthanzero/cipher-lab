"""Unit tests for cartographic grid operations and coordinate transformations."""

from __future__ import annotations

import pytest

from projects.dagapeyeff.cartographic_grid import (
    CARTOGRAPHIC_OPERATORS,
    pairs_to_grid,
    grid_to_pairs,
    read_cartesian_bottom_up,
    read_easting_first,
    read_diagonal_matrix_transpose,
    read_contour_spiral,
    read_cartographic_boustrophedon,
)
from projects.dagapeyeff.corpus import get_digit_pairs


def test_pairs_to_grid_and_back() -> None:
    """Verify lossless grid shaping and flattening."""
    pairs = get_digit_pairs()
    grid = pairs_to_grid(pairs, width=14)
    assert len(grid) == 14
    assert all(len(row) == 14 for row in grid)

    restored = grid_to_pairs(grid, len(pairs))
    assert restored == pairs


def test_cartesian_bottom_up() -> None:
    """Verify bottom-up row inversion."""
    pairs = [str(i) for i in range(16)]
    transformed = read_cartesian_bottom_up(pairs, width=4)
    # Original row 0 was 0,1,2,3; row 3 was 12,13,14,15
    # Bottom-up: row 3 comes first: 12,13,14,15
    assert transformed[:4] == ["12", "13", "14", "15"]
    assert transformed[-4:] == ["0", "1", "2", "3"]


def test_diagonal_matrix_transpose() -> None:
    """Verify diagonal transposition reflects across main diagonal and moves col 13 to row 13."""
    pairs = get_digit_pairs()
    # Anomaly pair '04' is at index 97 (row 6, column 13)
    assert pairs[97] == "04"
    
    transposed = read_diagonal_matrix_transpose(pairs, width=14)
    # After transpose, M[6][13] moves to M[13][6] -> index 13*14 + 6 = 188
    assert transposed[13 * 14 + 6] == "04"
    assert len(transposed) == 196


def test_easting_first_length_and_coverage() -> None:
    """Verify easting-first reads all cells without loss."""
    pairs = get_digit_pairs()
    transformed = read_easting_first(pairs, width=14)
    assert len(transformed) == 196
    assert set(transformed) == set(pairs)


def test_all_cartographic_operators_catalog() -> None:
    """Verify all operators in catalog execute without error and preserve length."""
    pairs = get_digit_pairs()
    for name, op in CARTOGRAPHIC_OPERATORS.items():
        result = op(pairs)
        assert len(result) == 196, f"Failed length check for operator {name}"
