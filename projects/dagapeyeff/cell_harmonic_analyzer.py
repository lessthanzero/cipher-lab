"""Cell Harmonic Analyzer for Two-Square Squares.

Tests what happens across all 182 positions when each of the 50 cells
in Square 1 and Square 2 is varied.
Since each cell is referenced by multiple positions simultaneously,
a correct letter change should improve multiple positions across the message!
"""

from __future__ import annotations

import collections
from typing import Dict, List, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_chi_squared, calculate_index_of_coincidence
from projects.dagapeyeff.algebraic_cell_extractor import get_winning_coordinates
from projects.dagapeyeff.two_square import STANDARD_ALPHABET, TwoSquareEngine

TARGET_SQ1 = "BDCOATXLUIGSRENHPWMYFZKQV"
TARGET_SQ2 = "WIMLTVRGCNESDYAKOZUBXFPHQ"


def main() -> None:
    coords = get_winning_coordinates()
    engine = TwoSquareEngine(alphabet1=TARGET_SQ1, alphabet2=TARGET_SQ2, orientation="vertical", pairing_mode="sequential")
    base_pt = engine.decipher_coordinates(coords)
    scorer = QuadgramScorer(language="english")
    base_q = scorer.score_total(base_pt)

    print("=" * 80)
    print("CELL HARMONIC SENSITIVITY & LINGUISTIC ALIGNMENT")
    print(f"Base Plaintext Q-Score: {base_q:.2f}")
    print("=" * 80)

    # Map positions to cells
    pos_map: Dict[int, Tuple[int, int, int]] = {}
    cell_to_pos: Dict[Tuple[int, int, int], List[int]] = collections.defaultdict(list)
    for i in range(0, 182, 2):
        r1, c1 = coords[i]
        r2, c2 = coords[i + 1]
        tc1 = c2 if c1 != c2 else c1
        tc2 = c1 if c1 != c2 else c2
        pos_map[i] = (1, r1, tc1)
        pos_map[i + 1] = (2, r2, tc2)
        cell_to_pos[(1, r1, tc1)].append(i)
        cell_to_pos[(2, r2, tc2)].append(i + 1)

    # Test single-cell mutations that improve Q-score
    improvements: List[Tuple[float, int, int, int, str, str, List[int], str]] = []

    # Test Square 1 mutations
    sq1_grid = [[TARGET_SQ1[r * 5 + c] for c in range(5)] for r in range(5)]
    sq2_grid = [[TARGET_SQ2[r * 5 + c] for c in range(5)] for r in range(5)]

    for r in range(5):
        for c in range(5):
            orig_char = sq1_grid[r][c]
            positions = cell_to_pos.get((1, r, c), [])
            if not positions:
                continue
            for cand_char in STANDARD_ALPHABET:
                if cand_char == orig_char or cand_char in TARGET_SQ1.replace(orig_char, ""):
                    continue  # Keep alphabet valid (no duplicates)
                
                # Test swapping orig_char with cand_char in TARGET_SQ1
                cand_a1 = list(TARGET_SQ1)
                idx_orig = cand_a1.index(orig_char)
                idx_cand = cand_a1.index(cand_char)
                cand_a1[idx_orig], cand_a1[idx_cand] = cand_a1[idx_cand], cand_a1[idx_orig]
                new_a1 = "".join(cand_a1)

                engine.set_alphabets(new_a1, TARGET_SQ2)
                new_pt = engine.decipher_coordinates(coords)
                new_q = scorer.score_total(new_pt)
                delta = new_q - base_q

                if delta > 0:
                    improvements.append((delta, 1, r, c, orig_char, cand_char, positions, new_pt))

    # Test Square 2 mutations
    for r in range(5):
        for c in range(5):
            orig_char = sq2_grid[r][c]
            positions = cell_to_pos.get((2, r, c), [])
            if not positions:
                continue
            for cand_char in STANDARD_ALPHABET:
                if cand_char == orig_char or cand_char in TARGET_SQ2.replace(orig_char, ""):
                    continue
                cand_a2 = list(TARGET_SQ2)
                idx_orig = cand_a2.index(orig_char)
                idx_cand = cand_a2.index(cand_char)
                cand_a2[idx_orig], cand_a2[idx_cand] = cand_a2[idx_cand], cand_a2[idx_orig]
                new_a2 = "".join(cand_a2)

                engine.set_alphabets(TARGET_SQ1, new_a2)
                new_pt = engine.decipher_coordinates(coords)
                new_q = scorer.score_total(new_pt)
                delta = new_q - base_q

                if delta > 0:
                    improvements.append((delta, 2, r, c, orig_char, cand_char, positions, new_pt))

    improvements.sort(key=lambda x: x[0], reverse=True)

    print(f"\nDiscovered {len(improvements)} Single-Swap Improvements over Baseline Q={base_q:.2f}:")
    for i, (delta, sq, r, c, old_c, new_c, pos, pt) in enumerate(improvements[:15], 1):
        print(f"{i:2d}. [+{delta:5.2f} pts] Sq{sq}[{r},{c}]: '{old_c}' <-> '{new_c}' (affects positions {pos})")
        print(f"    Sample: \"{pt[17:90]}...\"")


if __name__ == "__main__":
    main()
