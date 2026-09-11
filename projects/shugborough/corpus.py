"""Shugborough Inscription transcription and mandatory underdetermination guard."""

from __future__ import annotations

from cipher_lab.models import UnicityCheck
from cipher_lab.stats import check_unicity_distance

SHUGBOROUGH_TEXT = "OUOSVAVV"
SHUGBOROUGH_FRAMING = ("D", "M")

def get_shugborough_unicity() -> UnicityCheck:
    """Demonstrate mathematical underdetermination (N=8 chars vs U_0 >= 25 chars)."""
    return check_unicity_distance(
        payload_len=len(SHUGBOROUGH_TEXT),
        alphabet_size=26,
        key_space_bits=88.4,  # log2(26!)
    )
