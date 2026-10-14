"""Tier 2 Compass Bearings and Weltzeituhr Projection Sweeper for Kryptos K4.

Evaluates mathematical key schedules driven by the Alexanderplatz Weltzeituhr
and compass rose geometry:

1. Compass Rose Geometry:
   - 16 points of the compass:
     N (0), NNE (1), NE (2), ENE (3), E (4), ESE (5), SE (6), SSE (7),
     S (8), SSW (9), SW (10), WSW (11), W (12), WNW (13), NW (14), NNW (15).
   - Crib 1 is 'EASTNORTHEAST' (ENE = Point 3, 67.5 deg).
   - Modular compass angle progressions: Delta theta in {11.25, 22.5, 45, 67.5, 90, 180} degrees.

2. Weltzeituhr 24-Cylinder Projections:
   - 24 time zone facets (columns 0..23).
   - Rotational hour progression: hour = (h0 + t) % 24.
   - Cylinder readout in a 4x24 grid (96 chars) + 1 trailing char.
   - Cities of the Weltzeituhr as key words:
     BERLIN, MOSCOW, LONDON, PARIS, TOKYO, SYDNEY, NEWYORK, HAVANA, CAIRO,
     BAGHDAD, TEHRAN, BEIJING, HONGKONG, RANGOON, HONOLULU, ANCHORAGE,
     SANTIAGO, DAKAR, REYKJAVIK, GENEVA, PRAGUE, WARSAW, BUDAPEST, BUCHAREST.

3. Testing:
   Evaluates each candidate key schedule against the 24 confirmed K4 crib characters.
"""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.manifests import CONTEXTUAL_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


COMPASS_16_POINTS = [
    "NORTH", "NORTHNORTHEAST", "NORTHEAST", "EASTNORTHEAST",
    "EAST", "EASTSOUTHEAST", "SOUTHEAST", "SOUTHSOUTHEAST",
    "SOUTH", "SOUTHSOUTHWEST", "SOUTHWEST", "WESTSOUTHWEST",
    "WEST", "WESTNORTHWEST", "NORTHWEST", "NORTHNORTHWEST",
]

COMPASS_ABBREV_16 = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]

WELTZEITUHR_CITIES = [
    "BERLIN", "MOSCOW", "LONDON", "PARIS", "TOKYO", "SYDNEY", "NEWYORK",
    "HAVANA", "CAIRO", "BAGHDAD", "TEHRAN", "BEIJING", "HONGKONG", "RANGOON",
    "HONOLULU", "ANCHORAGE", "SANTIAGO", "DAKAR", "REYKJAVIK", "GENEVA",
    "PRAGUE", "WARSAW", "BUDAPEST", "BUCHAREST", "ALEXANDERPLATZ", "WELTZEITUHR",
]


def evaluate_key_sequence(
    keystream: List[int],
    anchor_pairs: List[Tuple[int, str, str]],
    alphabet: str,
    cipher_type: str = "vigenere",
) -> Tuple[int, int, float]:
    """Test match count of a numeric keystream (0..25) against anchor pairs."""
    matches = 0
    total = len(anchor_pairs)

    for idx, c, p in anchor_pairs:
        if idx >= len(keystream):
            continue
        c_val = alphabet.index(c)
        p_val = alphabet.index(p)
        k_val = keystream[idx] % 26

        if cipher_type == "vigenere":
            exp_c = (p_val + k_val) % 26
        elif cipher_type == "beaufort":
            exp_c = (k_val - p_val) % 26
        else:
            exp_c = (p_val - k_val) % 26

        if exp_c == c_val:
            matches += 1

    return matches, total, matches / total


