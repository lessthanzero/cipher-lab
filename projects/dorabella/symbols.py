"""Dorabella Cipher Symbol Decomposition & Physical Geometry.

Edward Elgar's cipher consists of 87 characters across 3 lines:
- Line 1: 24 symbols
- Line 2: 24 symbols
- Line 3: 39 symbols

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
from typing import Dict, List, Tuple

from projects.dorabella.corpus import DORABELLA_TOKENS


@dataclass(frozen=True)
class DorabellaSymbol:
    token_id: int
    humps: int          # 1, 2, or 3
    orientation_idx: int # 0 to 7
    angle_deg: int      # 0, 45, 90, 135, 180, 225, 270, 315
    direction_name: str # E, NE, N, NW, W, SW, S, SE


DIRECTIONS = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]


def token_to_symbol(token: int) -> DorabellaSymbol:
    """Decompose integer token into humps and geometric orientation."""
    humps = (token // 8) + 1
    ori_idx = token % 8
    return DorabellaSymbol(
        token_id=token,
        humps=humps,
        orientation_idx=ori_idx,
        angle_deg=ori_idx * 45,
        direction_name=DIRECTIONS[ori_idx],
    )


SYMBOL_CATALOG: Dict[int, DorabellaSymbol] = {t: token_to_symbol(t) for t in range(24)}


def get_dorabella_symbols() -> List[DorabellaSymbol]:
    """Return the ordered list of 87 physical symbols."""
    return [SYMBOL_CATALOG[t] for t in DORABELLA_TOKENS]


def decode_tokens(tokens: List[int], mapping: Dict[int, str]) -> str:
    """Decode token sequence into string using the provided symbol-to-char mapping."""
    return "".join(mapping.get(t, "?") for t in tokens)
