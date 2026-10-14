"""Tier 2 Intentional Errata and Phase Dislocation Engine for Kryptos K4.

Models historical Sanborn errata and potential text dislocations:
1. Historical Errata Coordinates:
   - K1: IQLUSION (pos 35) -> 'Q' instead of 'L'
   - K2: UNDERGRUUND (pos 232) -> 'U' instead of 'O'
   - K2: IDBYROWS (pos 368..375) -> 8 extra letters
   - K3: DESPARATLY (pos 133) -> 'A' instead of 'E'
   - Tableau: Extra 'L' in Row 14 (between rows M and N)

2. Phase Shift & Dislocation Invariance:
   Tests whether omitted/inserted null characters (deltas in [-7..+7]) between Crib 1 and Crib 2
   can reconcile periodic polyalphabetic keys across periods 1..14.

3. Errata-Seeded Cardan Stencil Masks:
   Maps errata coordinates modulo 97 into binary stencil masks.
"""

from __future__ import annotations

import argparse
import time
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


ERRATA_COORDINATES: Dict[str, Any] = {
    "k1_iqlusion": 35,
    "k2_undergruund": 232,
    "k2_idbyrows": list(range(368, 376)),
    "k3_desparatly": 133,
    "tableau_extra_l": 14 * 31 + 31,  # end of row 14
}


def test_phase_dislocation(
    max_delta: int = 7,
    max_period: int = 14,
) -> List[Dict[str, Any]]:
    """
    Tests whether an unencrypted phase shift delta in [-max_delta..+max_delta]
    between Crib 1 (pos 21..33) and Crib 2 (pos 63..73) yields a consistent periodic key.
    """
    pairs = extract_known_pairs()
    crib1 = {idx: (c, p) for idx, c, p in pairs if 21 <= idx <= 33}
    crib2 = {idx: (c, p) for idx, c, p in pairs if 63 <= idx <= 73}

    hits = []
    alphabets = [("standard", STANDARD_ALPHABET), ("kryptos", KRYPTOS_ALPHABET)]
    modes = ["vigenere", "beaufort"]

    for alpha_name, alpha in alphabets:
        for mode in modes:
            for delta in range(-max_delta, max_delta + 1):
                for L in range(1, max_period + 1):
                    residues = {}
                    conflict = False
                    # Crib 1 residues
                    for idx, (c, p) in crib1.items():
                        c_val = alpha.index(c)
                        p_val = alpha.index(p)
                        k_val = (c_val - p_val) % 26 if mode == "vigenere" else (c_val + p_val) % 26
                        rem = idx % L
                        if rem in residues:
                            if residues[rem] != k_val:
                                conflict = True
                                break
                        else:
                            residues[rem] = k_val
                    if conflict:
                        continue

                    # Crib 2 residues with delta offset
                    for idx, (c, p) in crib2.items():
                        c_val = alpha.index(c)
                        p_val = alpha.index(p)
                        k_val = (c_val - p_val) % 26 if mode == "vigenere" else (c_val + p_val) % 26
                        rem = (idx + delta) % L
                        if rem in residues:
                            if residues[rem] != k_val:
                                conflict = True
                                break
                        else:
                            residues[rem] = k_val

                    if not conflict and len(residues) >= 6:
                        hits.append({
                            "delta": delta,
                            "period": L,
                            "mode": mode,
                            "alphabet": alpha_name,
                            "residues": len(residues),
                        })

    return hits


def evaluate_errata_stencil_mask() -> Dict[str, Any]:
    """Generates Cardan masks from historical errata coordinates and evaluates alignment."""
    # Map errata to 97-cell grid coordinates
    errata_cells = set()
    for name, val in ERRATA_COORDINATES.items():
        if isinstance(val, int):
            errata_cells.add(val % 97)
        elif isinstance(val, list):
            for v in val:
                errata_cells.add(v % 97)

    # Invert and test mask consistency
    pairs = extract_known_pairs()
    inside_mask = [p for p in pairs if p[0] in errata_cells]
    outside_mask = [p for p in pairs if p[0] not in errata_cells]

    return {
        "errata_cell_indices": sorted(errata_cells),
        "crib_anchors_inside_mask": len(inside_mask),
        "crib_anchors_outside_mask": len(outside_mask),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CIPHERLAB — TIER 2 ERRATA & PHASE DISLOCATION ENGINE")
    print("=" * 70)

    t0 = time.time()
    dislocations = test_phase_dislocation(max_delta=7, max_period=14)
    stencil_info = evaluate_errata_stencil_mask()
    elapsed = time.time() - t0

    print(f"Executed in {elapsed:.3f}s\n")
    print(f"Phase Dislocation Hits (deltas -7..+7, periods 1..14): {len(dislocations)}")
    if dislocations:
        for h in dislocations:
            print(f"  Hit: delta={h['delta']:+d}, L={h['period']}, {h['mode']}, {h['alphabet']}")
    else:
        print("  Zero periodic key alignments found under any phase dislocation.")

    print(f"\nErrata Stencil Cells: {stencil_info['errata_cell_indices']}")
    print(f"Crib anchors inside errata mask: {stencil_info['crib_anchors_inside_mask']}/24")
    print("=" * 70)