def sweep_compass_bearings() -> List[Dict[str, Any]]:
    """Sweep linear and progressive compass angle schedules."""
    anchors = extract_known_pairs()
    hits = []

    alphabets = [("KRYPTOS", KRYPTOS_ALPHABET), ("STANDARD", STANDARD_ALPHABET)]
    cipher_types = ["vigenere", "beaufort", "variant_beaufort"]

    # 1. 16-point compass progression: step in 0..15, initial in 0..15
    for alph_name, alph in alphabets:
        for c_type in cipher_types:
            for init_pt in range(16):
                for step in range(16):
                    # Key at position i is point (init_pt + i * step) % 16
                    # Mapped to shift = (pt * 26 // 16) or pt % 26
                    for map_mode in ["direct_mod", "scaled_26"]:
                        if map_mode == "direct_mod":
                            kstream = [(init_pt + i * step) % 16 for i in range(97)]
                        else:
                            kstream = [int(round((init_pt + i * step) % 16 * 26.0 / 16.0)) % 26 for i in range(97)]

                        m, t, r = evaluate_key_sequence(kstream, anchors, alph, c_type)
                        if r >= 0.25:
                            hits.append({
                                "type": "compass_bearing_progression",
                                "alphabet": alph_name,
                                "cipher_type": c_type,
                                "init_point": COMPASS_ABBREV_16[init_pt],
                                "step": step,
                                "map_mode": map_mode,
                                "matches": m,
                                "match_rate": round(r, 4),
                            })

    return hits


def sweep_weltzeituhr_cities() -> List[Dict[str, Any]]:
    """Sweep Weltzeituhr city names and concatenations as periodic or chained keys."""
    anchors = extract_known_pairs()
    hits = []

    alphabets = [("KRYPTOS", KRYPTOS_ALPHABET), ("STANDARD", STANDARD_ALPHABET)]
    cipher_types = ["vigenere", "beaufort", "variant_beaufort"]

    for city in WELTZEITUHR_CITIES:
        L = len(city)
        for alph_name, alph in alphabets:
            for c_type in cipher_types:
                # Direct periodic city key
                kstream = [alph.index(city[i % L]) for i in range(97)]
                m, t, r = evaluate_key_sequence(kstream, anchors, alph, c_type)
                if r >= 0.25:
                    hits.append({
                        "type": "city_periodic_key",
                        "city": city,
                        "alphabet": alph_name,
                        "cipher_type": c_type,
                        "matches": m,
                        "match_rate": round(r, 4),
                    })

    return hits


def sweep_24_cylinder_projections() -> List[Dict[str, Any]]:
    """Sweep 24-column cylinder rotations: K[r, c] in a 4x24 grid."""
    anchors = extract_known_pairs()
    hits = []

    alphabets = [("KRYPTOS", KRYPTOS_ALPHABET), ("STANDARD", STANDARD_ALPHABET)]
    cipher_types = ["vigenere", "beaufort"]

    # In a 4x24 grid: col in 0..23, row in 0..3
    # If the cylinder rotates by Delta per row: col_eff = (col + r * delta) % 24
    for delta in range(24):
        for h0 in range(24):
            for alph_name, alph in alphabets:
                for c_type in cipher_types:
                    kstream = []
                    for i in range(97):
                        r = i // 24
                        c = i % 24
                        col_eff = (h0 + c + r * delta) % 24
                        # map 0..23 to 0..25 shift
                        kstream.append(col_eff)

                    m, t, r = evaluate_key_sequence(kstream, anchors, alph, c_type)
                    if r >= 0.25:
                        hits.append({
                            "type": "24_cylinder_rotation",
                            "delta_per_row": delta,
                            "h0": h0,
                            "alphabet": alph_name,
                            "cipher_type": c_type,
                            "matches": m,
                            "match_rate": round(r, 4),
                        })

    return hits


def run_compass_weltzeituhr_campaign() -> Dict[str, Any]:
    """Execute complete compass and Weltzeituhr campaign."""
    compass_hits = sweep_compass_bearings()
    city_hits = sweep_weltzeituhr_cities()
    cyl_hits = sweep_24_cylinder_projections()

    all_hits = compass_hits + city_hits + cyl_hits
    all_hits.sort(key=lambda x: x["match_rate"], reverse=True)

    return {
        "total_hits_above_25pct": len(all_hits),
        "best_hits": all_hits[:10],
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CIPHERLAB — TIER 2 COMPASS & WELTZEITUHR GEOMETRIC SWEEPER")
    print("=" * 70)

    res = run_compass_weltzeituhr_campaign()
    print(f"\nTotal Candidates Crossing 25% Threshold: {res['total_hits_above_25pct']}")
    if res["best_hits"]:
        for h in res["best_hits"][:10]:
            print("  ->", h)
    else:
        print("  -> Zero candidates crossed the 25% alignment threshold.")
    print("=" * 70)
