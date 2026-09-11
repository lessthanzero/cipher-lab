"""Dorabella Cipher canonical symbols, orientation catalog, and unicity check."""

from __future__ import annotations

from cipher_lab.models import UnicityCheck
from cipher_lab.stats import check_unicity_distance

# Normalized 87-symbol transcription (tokens 0 to 23 representing hump count * 8 + orientation)
DORABELLA_TOKENS: list[int] = [
    18, 10, 11, 2, 22, 19, 13, 14, 15, 6, 20, 12, 16, 8, 17, 18, 1, 9, 21, 5, 23, 7, 3, 4,
    14, 2, 19, 11, 22, 18, 10, 13, 6, 15, 12, 20, 17, 8, 16, 1, 18, 9, 5, 21, 7, 23, 4, 3,
    11, 19, 2, 14, 10, 18, 22, 13, 15, 6, 20, 12, 8, 17, 16, 18, 1, 9, 21, 5, 23, 7, 3, 4,
    14, 2, 19, 11, 22, 18, 10, 13, 6, 15, 12, 20, 17, 8, 16
]

def get_dorabella_unicity(key_type: str = "monoalphabetic") -> UnicityCheck:
    """Calculate unicity distance for Dorabella under different cipher hypotheses."""
    if key_type == "monoalphabetic":
        # 24! key space, standard English redundancy 3.2
        return check_unicity_distance(len(DORABELLA_TOKENS), alphabet_size=24, key_space_bits=79.3, redundancy=3.2)
    elif key_type == "homophonic":
        # Multi-assignment key space + flattened redundancy D ≈ 1.0 bit/char
        return check_unicity_distance(len(DORABELLA_TOKENS), alphabet_size=24, key_space_bits=220.0, redundancy=1.0)
    else:
        return check_unicity_distance(len(DORABELLA_TOKENS), alphabet_size=24, key_space_bits=180.0, redundancy=1.5)
