"""Tier 2 Transposition Models for Kryptos K4.

Models classical transposition systems taught by Edward Scheidt to Jim Sanborn:
1. 90-Degree Matrix Rotations (the exact transformation verified in Kryptos K3).
2. Rectangular Grid Transposition with candidate null padding (98, 100, 104, 112 cells).
3. Columnar Transposition (regular and irregular).
4. Berlin Clock base-5 route transposition.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def rotate_matrix_90_clockwise(grid: List[List[str]]) -> List[List[str]]:
    """Rotate a 2D rectangular grid 90 degrees clockwise."""
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    # New grid has dimensions cols x rows
    rotated = [[grid[rows - 1 - r][c] for r in range(rows)] for c in range(cols)]
    return rotated


def rotate_matrix_90_counter_clockwise(grid: List[List[str]]) -> List[List[str]]:
    """Rotate a 2D rectangular grid 90 degrees counter-clockwise."""
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    rotated = [[grid[r][cols - 1 - c] for r in range(rows)] for c in range(cols)]
    return rotated


def text_to_grid(text: str, rows: int, cols: int, pad_char: str = "") -> List[List[str]]:
    """Fill a grid of size rows x cols with text (row by row)."""
    grid = []
    idx = 0
    total = rows * cols
    padded = text + pad_char * max(0, total - len(text))
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(padded[idx] if idx < len(padded) else pad_char)
            idx += 1
        grid.append(row)
    return grid


def grid_to_text(grid: List[List[str]], strip_chars: str = "") -> str:
    """Read out a grid row by row."""
    chars = []
    for row in grid:
        for ch in row:
            if ch not in strip_chars:
                chars.append(ch)
    return "".join(chars)


def read_columns_bottom_to_top_left_to_right(grid: List[List[str]]) -> str:
    """Read grid columns bottom-to-top, left-to-right (Sanborn's K3 route)."""
    rows = len(grid)
    cols = len(grid[0])
    chars = []
    for c in range(cols):
        for r in range(rows - 1, -1, -1):
            chars.append(grid[r][c])
    return "".join(chars)


def read_columns_top_to_bottom_left_to_right(grid: List[List[str]]) -> str:
    """Read grid columns top-to-bottom, left-to-right (Standard columnar)."""
    rows = len(grid)
    cols = len(grid[0])
    chars = []
    for c in range(cols):
        for r in range(rows):
            chars.append(grid[r][c])
    return "".join(chars)


def generate_candidate_grid_dimensions(n: int = 97, max_nulls: int = 15) -> List[Tuple[int, int, int]]:
    """Generate (rows, cols, nulls) for composite grid sizes from N to N + max_nulls."""
    candidates = []
    for total in range(n, n + max_nulls + 1):
        nulls = total - n
        for r in range(2, int(math.isqrt(total)) + 1):
            if total % r == 0:
                c = total // r
                candidates.append((r, c, nulls))
                if r != c:
                    candidates.append((c, r, nulls))
    return sorted(candidates, key=lambda x: (x[2], x[0]))


def apply_sanborn_k3_style_double_transposition(
    text: str,
    r1: int,
    c1: int,
    r2: int,
    c2: int,
    pad_char: str = "?",
) -> str:
    """Apply Sanborn's two-stage rotation transposition as used in Kryptos K3."""
    # Stage 1: write into r1 x c1, read bottom-to-top, left-to-right
    g1 = text_to_grid(text, r1, c1, pad_char=pad_char)
    inter = read_columns_bottom_to_top_left_to_right(g1)

    # Stage 2: write into r2 x c2, read bottom-to-top, left-to-right
    g2 = text_to_grid(inter, r2, c2, pad_char=pad_char)
    final = read_columns_bottom_to_top_left_to_right(g2)
    return final


def test_grid_configurations() -> List[Dict[str, Any]]:
    """Test standard grid configurations on N=97."""
    configs = generate_candidate_grid_dimensions(n=97, max_nulls=7)
    results = []
    for r, c, nulls in configs:
        results.append({
            "rows": r,
            "cols": c,
            "total_cells": r * c,
            "nulls_required": nulls,
        })
    return results


if __name__ == "__main__":
    grids = test_grid_configurations()
    print("Candidate Rectangular Grid Dimensions for Kryptos K4 (with <= 7 nulls):")
    for g in grids[:12]:
        print(f"  {g['rows']:2d} x {g['cols']:2d} = {g['total_cells']:3d} cells ({g['nulls_required']} nulls)")
