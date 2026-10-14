"""Tier 2 Dual-Panel Asymmetric Key Sweeper for Kryptos K4.

Evaluates the Two-Panel (Square A + Square B) architecture:
- Panel A: 49 cells (7x7), containing Crib 1 tail (THEAST, 6 chars) and Crib 2 tail (LOCK, 4 chars). Total: 10 anchors.
- Panel B: 48 cells (7x7 minus 1), containing Crib 1 head (EASTNOR, 7 chars) and Crib 2 head (BERLINC, 7 chars). Total: 14 anchors.

Sweeps:
1. Independent keyword pairs (K_A, K_B) across candidate historical keywords and dictionaries.
2. Read directions: Row-major and Column-major.
3. Cipher variants: Standard Vigenere, Kryptos Vigenere, Standard Beaufort, Kryptos Beaufort.
4. Identifies candidates matching >= 50% on either panel, and flags any candidate matching 100%.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.manifests import BLIND_PATH, CONTEXTUAL_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


HISTORICAL_KEYWORDS: List[str] = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT",
    "BERLIN", "CLOCK", "NORTHEAST", "EASTNORTHEAST", "BERLINCLOCK",
    "TITUS", "CARTER", "TOMB", "EGYPT", "LANGLEY", "VIRGINIA",
    "COPPER", "MATRIX", "SHADOW", "ILLUSION", "IQLUSION", "LIGHT",
    "MEDUSA", "DEFECTOR", "AGENCY", "INTELLIGENCE", "HEADQUARTERS",
    "DISCOVERY", "CANANYONESEETHE", "WHOKNOWSTHETRUTH", "SLOWLYDESPARATLY",
    "UNDERGROUND", "UNDERGRUUND", "IDBYROWS", "COMPASS", "WELTZEITUHR",
    "OCTOBER", "NOVEMBER", "COLDWAR", "WALL", "CHECKPOINT", "CHARLIE",
    "FREEDOM", "MONUMENT", "SCULPTURE", "CENTRAL", "SECRECY", "CIPHER",
]


def load_panel_anchor_datasets() -> Dict[str, Dict[str, Dict[int, Tuple[str, str]]]]:
    """
    Returns anchor mappings for Panel A (0..48) and Panel B (0..47).
    Positions are given in:
    1. 'row_major': r * 7 + c
    2. 'col_major': c * 7 + r
    """
    pairs = extract_known_pairs()

    datasets: Dict[str, Dict[str, Dict[int, Tuple[str, str]]]] = {
        "panel_a": {"row_major": {}, "col_major": {}},
        "panel_b": {"row_major": {}, "col_major": {}},
    }

    for idx, c, p in pairs:
        r = idx // 14
        col = idx % 14

        if col < 7:  # Panel A
            r_idx = r * 7 + col
            c_idx = col * 7 + r
            datasets["panel_a"]["row_major"][r_idx] = (c, p)
            datasets["panel_a"]["col_major"][c_idx] = (c, p)
        else:  # Panel B
            local_col = col - 7
            r_idx = r * 7 + local_col
            c_idx = local_col * 7 + r
            datasets["panel_b"]["row_major"][r_idx] = (c, p)
            datasets["panel_b"]["col_major"][c_idx] = (c, p)

    return datasets


def evaluate_keyword_on_panel(
    keyword: str,
    anchors: Dict[int, Tuple[str, str]],
    alphabet_name: str,
    cipher_type: str,
) -> Tuple[int, int, float]:
    """
    Evaluates keyword alignment against a panel's anchor positions.
    Returns (matches, total, match_rate).
    """
    alpha = KRYPTOS_ALPHABET if alphabet_name == "kryptos" else STANDARD_ALPHABET
    kw = keyword.upper()
    kw_len = len(kw)
    if kw_len == 0 or len(anchors) == 0:
        return 0, 0, 0.0

    matches = 0
    total = len(anchors)

    for pos, (c_char, p_char) in anchors.items():
        k_char = kw[pos % kw_len]
        if k_char not in alpha:
            continue

        c_val = alpha.index(c_char)
        p_val = alpha.index(p_char)
        k_val = alpha.index(k_char)

        if cipher_type == "vigenere":
            expected = (p_val + k_val) % 26
        elif cipher_type == "beaufort":
            expected = (k_val - p_val) % 26
        elif cipher_type == "var_beaufort":
            expected = (p_val - k_val) % 26
        else:
            continue

        if c_val == expected:
            matches += 1

    return matches, total, matches / total if total > 0 else 0.0


def sweep_dual_panel_keywords(
    keywords: Optional[List[str]] = None,
    threshold: float = 0.40,
) -> Dict[str, Any]:
    """
    Sweeps keyword candidates across Panel A and Panel B independently.
    """
    if keywords is None:
        keywords = HISTORICAL_KEYWORDS

    panel_data = load_panel_anchor_datasets()
    results: Dict[str, Any] = {
        "panel_a_candidates": [],
        "panel_b_candidates": [],
        "exact_matches": [],
    }

    alphabets = ["kryptos", "standard"]
    cipher_modes = ["vigenere", "beaufort", "var_beaufort"]
    read_orders = ["row_major", "col_major"]

    for kw in keywords:
        for p_name in ["panel_a", "panel_b"]:
            for alpha in alphabets:
                for cm in cipher_modes:
                    for ro in read_orders:
                        anchors = panel_data[p_name][ro]
                        m, tot, rate = evaluate_keyword_on_panel(kw, anchors, alpha, cm)

                        if rate >= threshold:
                            entry = {
                                "panel": p_name,
                                "keyword": kw,
                                "read_order": ro,
                                "alphabet": alpha,
                                "cipher_type": cm,
                                "matches": m,
                                "total": tot,
                                "rate": round(rate, 4),
                            }
                            if p_name == "panel_a":
                                results["panel_a_candidates"].append(entry)
                            else:
                                results["panel_b_candidates"].append(entry)

                            if rate == 1.0:
                                results["exact_matches"].append(entry)

    # Sort descending by match rate
    results["panel_a_candidates"].sort(key=lambda x: x["rate"], reverse=True)
    results["panel_b_candidates"].sort(key=lambda x: x["rate"], reverse=True)

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dual-Panel Asymmetric Key Sweeper")
    parser.add_argument("--threshold", type=float, default=0.35, help="Match rate threshold to report")
    args = parser.parse_args()

    print("=" * 70)
    print("CIPHERLAB — TIER 2 DUAL-PANEL ASYMMETRIC KEY SWEEPER")
    print(f"Testing {len(HISTORICAL_KEYWORDS)} historical keywords across Panel A and Panel B")
    print("=" * 70)

    t0 = time.time()
    res = sweep_dual_panel_keywords(threshold=args.threshold)
    elapsed = time.time() - t0

    print(f"Executed in {elapsed:.3f}s\n")
    print(f"Panel A candidates (>= {args.threshold*100:.0f}%): {len(res['panel_a_candidates'])}")
    for c in res["panel_a_candidates"][:5]:
        print(f"  [Panel A] {c['keyword']:15s} ({c['cipher_type']}, {c['alphabet']}, {c['read_order']}) -> {c['matches']}/{c['total']} ({c['rate']*100:.1f}%)")

    print(f"\nPanel B candidates (>= {args.threshold*100:.0f}%): {len(res['panel_b_candidates'])}")
    for c in res["panel_b_candidates"][:5]:
        print(f"  [Panel B] {c['keyword']:15s} ({c['cipher_type']}, {c['alphabet']}, {c['read_order']}) -> {c['matches']}/{c['total']} ({c['rate']*100:.1f}%)")

    print(f"\nExact (100%) Matches: {len(res['exact_matches'])}")
    for em in res["exact_matches"]:
        print(f"  *** EXACT MATCH *** {em}")
    print("=" * 70)
