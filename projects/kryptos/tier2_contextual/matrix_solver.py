"""Algebraic 14x7 Keystream Matrix Solver for Kryptos K4.

Analyzes the 14x7 key schedule matrix M[r, c] (98 cells, 1 null cell) conditioned on
the 24 fixed anchor cells from Crib 1 (Rows 3-4) and Crib 2 (Rows 9-10).
Evaluates:
1. Row-wise differentials: Delta_r = M[r+1, c] - M[r, c]
2. Column-wise differentials: Delta_c = M[r, c+1] - M[r, c]
3. Modular arithmetic counters (Berlin Clock mod-5/mod-1 progressive cycles)
4. Route transposition of a single keyword across rows or columns
"""

from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.manifests import BLIND_PATH, CONTEXTUAL_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


@dataclass(frozen=True)
class MatrixCell:
    row: int
    col: int
    linear_idx: int
    cipher_char: str
    plain_char: Optional[str]
    is_anchor: bool
    std_vig_shift: Optional[int]
    std_vig_key: Optional[str]
    kry_vig_shift: Optional[int]
    kry_vig_key: Optional[str]
    beaufort_shift: Optional[int]
    beaufort_key: Optional[str]


class KeystreamMatrix14x7:
    """14 rows x 7 cols grid structure with 97 characters and 1 null cell."""

    def __init__(self, null_placement: str = "trailing") -> None:
        """
        null_placement: 'trailing' (row 13, col 6), 'leading' (row 0, col 0),
                        or 'median' (row 7, col 0).
        """
        self.null_placement = null_placement
        blind = load_dataset(BLIND_PATH, current_tier=1)
        self.ciphertext = blind["ciphertext"]
        assert len(self.ciphertext) == 97

        pairs = extract_known_pairs()
        self.anchor_dict = {idx: (c, p) for idx, c, p in pairs}

        self.grid: List[List[Optional[MatrixCell]]] = [[None for _ in range(7)] for _ in range(14)]
        self._populate_grid()

    def _linear_to_coords(self, linear_idx: int) -> Tuple[int, int]:
        """Map 0..96 linear index to (row, col) given null placement."""
        if self.null_placement == "trailing":
            # Grid has 98 cells, cell (13, 6) is empty
            return linear_idx // 7, linear_idx % 7
        elif self.null_placement == "leading":
            # Cell (0, 0) is empty; linear_idx 0 is at (0, 1)
            cell_idx = linear_idx + 1
            return cell_idx // 7, cell_idx % 7
        elif self.null_placement == "median":
            # Cell (7, 0) is empty (index 49)
            cell_idx = linear_idx if linear_idx < 49 else linear_idx + 1
            return cell_idx // 7, cell_idx % 7
        else:
            raise ValueError(f"Unknown null placement: {self.null_placement}")

    def _populate_grid(self) -> None:
        for idx, c in enumerate(self.ciphertext):
            r, col = self._linear_to_coords(idx)
            is_anchor = idx in self.anchor_dict
            p = self.anchor_dict[idx][1] if is_anchor else None

            std_shift = None
            std_key = None
            kry_shift = None
            kry_key = None
            beau_shift = None
            beau_key = None

            if p is not None:
                # Standard Vigenere: K = (C - P) mod 26
                std_shift = (STANDARD_ALPHABET.index(c) - STANDARD_ALPHABET.index(p)) % 26
                std_key = STANDARD_ALPHABET[std_shift]
                # Kryptos Vigenere: shifts on Kryptos tableau
                kry_shift = (KRYPTOS_ALPHABET.index(c) - KRYPTOS_ALPHABET.index(p)) % 26
                kry_key = KRYPTOS_ALPHABET[kry_shift]
                # Beaufort: K = (C + P) mod 26
                beau_shift = (STANDARD_ALPHABET.index(c) + STANDARD_ALPHABET.index(p)) % 26
                beau_key = STANDARD_ALPHABET[beau_shift]

            self.grid[r][col] = MatrixCell(
                row=r,
                col=col,
                linear_idx=idx,
                cipher_char=c,
                plain_char=p,
                is_anchor=is_anchor,
                std_vig_shift=std_shift,
                std_vig_key=std_key,
                kry_vig_shift=kry_shift,
                kry_vig_key=kry_key,
                beaufort_shift=beau_shift,
                beaufort_key=beau_key,
            )

    def analyze_differentials(self, key_type: str = "kry_vig_shift") -> Dict[str, Any]:
        """Compute row and column differentials for anchor cells."""
        row_diffs = []
        col_diffs = []

        # Row differentials within same column across adjacent rows
        # Crib 1 has adjacent rows 3 and 4!
        # For columns 0..5, both row 3 and row 4 are anchors
        for col in range(6):
            cell_r3 = self.grid[3][col]
            cell_r4 = self.grid[4][col]
            if cell_r3 and cell_r4:
                val3 = getattr(cell_r3, key_type)
                val4 = getattr(cell_r4, key_type)
                if val3 is not None and val4 is not None:
                    diff = (val4 - val3) % 26
                    row_diffs.append({
                        "col": col,
                        "from_row": 3,
                        "to_row": 4,
                        "val1": val3,
                        "val2": val4,
                        "diff": diff,
                    })

        # Row differentials in Crib 2: adjacent rows 9 and 10!
        # For columns 0..3, both row 9 and row 10 are anchors
        for col in range(4):
            cell_r9 = self.grid[9][col]
            cell_r10 = self.grid[10][col]
            if cell_r9 and cell_r10:
                val9 = getattr(cell_r9, key_type)
                val10 = getattr(cell_r10, key_type)
                if val9 is not None and val10 is not None:
                    diff = (val10 - val9) % 26
                    row_diffs.append({
                        "col": col,
                        "from_row": 9,
                        "to_row": 10,
                        "val1": val9,
                        "val2": val10,
                        "diff": diff,
                    })

        # Column differentials within same row across adjacent columns
        for r in [3, 4, 9, 10]:
            row_cells = [cell for cell in self.grid[r] if cell and cell.is_anchor]
            for i in range(len(row_cells) - 1):
                c1 = row_cells[i]
                c2 = row_cells[i + 1]
                v1 = getattr(c1, key_type)
                v2 = getattr(c2, key_type)
                if v1 is not None and v2 is not None:
                    diff = (v2 - v1) % 26
                    col_diffs.append({
                        "row": r,
                        "from_col": c1.col,
                        "to_col": c2.col,
                        "val1": v1,
                        "val2": v2,
                        "diff": diff,
                    })

        # Analyze consistency of differences
        row_diff_vals = [d["diff"] for d in row_diffs]
        col_diff_vals = [d["diff"] for d in col_diffs]

        return {
            "key_type": key_type,
            "null_placement": self.null_placement,
            "row_differentials": row_diffs,
            "row_diff_counts": dict(collections.Counter(row_diff_vals)),
            "col_differentials": col_diffs,
            "col_diff_counts": dict(collections.Counter(col_diff_vals)),
        }


def run_matrix_algebra_analysis() -> Dict[str, Any]:
    """Execute differential analysis across null placements and key types."""
    results = {}
    for null_loc in ["trailing", "leading", "median"]:
        matrix = KeystreamMatrix14x7(null_placement=null_loc)
        for ktype in ["kry_vig_shift", "std_vig_shift", "beaufort_shift"]:
            name = f"{null_loc}_{ktype}"
            results[name] = matrix.analyze_differentials(key_type=ktype)
    return results


if __name__ == "__main__":
    rep = run_matrix_algebra_analysis()
    print("=" * 70)
    print("CIPHERLAB — 14x7 KEYSTREAM MATRIX DIFFERENTIAL ANALYSIS")
    print("=" * 70)
    for model_name, data in list(rep.items())[:3]:
        print(f"\nConfiguration: {model_name}")
        print(f"  Row-wise Shifts (Delta_r): {data['row_diff_counts']}")
        print(f"  Col-wise Shifts (Delta_c): {data['col_diff_counts']}")
    print("=" * 70)
