"""Reversed Kerckhoffs double-transposition engine and structural hypothesis generator.

Addresses Nick Pelling's 2017 finding that D'Agapeyeff copied his method from Auguste Kerckhoffs' 
1883 'La Cryptographie Militaire' with encryption and decryption steps swapped.
"""

from __future__ import annotations

from typing import List

from cipher_lab.solvers import PolybiusCheckerboard


class KerckhoffsEngine:
    """Implements both standard and reversed Kerckhoffs double-transposition on grids of pairs."""

    def __init__(self, key_alphabet: str = "ABCDEFGHIKLMNOPQRSTUVWXYZ") -> None:
        self.checkerboard = PolybiusCheckerboard(key_alphabet=key_alphabet, size=5)
        # Row mapping: {6:1, 7:2, 8:3, 9:4, 0:5}
        self.row_map = {"6": 1, "7": 2, "8": 3, "9": 4, "0": 5}

    def decode_pair_stream(self, pairs: List[str]) -> str:
        """Decode a list of valid two-digit pairs into characters using the Polybius square."""
        chars = []
        for p in pairs:
            if len(p) == 2:
                r_digit, c_digit = p[0], p[1]
                r = self.row_map.get(r_digit, 1)
                try:
                    c = int(c_digit)
                except ValueError:
                    c = 1
                chars.append(self.checkerboard.coord_to_char.get((r, c), "?"))
        return "".join(chars)

    def apply_single_pair_transposition(self, pairs: List[str], width: int, col_order: List[int]) -> List[str]:
        """Apply columnar transposition over pairs rather than raw digits."""
        num_rows = len(pairs) // width
        if num_rows * width != len(pairs):
            return pairs
        
        # Form grid of pairs
        grid = [pairs[r * width : (r + 1) * width] for r in range(num_rows)]
        
        # Read out columns in col_order
        reordered_cols = []
        for c in col_order:
            if c < width:
                reordered_cols.extend([grid[r][c] for r in range(num_rows)])
        return reordered_cols

    def apply_reversed_kerckhoffs_double_transposition(
        self,
        pairs: List[str],
        row_key: List[int],
        col_key: List[int],
        width: int = 14,
    ) -> List[str]:
        """Apply Kerckhoffs double-transposition with swapped encryption/decryption instructions.
        
        Kerckhoffs specifies:
        1. Inscribe by rows / columns.
        2. Permute rows by Key 1.
        3. Permute columns by Key 2.
        4. Read out by column / row.
        """
        num_rows = len(pairs) // width
        if len(row_key) != num_rows or len(col_key) != width:
            return pairs

        # Step 1: Inscribe into grid
        grid = [pairs[r * width : (r + 1) * width] for r in range(num_rows)]

        # Step 2: Permute rows according to row_key
        row_permuted = [grid[r] for r in row_key]

        # Step 3: Permute columns according to col_key
        fully_permuted = []
        for r in range(num_rows):
            new_row = [row_permuted[r][c] for c in col_key]
            fully_permuted.append(new_row)

        # Step 4: Read out in inverted order (column-by-column rather than row-by-row)
        readout = []
        for c in range(width):
            for r in range(num_rows):
                readout.append(fully_permuted[r][c])
        return readout

    def apply_position_97_correction(self, pairs: List[str], replacement: str = "75") -> List[str]:
        """Apply Marland's position 97 anomaly correction (04 -> replacement)."""
        res = list(pairs)
        if len(res) > 97:
            res[97] = replacement
        return res
