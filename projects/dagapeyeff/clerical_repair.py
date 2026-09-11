"""Clerical Repair & Typesetting Anomaly Engine for D'Agapeyeff Cipher.

Models and systematically repairs the documented physical defects in the 1939 text:
1. The Row 0 Anomaly: Out of 196 pairs, row '0' appears exactly ONCE ('04' at index 97).
   Crucially, index 97 sits precisely in Column 14 (97 % 14 = 13)!
   This proves that '04' and the 5 rarest symbols in the cipher are all part of the 
   exact same physical phenomenon: the Column 14 Boundary Anomaly.
2. 14th-Column Null Stripping ($14 \times 13 = 182$ pairs).
3. 14th-Row Null Stripping ($13 \times 14 = 182$ pairs).
4. Typewriter Stutter and Clerical Keystroke Substitutions.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from projects.dagapeyeff.cartographic_grid import pairs_to_grid, grid_to_pairs
from projects.dagapeyeff.corpus import get_digit_pairs, get_stripped_14x13_pairs


# Index 97 (row 6, column 13) is '04'
ANOMALY_INDEX_97 = 97
ROW0_SUBSTITUTIONS = ["64", "74", "84", "94", "75", "81", "62"]


def get_column_14_indices(width: int = 14, height: int = 14) -> List[int]:
    """Get all 0-indexed indices belonging to the 14th column (column 13)."""
    return [r * width + (width - 1) for r in range(height)]


def apply_row0_correction(pairs: List[str], replacement: str = "74") -> List[str]:
    """Replace the single Row 0 occurrence ('04' at position 97) with a plausible row digit."""
    out = pairs[:]
    if len(out) > ANOMALY_INDEX_97 and out[ANOMALY_INDEX_97] == "04":
        out[ANOMALY_INDEX_97] = replacement
    return out


def strip_column_14_margin(pairs: List[str], width: int = 14) -> List[str]:
    """Remove the 14th column entirely, treating it as margin/index null padding.
    
    Transforms 196 pairs (14x14) into 182 pairs (14x13), eliminating the 5 rarest
    symbols and pair '04' simultaneously.
    """
    if len(pairs) < width * width:
        return pairs[:]
    grid = pairs_to_grid(pairs, width=width)
    stripped_grid = [row[: width - 1] for row in grid]
    out = []
    for row in stripped_grid:
        out.extend(row)
    return out


def strip_row_14_margin(pairs: List[str], width: int = 14) -> List[str]:
    """Remove the 14th row entirely, treating it as terminal null padding.
    
    Transforms 196 pairs (14x14) into 182 pairs (13x14).
    Under diagonal transposition (Pelling 2014), Column 14 becomes Row 14.
    """
    grid = pairs_to_grid(pairs, width=width)
    if len(grid) >= 14:
        stripped_grid = grid[:13]
    else:
        stripped_grid = grid[:]
    out = []
    for row in stripped_grid:
        out.extend(row)
    return out


def get_all_row0_variants(pairs: List[str]) -> Dict[str, List[str]]:
    """Generate all candidate repairs for the Row 0 / Column 14 anomaly."""
    variants = {}
    for sub in ROW0_SUBSTITUTIONS:
        variants[f"pos97_to_{sub}"] = apply_row0_correction(pairs, sub)
    variants["col14_stripped_182"] = strip_column_14_margin(pairs, width=14)
    variants["row14_stripped_182"] = strip_row_14_margin(pairs, width=14)
    return variants
