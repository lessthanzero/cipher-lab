"""Cartographic Grid & Coordinate Geometry Engine for D'Agapeyeff Cipher.

Models the geometrical and drafting conventions of a 1930s British civilian 
cartographer and patent draughtsman:
- Easting before Northing (column-first coordinate reading)
- Cartesian Bottom-Up grid reading (Northing increasing upwards from bottom-left)
- Diagonal Matrix Transposition (Pelling 2014: folding Column 14 into a terminal row of nulls)
- Drafting Contour Spiral and Boustrophedon Traverses
"""

from __future__ import annotations

from typing import List, Tuple


def pairs_to_grid(pairs: List[str], width: int = 14) -> List[List[str]]:
    """Reshape a 1D sequence of pairs into a 2D matrix [rows][cols]."""
    height = (len(pairs) + width - 1) // width
    grid = []
    for r in range(height):
        row = pairs[r * width : (r + 1) * width]
        while len(row) < width:
            row.append("75")  # Safe standard filler
        grid.append(row)
    return grid


def grid_to_pairs(grid: List[List[str]], original_len: int) -> List[str]:
    """Flatten a 2D grid row-wise back to 1D sequence of original length."""
    out = []
    for row in grid:
        out.extend(row)
    return out[:original_len]


def read_cartesian_bottom_up(pairs: List[str], width: int = 14) -> List[str]:
    """Read grid as a Cartesian map coordinate plane: bottom row upward, left to right.
    
    In British Ordnance Survey convention, Northing = 0 is at the bottom margin.
    Reading rows from bottom to top inverts the vertical axis.
    """
    grid = pairs_to_grid(pairs, width)
    # Bottom row first, moving upwards
    inverted_grid = grid[::-1]
    return grid_to_pairs(inverted_grid, len(pairs))


def read_easting_first(pairs: List[str], width: int = 14) -> List[str]:
    """Read grid 'Easting before Northing': column-by-column (left-to-right, top-to-bottom).
    
    Standard cartographic rule for reporting grid coordinates.
    """
    grid = pairs_to_grid(pairs, width)
    height = len(grid)
    out = []
    for c in range(width):
        for r in range(height):
            out.append(grid[r][c])
    return out[:len(pairs)]


def read_diagonal_matrix_transpose(pairs: List[str], width: int = 14) -> List[str]:
    """Reflect the 14x14 grid across its main diagonal (M[r][c] -> M[c][r]).
    
    Nick Pelling (2014) structural invariant:
    Flipping across the main diagonal maps Column 14 (where all 5 rarest anomaly symbols 
    cluster in D'Agapeyeff's cryptogram) into Row 14 (the bottom row), transforming margin 
    anomalies into a clean terminal padding block.
    """
    grid = pairs_to_grid(pairs, width)
    height = len(grid)
    out_grid = [[grid[r][c] for r in range(height)] for c in range(width)]
    return grid_to_pairs(out_grid, len(pairs))


def read_contour_spiral(pairs: List[str], width: int = 14, clockwise: bool = True) -> List[str]:
    """Traverse grid in an inward spiral, simulating drafting a perimeter contour inward."""
    grid = pairs_to_grid(pairs, width)
    height = len(grid)
    top, bottom = 0, height - 1
    left, right = 0, width - 1
    out = []

    while top <= bottom and left <= right:
        if clockwise:
            # Left to Right
            for c in range(left, right + 1):
                out.append(grid[top][c])
            top += 1
            # Top to Bottom
            for r in range(top, bottom + 1):
                out.append(grid[r][right])
            right -= 1
            # Right to Left
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    out.append(grid[bottom][c])
                bottom -= 1
            # Bottom to Top
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    out.append(grid[r][left])
                left += 1
        else:
            # Counter-clockwise: Top to Bottom along left
            for r in range(top, bottom + 1):
                out.append(grid[r][left])
            left += 1
            for c in range(left, right + 1):
                out.append(grid[bottom][c])
            bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    out.append(grid[r][right])
                right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    out.append(grid[top][c])
                top += 1

    return out[:len(pairs)]


def read_cartographic_boustrophedon(
    pairs: List[str], width: int = 14, vertical: bool = False
) -> List[str]:
    """Serpentine survey traverse: alternating directions on successive survey lines."""
    grid = pairs_to_grid(pairs, width)
    height = len(grid)
    out = []

    if not vertical:
        # Horizontal boustrophedon (survey rows)
        for r in range(height):
            row = grid[r]
            if r % 2 == 1:
                out.extend(row[::-1])
            else:
                out.extend(row)
    else:
        # Vertical boustrophedon (survey columns)
        for c in range(width):
            col = [grid[r][c] for r in range(height)]
            if c % 2 == 1:
                out.extend(col[::-1])
            else:
                out.extend(col)

    return out[:len(pairs)]


# Catalog of all cartographic grid operators for systematic permutation sweeps
CARTOGRAPHIC_OPERATORS = {
    "cartesian_bottom_up": read_cartesian_bottom_up,
    "easting_first": read_easting_first,
    "diagonal_transpose": read_diagonal_matrix_transpose,
    "contour_spiral_cw": lambda p, w=14: read_contour_spiral(p, w, clockwise=True),
    "contour_spiral_ccw": lambda p, w=14: read_contour_spiral(p, w, clockwise=False),
    "boustrophedon_horiz": lambda p, w=14: read_cartographic_boustrophedon(p, w, vertical=False),
    "boustrophedon_vert": lambda p, w=14: read_cartographic_boustrophedon(p, w, vertical=True),
}
