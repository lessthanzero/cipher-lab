"""Kerckhoffs Defect & Historical Book Keyword Models for D'Agapeyeff Cipher.

Models the exact historical defects documented in Alexander D'Agapeyeff's (1939)
worked example of double columnar transposition:
1. The Kerckhoffs Inversion: Executing decryption direction instead of encryption
2. The SCHUVALOF Ranking Error: Copying Kerckhoffs' SCHUVALOW numeric ordering verbatim 
   without adjusting for the letter 'F'
3. Book-Specific Keywords from Codes and Ciphers and Maps (OUP)
"""

from __future__ import annotations

from typing import Dict, List

from projects.dagapeyeff.cartographic_grid import grid_to_pairs, pairs_to_grid

# Historical Key Phrases and Words directly appearing in D'Agapeyeff's books
BOOK_KEYWORDS: Dict[str, str] = {
    # Worked example in Codes and Ciphers (p. 142-143)
    "SCHUVALOW_KERCKHOFFS": "SCHUVALOW",
    "SCHUVALOF_BOOK_TEXT": "SCHUVALOF",
    "SHUVALOV_RUSSIAN": "SHUVALOV",
    "REUNION_TOMORROW": "REUNIONTOMORROW",
    "RAILWAY_STATION": "RAILWAYSTATION",
    "BRING_ARMS": "BRINGARMS",
    
    # Author & Publication Details
    "DAGAPEYEFF": "DAGAPEYEFF",
    "ALEXANDER_DAGAPEYEFF": "ALEXANDERDAGAPEYEFF",
    "CODES_AND_CIPHERS": "CODESANDCIPHERS",
    "OXFORD_PRESS": "OXFORDUNIVERSITYPRESS",
    "COMPASS_BOOKS": "COMPASSBOOKS",
    "HADFIELD": "HADFIELD",
    
    # Cartography Book ("Maps", 1942 OUP)
    "ORDNANCE_SURVEY": "ORDNANCESURVEY",
    "RETRIANGULATION": "RETRIANGULATION",
    "TRIG_POINT": "TRIGPOINT",
    "BENCHMARK": "BENCHMARK",
    "CASSINI": "CASSINI",
    "HOTINE": "HOTINE",
    "GRID_REFERENCE": "GRIDREFERENCE",
}


def get_standard_key_order(keyword: str) -> List[int]:
    """Derive standard mathematical column ordering from a keyword (alphabetical rank)."""
    clean_kw = "".join([c for c in keyword.upper() if c.isalpha()])
    indexed = sorted(list(enumerate(clean_kw)), key=lambda x: (x[1], x[0]))
    ranks = [0] * len(clean_kw)
    for rank, (orig_idx, _) in enumerate(indexed):
        ranks[orig_idx] = rank
    return ranks


def get_historical_shuvalof_ranks() -> Dict[str, List[int]]:
    """Return both D'Agapeyeff's flawed book ranking and the corrected alphabetical ranking."""
    return {
        # Kerckhoffs 1883 (SCHUVALOW): A=1, C=2, H=3, L=4, O=5, S=6, U=7, V=8, W=9
        # In 0-indexed: [5, 1, 2, 6, 7, 0, 3, 4, 8]
        "kerckhoffs_original_schuvalow": [5, 1, 2, 6, 7, 0, 3, 4, 8],
        
        # D'Agapeyeff book text: printed "SCHUVALOF" with Kerckhoffs' numbers verbatim!
        # Giving F rank 9 even though F is between C and H!
        "dagapeyeff_erroneous_schuvalof": [5, 1, 2, 6, 7, 0, 3, 4, 8],
        
        # Correct alphabetical ranking of S C H U V A L O F:
        # A=0, C=1, F=2, H=3, L=4, O=5, S=6, U=7, V=8
        # S(6), C(1), H(3), U(7), V(8), A(0), L(4), O(5), F(2)
        "mathematically_correct_schuvalof": [6, 1, 3, 7, 8, 0, 4, 5, 2],
    }


def apply_columnar_transposition_direction(
    pairs: List[str],
    col_order: List[int],
    mode: str = "kerckhoffs_decryption",
) -> List[str]:
    """Execute columnar transposition under either encryption or reversed decryption mode.
    
    col_order: Permutation of column indices [0 .. width-1].
    mode:
      - 'kerckhoffs_decryption': D'Agapeyeff's actual worked example method (reading into 
        columns ordered by key, then reading out rows).
      - 'standard_encryption': Normal columnar transposition (writing in by rows, reading 
        out by columns in key order).
    """
    width = len(col_order)
    height = (len(pairs) + width - 1) // width
    grid = pairs_to_grid(pairs, width)
    
    if mode == "kerckhoffs_decryption":
        # In D'Agapeyeff's worked example (Marie & Pelling 2017):
        # Columns of the matrix are filled in the order specified by the keyword ranking,
        # and then read out across rows.
        # This reorders the columns: column c comes from col_order[c]
        out_grid = [[grid[r][col_order[c]] for c in range(width)] for r in range(height)]
        return grid_to_pairs(out_grid, len(pairs))
    else:
        # Standard encryption: grid written row-wise, read column-wise in order of key
        # Invert the permutation
        inv_order = [0] * width
        for i, c in enumerate(col_order):
            inv_order[c] = i
        out_grid = [[grid[r][inv_order[c]] for c in range(width)] for r in range(height)]
        return grid_to_pairs(out_grid, len(pairs))


def apply_double_kerckhoffs_transposition(
    pairs: List[str],
    key_order: List[int],
    mode: str = "kerckhoffs_decryption",
) -> List[str]:
    """Execute the full Russian Nihilist double transposition as described by D'Agapeyeff.
    
    In Codes and Ciphers p. 142:
    "transposed vertically, then transposed horizontally... using the same keyword in both".
    """
    width = len(key_order)
    # Stage 1: Column transposition
    step1 = apply_columnar_transposition_direction(pairs, key_order, mode=mode)
    
    # Stage 2: Row transposition using the same key order
    grid = pairs_to_grid(step1, width)
    height = len(grid)
    row_order = key_order[:height] if len(key_order) >= height else (key_order * ((height // len(key_order)) + 1))[:height]
    
    if mode == "kerckhoffs_decryption":
        out_grid = [grid[row_order[r]] for r in range(height)]
    else:
        inv_row = [0] * height
        for i, r in enumerate(row_order):
            inv_row[r] = i
        out_grid = [grid[inv_row[r]] for r in range(height)]
        
    return grid_to_pairs(out_grid, len(pairs))
