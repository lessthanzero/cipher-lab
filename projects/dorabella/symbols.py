"""Dorabella Cipher Symbol Decomposition & Physical Geometry.

Edward Elgar's cipher consists of 87 characters across 3 lines:
- Line 1: 24 symbols
- Line 2: 33 symbols
- Line 3: 30 symbols (with a dot after character 5)

Each of the 24 symbol types is characterized by:
- Hump count: 1, 2, or 3 semicircular loops
- Orientation: 8 compass directions (0° to 315° in 45° steps)
  0: E (0°)
  1: NE (45°)
  2: N (90°)
  3: NW (135°)
  4: W (180°)
  5: SW (225°)
  6: S (270°)
  7: SE (315°)

Token encoding: token_id = (hump_count - 1) * 8 + orientation_id (0 <= token_id < 24)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from projects.dorabella.corpus import DORABELLA_TOKENS


@dataclass(frozen=True)
class DorabellaSymbol:
    token_id: int
    humps: int           # 1, 2, or 3
    orientation_idx: int # 0 to 7
    angle_deg: int       # 0, 45, 90, 135, 180, 225, 270, 315
    direction_name: str  # E, NE, N, NW, W, SW, S, SE
    musical_pitch: str   # Solfège / note degree (C, D, E, F, G, A, B, C')
    clock_hour: float    # Clock-face hour equivalent (1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0)


DIRECTIONS = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]
# Musical mapping: 8 compass points mapped to 8 diatonic scale steps (C major baseline)
SCALE_DEGREES = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
# Clock-face equivalent hours (starting East = 3 o'clock, clockwise)
CLOCK_HOURS = [3.0, 1.5, 12.0, 10.5, 9.0, 7.5, 6.0, 4.5]


def token_to_symbol(token: int) -> DorabellaSymbol:
    """Decompose integer token into physical and musical geometry."""
    humps = (token // 8) + 1
    ori_idx = token % 8
    return DorabellaSymbol(
        token_id=token,
        humps=humps,
        orientation_idx=ori_idx,
        angle_deg=ori_idx * 45,
        direction_name=DIRECTIONS[ori_idx],
        musical_pitch=SCALE_DEGREES[ori_idx],
        clock_hour=CLOCK_HOURS[ori_idx],
    )


SYMBOL_CATALOG: Dict[int, DorabellaSymbol] = {t: token_to_symbol(t) for t in range(24)}


def get_dorabella_symbols() -> List[DorabellaSymbol]:
    """Return the ordered list of 87 physical symbols."""
    return [SYMBOL_CATALOG[t] for t in DORABELLA_TOKENS]


def get_symbol_frequency_profile() -> Dict[int, int]:
    """Return histogram of token frequencies across the 87 characters."""
    counts: Dict[int, int] = {t: 0 for t in range(24)}
    for t in DORABELLA_TOKENS:
        counts[t] += 1
    return counts


def get_hump_distribution() -> Dict[int, int]:
    """Return frequency of 1-, 2-, and 3-hump glyphs."""
    hump_counts = {1: 0, 2: 0, 3: 0}
    for t in DORABELLA_TOKENS:
        humps = (t // 8) + 1
        hump_counts[humps] += 1
    return hump_counts


def get_orientation_distribution() -> Dict[str, int]:
    """Return frequency of glyphs by orientation."""
    ori_counts = {d: 0 for d in DIRECTIONS}
    for t in DORABELLA_TOKENS:
        ori = DIRECTIONS[t % 8]
        ori_counts[ori] += 1
    return ori_counts


def decode_tokens(tokens: List[int], mapping: Dict[int, str]) -> str:
    """Decode token sequence into string using the provided symbol-to-char mapping."""
    return "".join(mapping.get(t, "?") for t in tokens)
