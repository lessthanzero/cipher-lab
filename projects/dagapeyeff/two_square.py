"""Two-Square Cryptographic Engine for D'Agapeyeff.

Implements the exact Two-Square (double-square) cipher model tested by Tim Marland
(dagapeyeffresearch.com Phase 6, record Q = -692.13).

Supports:
- Vertical orientation (Square 1 above Square 2; column coordinates swapped)
- Horizontal orientation (Square 1 left of Square 2; row coordinates swapped)
- Dual independent Polybius alphabets (50 letters) vs single shared alphabet (25 letters)
- Sequential digraph stream pairing vs vertical grid-column pairing
- Exact round-trip encryption and decryption
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


# Standard Polybius coordinate mapping for D'Agapeyeff
ROW_MAP: Dict[str, int] = {"6": 0, "7": 1, "8": 2, "9": 3, "0": 4}
REV_ROW_MAP: Dict[int, str] = {0: "6", 1: "7", 2: "8", 3: "9", 4: "0"}

COL_MAP: Dict[str, int] = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4}
REV_COL_MAP: Dict[int, str] = {0: "1", 1: "2", 2: "3", 3: "4", 4: "5"}

STANDARD_ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # 25 letters, I/J merged


def pairs_to_coordinates(pairs: List[str]) -> List[Tuple[int, int]]:
    """Convert string pairs (e.g. '75', '62') to 0-indexed (row, col) coordinates."""
    coords = []
    for p in pairs:
        if len(p) == 2:
            r = ROW_MAP.get(p[0], 0)
            c = COL_MAP.get(p[1], 0)
            coords.append((r, c))
        else:
            coords.append((0, 0))
    return coords


def coordinates_to_pairs(coords: List[Tuple[int, int]]) -> List[str]:
    """Convert (row, col) coordinates back to D'Agapeyeff digit pairs."""
    return [f"{REV_ROW_MAP.get(r, '6')}{REV_COL_MAP.get(c, '1')}" for r, c in coords]


