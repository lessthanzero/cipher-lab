"""Nihilist Modular Additive Key Engine for D'Agapeyeff.

Implements secondary modular addition/subtraction on Polybius coordinates (mod 5)
applied either BEFORE or AFTER columnar transposition.
Preserves the strict row-in-{6,7,8,9,0} and col-in-{1,2,3,4,5} alternating structure.
"""

from __future__ import annotations

from typing import List, Tuple

# Row mapping: {6:1, 7:2, 8:3, 9:4, 0:5}
ROW_MAP = {"6": 1, "7": 2, "8": 3, "9": 4, "0": 5}
INV_ROW_MAP = {1: "6", 2: "7", 3: "8", 4: "9", 5: "0"}


def pairs_to_coords(pairs: List[str]) -> List[Tuple[int, int]]:
    """Convert pair strings to 1-indexed (row, col) integer coordinates."""
    coords = []
    for p in pairs:
        if len(p) == 2:
            r = ROW_MAP.get(p[0], 1)
            try:
                c = int(p[1])
            except ValueError:
                c = 1
            coords.append((r, c))
    return coords


def coords_to_pairs(coords: List[Tuple[int, int]]) -> List[str]:
    """Convert (row, col) integer coordinates back to two-digit pair strings."""
    pairs = []
    for r, c in coords:
        r_d = INV_ROW_MAP.get(r, "6")
        c_d = str(max(1, min(5, c)))
        pairs.append(r_d + c_d)
    return pairs


def derive_additive_key_from_keyword(keyword: str, alphabet: str = "ABCDEFGHIKLMNOPQRSTUVWXYZ") -> List[Tuple[int, int]]:
    """Derive modular additive key shifts (0..4, 0..4) from a keyword using Polybius coordinates."""
    alpha_grid = {}
    idx = 0
    for r in range(1, 6):
        for c in range(1, 6):
            if idx < len(alphabet):
                alpha_grid[alphabet[idx]] = (r - 1, c - 1)
            idx += 1

    shifts = []
    for char in keyword.upper().replace("J", "I"):
        if char.isalpha():
            shifts.append(alpha_grid.get(char, (0, 0)))
    return shifts if shifts else [(0, 0)]


def subtract_additive_key(coords: List[Tuple[int, int]], key_shifts: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Subtract periodic additive key shifts modulo 5 from coordinate stream."""
    if not key_shifts:
        return coords

    period = len(key_shifts)
    out = []
    for i, (r, c) in enumerate(coords):
        kr, kc = key_shifts[i % period]
        r_new = (r - 1 - kr) % 5 + 1
        c_new = (c - 1 - kc) % 5 + 1
        out.append((r_new, c_new))
    return out


def add_additive_key(coords: List[Tuple[int, int]], key_shifts: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Add periodic additive key shifts modulo 5 to coordinate stream."""
    if not key_shifts:
        return coords

    period = len(key_shifts)
    out = []
    for i, (r, c) in enumerate(coords):
        kr, kc = key_shifts[i % period]
        r_new = (r - 1 + kr) % 5 + 1
        c_new = (c - 1 + kc) % 5 + 1
        out.append((r_new, c_new))
    return out
