"""Exact Square Extractor from Semantically Normalized 182-Character Text.

Directly maps the 182 characters to cells in Square 1 and Square 2
using the winning Cartesian Two-Square coordinates.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from projects.dagapeyeff.algebraic_cell_extractor import get_winning_coordinates
from projects.dagapeyeff.two_square import STANDARD_ALPHABET, TwoSquareEngine
from cipher_lab.stats import QuadgramScorer, calculate_chi_squared, calculate_index_of_coincidence

TARGET_PT_182 = "BDNGRADIECARONGOSSOMEASSHESENDCARDSWEREALLTHATAIDIFITISTOUSEORDERMENGETWHEREACLOSUREALLITISASPECIALCASEBUTYETATALLBOUNDWEREFORASITISAMORNINGTOILSECTORENSUREDAYBYDAYEXPERTSWINGSIGNALS"


def main() -> None:
    coords = get_winning_coordinates()
    assert len(coords) == 182
    text = TARGET_PT_182.upper().replace("J", "I")
    assert len(text) == 182, f"Expected 182 chars, got {len(text)}"

    sq1_cells: Dict[Tuple[int, int], Dict[str, int]] = {}
    sq2_cells: Dict[Tuple[int, int], Dict[str, int]] = {}

    for i in range(0, 182, 2):
        r1, c1 = coords[i]
        r2, c2 = coords[i + 1]

        tc1 = c2 if c1 != c2 else c1
        tc2 = c1 if c1 != c2 else c2

        ch1 = text[i]
        ch2 = text[i + 1]

        if (r1, tc1) not in sq1_cells:
            sq1_cells[(r1, tc1)] = {}
        sq1_cells[(r1, tc1)][ch1] = sq1_cells[(r1, tc1)].get(ch1, 0) + 1

        if (r2, tc2) not in sq2_cells:
            sq2_cells[(r2, tc2)] = {}
        sq2_cells[(r2, tc2)][ch2] = sq2_cells[(r2, tc2)].get(ch2, 0) + 1

    print("=" * 80)
    print("EXACT TWO-SQUARE CELL ASSIGNMENT DERIVATION")
    print(f"Square 1 cells addressed: {len(sq1_cells)}/25")
    print(f"Square 2 cells addressed: {len(sq2_cells)}/25")
    print("=" * 80)

    print("\n--- Square 1 Derived Cells ---")
    sq1_grid = [["." for _ in range(5)] for _ in range(5)]
    sq1_assigned = set()
    for (r, c), votes in sorted(sq1_cells.items()):
        top_c = sorted(votes.items(), key=lambda x: x[1], reverse=True)[0][0]
        sq1_grid[r][c] = top_c
        sq1_assigned.add(top_c)
        print(f"  Sq1[{r},{c}] = {top_c} (votes: {votes})")

    print("\n--- Square 2 Derived Cells ---")
    sq2_grid = [["." for _ in range(5)] for _ in range(5)]
    sq2_assigned = set()
    for (r, c), votes in sorted(sq2_cells.items()):
        top_c = sorted(votes.items(), key=lambda x: x[1], reverse=True)[0][0]
        sq2_grid[r][c] = top_c
        sq2_assigned.add(top_c)
        print(f"  Sq2[{r},{c}] = {top_c} (votes: {votes})")

    # Display grids
    print("\n" + "=" * 80)
    print("DERIVED POLYBIUS SQUARES:")
    print("=" * 80)
    print("Square 1:")
    for r in range(5):
        print("  " + " ".join(sq1_grid[r]))

    print("\nSquare 2:")
    for r in range(5):
        print("  " + " ".join(sq2_grid[r]))

    print(f"\nUnused in Square 1: {set(STANDARD_ALPHABET) - sq1_assigned}")
    print(f"Unused in Square 2: {set(STANDARD_ALPHABET) - sq2_assigned}")


if __name__ == "__main__":
    main()