class TwoSquareEngine:
    """Core Two-Square cipher execution engine."""

    def __init__(
        self,
        alphabet1: str = STANDARD_ALPHABET,
        alphabet2: Optional[str] = None,
        orientation: str = "vertical",
        pairing_mode: str = "sequential",
        grid_width: int = 14,
    ) -> None:
        self.alphabet1 = alphabet1.upper().replace("J", "I")[:25]
        if alphabet2 is not None:
            self.alphabet2 = alphabet2.upper().replace("J", "I")[:25]
        else:
            self.alphabet2 = self.alphabet1
        self.orientation = orientation.lower()
        self.pairing_mode = pairing_mode.lower()
        self.grid_width = grid_width

        self._build_lookup_tables()

    def _build_lookup_tables(self) -> None:
        """Pre-compute forward and reverse lookup matrices for high performance."""
        # Matrix 1
        self.grid1: List[List[str]] = [[self.alphabet1[r * 5 + c] for c in range(5)] for r in range(5)]
        self.pos1: Dict[str, Tuple[int, int]] = {
            self.alphabet1[r * 5 + c]: (r, c) for r in range(5) for c in range(5)
        }

        # Matrix 2
        self.grid2: List[List[str]] = [[self.alphabet2[r * 5 + c] for c in range(5)] for r in range(5)]
        self.pos2: Dict[str, Tuple[int, int]] = {
            self.alphabet2[r * 5 + c]: (r, c) for r in range(5) for c in range(5)
        }

    def set_alphabets(self, alphabet1: str, alphabet2: Optional[str] = None) -> None:
        """Update alphabets and rebuild lookup tables."""
        self.alphabet1 = alphabet1.upper().replace("J", "I")[:25]
        self.alphabet2 = (alphabet2 or alphabet1).upper().replace("J", "I")[:25]
        self._build_lookup_tables()

    def decipher_coordinates(self, coords: List[Tuple[int, int]]) -> str:
        """Decipher a sequence of (row, col) coordinate pairs into plaintext letters."""
        n = len(coords)
        out: List[str] = ["?"] * n

        if self.pairing_mode == "sequential":
            # Group consecutive pairs: (0, 1), (2, 3), ...
            for i in range(0, n - 1, 2):
                r1, c1 = coords[i]
                r2, c2 = coords[i + 1]

                if self.orientation == "vertical":
                    # Vertical Two-Square: swap column coordinates if c1 != c2
                    if c1 != c2:
                        p1 = self.grid1[r1][c2]
                        p2 = self.grid2[r2][c1]
                    else:
                        p1 = self.grid1[r1][c1]
                        p2 = self.grid2[r2][c2]
                else:
                    # Horizontal Two-Square: swap row coordinates if r1 != r2
                    if r1 != r2:
                        p1 = self.grid1[r2][c1]
                        p2 = self.grid2[r1][c2]
                    else:
                        p1 = self.grid1[r1][c1]
                        p2 = self.grid2[r2][c2]

                out[i] = p1
                out[i + 1] = p2

            if n % 2 == 1:
                # Odd trailing coordinate, direct decode in square 1
                r, c = coords[-1]
                out[-1] = self.grid1[r][c]

        elif self.pairing_mode == "vertical_grid":
            # Pairs are laid out in a grid of width W.
            # Digraphs are formed by cells in column c: (row 2r, c) and (row 2r+1, c)
            width = self.grid_width
            num_rows = n // width
            
            for c in range(width):
                for r in range(0, num_rows - 1, 2):
                    idx1 = r * width + c
                    idx2 = (r + 1) * width + c
                    if idx2 < n:
                        r1, c1 = coords[idx1]
                        r2, c2 = coords[idx2]

                        if self.orientation == "vertical":
                            if c1 != c2:
                                p1 = self.grid1[r1][c2]
                                p2 = self.grid2[r2][c1]
                            else:
                                p1 = self.grid1[r1][c1]
                                p2 = self.grid2[r2][c2]
                        else:
                            if r1 != r2:
                                p1 = self.grid1[r2][c1]
                                p2 = self.grid2[r1][c2]
                            else:
                                p1 = self.grid1[r1][c1]
                                p2 = self.grid2[r2][c2]

                        out[idx1] = p1
                        out[idx2] = p2

            # Any unfilled cells decode directly
            for i in range(n):
                if out[i] == "?":
                    r, c = coords[i]
                    out[i] = self.grid1[r][c]

        return "".join(out)

    def encipher_plaintext(self, plaintext: str) -> Tuple[str, List[Tuple[int, int]]]:
        """Encipher plaintext letters into ciphertext digraphs and coordinates."""
        clean = "".join(c.upper().replace("J", "I") for c in plaintext if c.isalpha())
        if len(clean) % 2 != 0:
            clean += "X"

        cipher_chars: List[str] = []
        coords: List[Tuple[int, int]] = []

        for i in range(0, len(clean), 2):
            l1, l2 = clean[i], clean[i + 1]
            r1, c1 = self.pos1.get(l1, (0, 0))
            r2, c2 = self.pos2.get(l2, (0, 0))

            if self.orientation == "vertical":
                if c1 != c2:
                    c_l1 = self.grid1[r1][c2]
                    c_l2 = self.grid2[r2][c1]
                    coords.append((r1, c2))
                    coords.append((r2, c1))
                else:
                    c_l1 = l1
                    c_l2 = l2
                    coords.append((r1, c1))
                    coords.append((r2, c2))
            else:
                if r1 != r2:
                    c_l1 = self.grid1[r2][c1]
                    c_l2 = self.grid2[r1][c2]
                    coords.append((r2, c1))
                    coords.append((r1, c2))
                else:
                    c_l1 = l1
                    c_l2 = l2
                    coords.append((r1, c1))
                    coords.append((r2, c2))

            cipher_chars.append(c_l1)
            cipher_chars.append(c_l2)

        return "".join(cipher_chars), coords
