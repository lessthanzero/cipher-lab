"""Algebraic Cell Extractor for Vertical Two-Square.

In Vertical Two-Square:
Given ciphertext pair i (even) and i+1 (odd) with coordinates (r1, c1) and (r2, c2):
If c1 != c2:
    p1 = Grid1[r1, c2]
    p2 = Grid2[r2, c1]
If c1 == c2:
    p1 = Grid1[r1, c1]
    p2 = Grid2[r2, c2]

Therefore, for any known character p1 at even position i:
    Grid1[r1, c2 if c1 != c2 else c1] MUST be p1.
And for any known character p2 at odd position i+1:
    Grid2[r2, c1 if c1 != c2 else c2] MUST be p2.
"""

from __future__ import annotations

import collections
from typing import Dict, List, Tuple

from projects.dagapeyeff.admiralty_sweep import generate_hydrographical_duplicate_rankings
from projects.dagapeyeff.cartographic_grid import (
    read_cartesian_bottom_up,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.two_square import pairs_to_coordinates


def get_winning_coordinates() -> List[Tuple[int, int]]:
    """Derive the 182 coordinates for the winning key."""
    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    rankings_dict = dict(generate_hydrographical_duplicate_rankings())
    ranks = rankings_dict["hydro_tie_AR_HR_RR"]
    _w, h = 14, 13
    col_order = ranks
    row_ranks = ranks[:h]
    row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
    row_order = [0] * h
    for r_i, (orig_i, _) in enumerate(row_indexed):
        row_order[orig_i] = r_i

    t_pairs = apply_generalized_double_transposition(
        diag_182, col_order=col_order, row_order=row_order, mode="standard_encryption", order="row_then_col"
    )
    final_pairs = read_cartesian_bottom_up(t_pairs, width=14)
    return pairs_to_coordinates(final_pairs)


def main() -> None:
    coords = get_winning_coordinates()
    assert len(coords) == 182

    # Map each position 0..181 to (square, row, col)
    pos_to_cell: List[Tuple[int, int, int]] = []
    for i in range(0, 182, 2):
        r1, c1 = coords[i]
        r2, c2 = coords[i + 1]
        
        target_c1 = c2 if c1 != c2 else c1
        target_c2 = c1 if c1 != c2 else c2

        pos_to_cell.append((1, r1, target_c1))
        pos_to_cell.append((2, r2, target_c2))

    print("=" * 80)
    print("VERTICAL TWO-SQUARE: ALGEBRAIC CELL MAPPING DIRECTORY")
    print("=" * 80)

    # Let's inspect which positions map to which cells in Grid1 and Grid2
    grid1_refs: Dict[Tuple[int, int], List[int]] = collections.defaultdict(list)
    grid2_refs: Dict[Tuple[int, int], List[int]] = collections.defaultdict(list)

    for pos, (sq, r, c) in enumerate(pos_to_cell):
        if sq == 1:
            grid1_refs[(r, c)].append(pos)
        else:
            grid2_refs[(r, c)].append(pos)

    print(f"Square 1 cells addressed by ciphertext: {len(grid1_refs)}/25 cells")
    print(f"Square 2 cells addressed by ciphertext: {len(grid2_refs)}/25 cells")

    # Let's see if there are multiple positions referencing the SAME cell:
    print("\n--- Square 1 Co-referencing Positions (same cell must have same letter!) ---")
    sq1_multi = {k: v for k, v in grid1_refs.items() if len(v) > 1}
    print(f"Total multi-referenced cells in Square 1: {len(sq1_multi)}")
    for (r, c), positions in sorted(sq1_multi.items()):
        print(f"  Cell ({r}, {c}): referenced by positions {positions}")

    print("\n--- Square 2 Co-referencing Positions (same cell must have same letter!) ---")
    sq2_multi = {k: v for k, v in grid2_refs.items() if len(v) > 1}
    print(f"Total multi-referenced cells in Square 2: {len(sq2_multi)}")
    for (r, c), positions in sorted(sq2_multi.items()):
        print(f"  Cell ({r}, {c}): referenced by positions {positions}")


if __name__ == "__main__":
    main()
