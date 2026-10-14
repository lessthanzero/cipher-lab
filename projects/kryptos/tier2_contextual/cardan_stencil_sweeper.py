"""Tier 2 Cardan Stencil Mask Sweeper for Kryptos K4.

Implements 1989-era physical paper stencil masks over the 14x7 grid:
1. Symmetries of the 14x7 rectangle:
   - 180-deg rotation: (r, c) <-> (13 - r, 6 - c)
   - Vertical reflection: (r, c) <-> (13 - r, c)
   - Horizontal reflection: (r, c) <-> (r, 6 - c)
   - Alternating / Checkerboard / Slit patterns
2. Two-stream decomposition:
   - 49 cells in Phase 1 (Stream A)
   - 49 cells in Phase 2 (Stream B)
   - For all 24 anchor positions, test if Stream A and Stream B each admit a consistent:
     a) Periodic key (periods 1..14)
     b) Historical keyword (KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, CLOCK, etc.)
     c) Constant Caesar shift

Outputs verified candidate partitions and logs falsifications.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from projects.kryptos.manifests import BLIND_PATH, CONTEXTUAL_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


GRID_ROWS = 14
GRID_COLS = 7
TEXT_LEN = 97


HISTORICAL_KEYWORDS = [
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "SANBORN",
    "SCHEIDT",
    "LANGLEY",
    "BERLIN",
    "CLOCK",
    "EASTNORTHEAST",
    "NORTHEAST",
    "SHADOWFORCES",
    "VIRTUALLYINVISIBLE",
    "LUCIDMEMORY",
    "DIGETALINTERPRETATIT",
    "WELTZEITUHR",
    "ALEXANDERPLATZ",
    "MEDUSA",
    "DEFECTOR",
    "TUTANKHAMUN",
    "CARTER",
    "LAYERTWO",
]


def get_symmetry_pairs(mode: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
    """Return pairs of complementary cells (cell1, cell2) under rectangle symmetry."""
    pairs = []
    seen: Set[Tuple[int, int]] = set()

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell = (r, c)
            if cell in seen:
                continue

            if mode == "rot180":
                comp = (13 - r, 6 - c)
            elif mode == "flip_v":
                comp = (13 - r, c)
            elif mode == "flip_h":
                comp = (r, 6 - c)
            else:
                raise ValueError(f"Unknown symmetry: {mode}")

            if cell == comp:
                # Fixed point cell (only possible if odd dimensions)
                continue

            pairs.append((cell, comp))
            seen.add(cell)
            seen.add(comp)

    return pairs


def test_stream_period_consistency(
    stream_keys: Dict[int, int],
    max_period: int = 14,
) -> Dict[int, int]:
    """
    For a single stream mapping linear_idx -> required_key (0..25),
    return a dict of period -> conflicts.
    """
    period_conflicts = {}
    for p in range(1, max_period + 1):
        residues: Dict[int, int] = {}
        conflicts = 0
        for idx, k in stream_keys.items():
            rem = idx % p
            if rem in residues:
                if residues[rem] != k:
                    conflicts += 1
            else:
                residues[rem] = k
        period_conflicts[p] = conflicts
    return period_conflicts


def test_keyword_match(
    stream_keys: Dict[int, int],
    keyword: str,
    alphabet: str,
    cipher_type: str = "vigenere",
) -> Tuple[int, int, float]:
    """Test how many characters of stream_keys match a periodic keyword."""
    L = len(keyword)
    matches = 0
    total = len(stream_keys)
    if total == 0:
        return 0, 0, 0.0

    kw_indices = [alphabet.index(ch) for ch in keyword]

    for idx, req_k in stream_keys.items():
        exp_k = kw_indices[idx % L]
        if req_k == exp_k:
            matches += 1

    return matches, total, matches / total


def sweep_fixed_geometric_stencils() -> List[Dict[str, Any]]:
    """
    Evaluate deterministic geometric stencil masks:
    1. Checkerboard: (r + c) % 2
    2. Alternating rows: r % 2
    3. Alternating cols: c % 2
    4. Top half vs Bottom half: r < 7
    5. Left half vs Right half: c < 4
    """
    pairs = extract_known_pairs()
    hits = []

    stencils = {
        "checkerboard": lambda r, c: (r + c) % 2 == 0,
        "alt_rows": lambda r, c: r % 2 == 0,
        "alt_cols": lambda r, c: c % 2 == 0,
        "half_vertical": lambda r, c: r < 7,
        "half_horizontal": lambda r, c: c < 4,
    }

    alphabets = [("KRYPTOS", KRYPTOS_ALPHABET), ("STANDARD", STANDARD_ALPHABET)]

    for sten_name, sten_fn in stencils.items():
        for alph_name, alph in alphabets:
            # Partition pairs into Stream A and Stream B
            stream_a: Dict[int, int] = {}
            stream_b: Dict[int, int] = {}

            for idx, c, p in pairs:
                r = idx // GRID_COLS
                col = idx % GRID_COLS
                c_idx = alph.index(c)
                p_idx = alph.index(p)
                kv = (c_idx - p_idx) % 26

                if sten_fn(r, col):
                    stream_a[idx] = kv
                else:
                    stream_b[idx] = kv

            # Check periodic consistency on both streams
            conf_a = test_stream_period_consistency(stream_a)
            conf_b = test_stream_period_consistency(stream_b)

            # Check if any (period_a, period_b) has 0 conflicts on both
            for p_a, c_a in conf_a.items():
                for p_b, c_b in conf_b.items():
                    if c_a == 0 and c_b == 0 and len(stream_a) >= 4 and len(stream_b) >= 4:
                        hits.append({
                            "type": "fixed_stencil",
                            "stencil": sten_name,
                            "alphabet": alph_name,
                            "period_a": p_a,
                            "period_b": p_b,
                            "count_a": len(stream_a),
                            "count_b": len(stream_b),
                            "conflicts_a": c_a,
                            "conflicts_b": c_b,
                        })

            # Check historical keywords on both streams
            for kw in HISTORICAL_KEYWORDS:
                ma, ta, ra = test_keyword_match(stream_a, kw, alph)
                mb, tb, rb = test_keyword_match(stream_b, kw, alph)
                if ra >= 0.5 or rb >= 0.5:
                    hits.append({
                        "type": "keyword_match",
                        "stencil": sten_name,
                        "alphabet": alph_name,
                        "keyword": kw,
                        "stream_a_matches": f"{ma}/{ta} ({ra:.1%})",
                        "stream_b_matches": f"{mb}/{tb} ({rb:.1%})",
                    })

    return hits


def sweep_rotational_stencils(symmetry_mode: str = "rot180", max_samples: int = 50000) -> List[Dict[str, Any]]:
    """
    Exhaustively/heuristically sample 2-phase stencils under specified symmetry.
    In 14x7, there are 49 pairs of complementary cells.
    Crib cells touch a subset of these pairs (specifically 24 anchor cells across rows 3, 4, 9, 10).
    """
    pairs = extract_known_pairs()
    anchor_cells = {p[0]: p for p in pairs}

    sym_pairs = get_symmetry_pairs(symmetry_mode)
    # Filter to pairs that overlap with at least one anchor cell
    relevant_pairs = []
    for c1, c2 in sym_pairs:
        idx1 = c1[0] * GRID_COLS + c1[1]
        idx2 = c2[0] * GRID_COLS + c2[1]
        if idx1 in anchor_cells or idx2 in anchor_cells:
            relevant_pairs.append((c1, c2, idx1, idx2))

    num_relevant = len(relevant_pairs)
    hits = []

    # Since num_relevant <= 24, 2^num_relevant <= 16,777,216
    # We can evaluate all 2^num_relevant choices of (which cell is in Phase 1 vs Phase 2)
    # For small num_relevant, exhaustive enumeration is instantaneous!
    print(f"[{symmetry_mode}] Relevant symmetric pairs touching cribs: {num_relevant} (Search space: 2^{num_relevant} = {2**num_relevant:,} combinations)")

    for choice in itertools.product([0, 1], repeat=num_relevant):
        stream_a: Dict[int, int] = {}
        stream_b: Dict[int, int] = {}

        for bit, (c1, c2, idx1, idx2) in zip(choice, relevant_pairs):
            # If bit == 0: c1 in Phase 1 (Stream A), c2 in Phase 2 (Stream B)
            # If bit == 1: c1 in Phase 2 (Stream B), c2 in Phase 1 (Stream A)
            if idx1 in anchor_cells:
                c, p = anchor_cells[idx1][1], anchor_cells[idx1][2]
                kv = (KRYPTOS_ALPHABET.index(c) - KRYPTOS_ALPHABET.index(p)) % 26
                if bit == 0:
                    stream_a[idx1] = kv
                else:
                    stream_b[idx1] = kv

            if idx2 in anchor_cells:
                c, p = anchor_cells[idx2][1], anchor_cells[idx2][2]
                kv = (KRYPTOS_ALPHABET.index(c) - KRYPTOS_ALPHABET.index(p)) % 26
                if bit == 0:
                    stream_b[idx2] = kv
                else:
                    stream_a[idx2] = kv

        # Test if both streams have zero conflicts for short periods (1..7)
        if len(stream_a) >= 6 and len(stream_b) >= 6:
            conf_a = test_stream_period_consistency(stream_a, max_period=7)
            conf_b = test_stream_period_consistency(stream_b, max_period=7)

            for p_a in [1, 2, 3, 4, 5, 6, 7]:
                if conf_a[p_a] == 0:
                    for p_b in [1, 2, 3, 4, 5, 6, 7]:
                        if conf_b[p_b] == 0:
                            hits.append({
                                "symmetry": symmetry_mode,
                                "period_a": p_a,
                                "period_b": p_b,
                                "count_a": len(stream_a),
                                "count_b": len(stream_b),
                                "choice_bits": "".join(str(b) for b in choice),
                            })
                            if len(hits) >= 10:
                                return hits

    return hits


def run_cardan_stencil_campaign() -> Dict[str, Any]:
    """Execute complete Cardan stencil campaign across all symmetries and fixed patterns."""
    t0 = time.time()
    fixed_hits = sweep_fixed_geometric_stencils()

    rot180_hits = sweep_rotational_stencils("rot180")
    flip_v_hits = sweep_rotational_stencils("flip_v")
    flip_h_hits = sweep_rotational_stencils("flip_h")
    elapsed = time.time() - t0

    return {
        "execution_time_s": round(elapsed, 3),
        "fixed_stencil_hits": fixed_hits,
        "rot180_hits": rot180_hits,
        "flip_v_hits": flip_v_hits,
        "flip_h_hits": flip_h_hits,
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CIPHERLAB — TIER 2 CARDAN STENCIL MASK SWEEPER")
    print("=" * 70)

    res = run_cardan_stencil_campaign()

    print(f"\nCompleted in {res['execution_time_s']}s")
    print(f"Fixed Geometric Stencil Hits: {len(res['fixed_stencil_hits'])}")
    for h in res['fixed_stencil_hits']:
        print("  ->", h)

    print(f"\n180-deg Rotational Stencil Hits: {len(res['rot180_hits'])}")
    for h in res['rot180_hits'][:5]:
        print("  ->", h)

    print(f"\nVertical Flip Stencil Hits: {len(res['flip_v_hits'])}")
    for h in res['flip_v_hits'][:5]:
        print("  ->", h)

    print(f"\nHorizontal Flip Stencil Hits: {len(res['flip_h_hits'])}")
    for h in res['flip_h_hits'][:5]:
        print("  ->", h)
    print("=" * 70)
