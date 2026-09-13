"""Shugborough Inscription transcription, epigraphic encoding, and underdetermination guards."""

from __future__ import annotations

from typing import Dict, List, Tuple

from cipher_lab.models import UnicityCheck
from cipher_lab.stats import check_unicity_distance

# Primary 8-letter inscription on upper line
SHUGBOROUGH_TEXT = "OUOSVAVV"

# Flanking lower-tier characters (Dis Manibus formula)
SHUGBOROUGH_FRAMING = ("D", "M")

# Canonical epigraphic representation with explicit carved interpuncts
SHUGBOROUGH_EPIGRAPHIC_UPPER = "O·U·O·S·V·A·V·V"
SHUGBOROUGH_EPIGRAPHIC_FRAMING = ("D·", "M·")

# Distinction between rounded vocalic U and pointed consonantal V
SHUGBOROUGH_LETTER_TYPES: List[Tuple[str, str]] = [
    ("O", "round_vowel"),
    ("U", "round_vowel_carved_U"),
    ("O", "round_vowel"),
    ("S", "sibilant"),
    ("V", "pointed_consonant_carved_V"),
    ("A", "pointed_vowel"),
    ("V", "pointed_consonant_carved_V"),
    ("V", "pointed_consonant_carved_V"),
]


def get_shugborough_unicity() -> UnicityCheck:
    """Demonstrate mathematical underdetermination (N=8 chars vs U_0 >= 28.5 chars)."""
    return check_unicity_distance(
        payload_len=len(SHUGBOROUGH_TEXT),
        alphabet_size=26,
        key_space_bits=88.4,  # log2(26!)
    )


def get_token_summary() -> Dict[str, str | int | bool]:
    """Return dictionary summary of canonical corpus attributes."""
    return {
        "text": SHUGBOROUGH_TEXT,
        "framing": f"{SHUGBOROUGH_FRAMING[0]} ... {SHUGBOROUGH_FRAMING[1]}",
        "length_upper": len(SHUGBOROUGH_TEXT),
        "length_total": len(SHUGBOROUGH_TEXT) + 2,
        "interpuncts_present": True,
        "u_v_distinction_observed": True,
        "epigraphic_string": f"{SHUGBOROUGH_EPIGRAPHIC_FRAMING[0]}  {SHUGBOROUGH_EPIGRAPHIC_UPPER}  {SHUGBOROUGH_EPIGRAPHIC_FRAMING[1]}",
    }
