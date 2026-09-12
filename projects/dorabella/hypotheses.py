"""Dorabella Hypothesis Models, Elgar Lexicon, and Structural Generators."""

from __future__ import annotations

import random
from typing import Dict, List, Set

ELGAR_KEYWORDS: List[str] = [
    "DORAPENNY",
    "EDWARDELGAR",
    "ELGAR",
    "VARIATIONS",
    "ENIGMA",
    "LADYMARY",
    "CARICE",
    "ALICE",
    "MALVERN",
    "GREATMALVERN",
    "WORCESTER",
    "SUSSEX",
    "CATHEDRAL",
    "ORGANIST",
    "SYMPHONY",
    "VIOLIN",
    "CONCERTO",
    "NIMROD",
    "JAEGER",
    "CHORAL",
    "POWICK",
    "FORMBY",
    "BIRCH",
    "KITE",
    "MUSIC",
]

# 24-letter English alphabet (combining I/J and U/V or omitting J/Z)
ALPHABET_24: str = "ABCDEFGHIKLMNOPQRSTUVWXY"

# English frequency ordering (high, medium, low)
ENGLISH_FREQ_ORDER: str = "ETAONIRSHDLCUMWFGYPBVKXQ"


def generate_frequency_tiered_mapping() -> Dict[int, str]:
    """Hypothesis: 1-hump = highest frequency letters, 2-humps = medium, 3-humps = rare."""
    # 8 orientations per hump tier
    tier1 = ENGLISH_FREQ_ORDER[0:8]   # E, T, A, O, N, I, R, S
    tier2 = ENGLISH_FREQ_ORDER[8:16]  # H, D, L, C, U, M, W, F
    tier3 = ENGLISH_FREQ_ORDER[16:24] # G, Y, P, B, V, K, X, Q

    mapping: Dict[int, str] = {}
    for ori in range(8):
        mapping[0 * 8 + ori] = tier1[ori]
        mapping[1 * 8 + ori] = tier2[ori]
        mapping[2 * 8 + ori] = tier3[ori]
    return mapping


def generate_keyword_alphabet_24(keyword: str) -> str:
    """Generate 24-letter alphabet keyed by keyword (combining I/J and U/V)."""
    clean = "".join([c for c in keyword.upper().replace("J", "I").replace("Z", "S") if c in ALPHABET_24])
    seen: Set[str] = set()
    res: List[str] = []
    for c in clean:
        if c not in seen:
            seen.add(c)
            res.append(c)
    for c in ALPHABET_24:
        if c not in seen:
            seen.add(c)
            res.append(c)
    return "".join(res[:24])


def generate_random_mapping(seed: int | None = None) -> Dict[int, str]:
    """Generate random bijective mapping of 24 tokens to 24 letters."""
    rng = random.Random(seed)
    letters = list(ALPHABET_24)
    rng.shuffle(letters)
    return {t: letters[t] for t in range(24)}


def scramble_tokens(tokens: List[int], seed: int | None = None) -> List[int]:
    """Twin-negative control: Scramble token order preserving exact token marginals."""
    rng = random.Random(seed)
    scrambled = list(tokens)
    rng.shuffle(scrambled)
    return scrambled
