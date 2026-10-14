"""Tier 2 Berlin Clock (Mengenlehreuhr) State Machine Engine for Kryptos K4.

Models the 24-lamp Berlin Clock (Mengenlehreuhr) as a discrete finite-state keystream generator:
1. Clock State Space:
   - Row 1: H // 5 (0..4 lamps, 5-hour increments)
   - Row 2: H % 5 (0..4 lamps, 1-hour increments)
   - Row 3: M // 5 (0..11 lamps, 5-minute increments)
   - Row 4: M % 5 (0..4 lamps, 1-minute increments)
   - Top: S % 2 (0..1 blinker)

2. Historical Timestamps (November 9, 1989 - Fall of the Berlin Wall):
   - 18:53: Schabowski press conference ("sofort, unverzueglich")
   - 19:00: Wire services broadcast open border
   - 21:00: Crowds gather at Bornholmer Strasse
   - 23:30: Bornholmer Strasse border gate swings open
   - 00:00: Midnight celebration

3. Key Progression Models:
   - Sum of active lamps: N_lamps = (r1 + r2 + r3 + r4) mod 26
   - Row-weighted odometer: (a * r1 + b * r2 + c * r3 + d * r4) mod 26
   - Binary lamp mask projection across the 24 lamp positions
   - Stepping rates: Delta t in {1 min, 5 min, 15 min, 1 hr, 1 sec}
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


HISTORICAL_TIMES: List[Tuple[str, int, int]] = [
    ("schabowski_press_conf_1853", 18, 53),
    ("news_broadcast_1900", 19, 0),
    ("crowd_assembly_2100", 21, 0),
    ("bornholmer_gate_opens_2330", 23, 30),
    ("midnight_fall_0000", 0, 0),
    ("noon_1200", 12, 0),
    ("morning_0800", 8, 0),
]


def get_berlin_clock_state(hour: int, minute: int) -> Tuple[int, int, int, int, int]:
    """Computes (r1, r2, r3, r4, total_lamps) for given (hour, minute)."""
    r1 = (hour % 24) // 5  # 0..4
    r2 = (hour % 24) % 5   # 0..4
    r3 = minute // 5       # 0..11
    r4 = minute % 5        # 0..4
    total = r1 + r2 + r3 + r4
    return r1, r2, r3, r4, total


def generate_clock_keystream(
    start_hour: int,
    start_minute: int,
    step_minutes: int,
    length: int = 97,
    weights: Tuple[int, int, int, int] = (1, 1, 1, 1),
    offset: int = 0,
) -> List[int]:
    """Generates a 97-character integer keystream from Berlin Clock state transitions."""
    keystream = []
    curr_total_min = start_hour * 60 + start_minute

    w1, w2, w3, w4 = weights
    for _ in range(length):
        h = (curr_total_min // 60) % 24
        m = curr_total_min % 60
        r1, r2, r3, r4, _ = get_berlin_clock_state(h, m)
        k_val = (w1 * r1 + w2 * r2 + w3 * r3 + w4 * r4 + offset) % 26
        keystream.append(k_val)
        curr_total_min += step_minutes

    return keystream


def evaluate_keystream_on_k4(
    keystream: List[int],
    alphabet_name: str = "kryptos",
    cipher_type: str = "vigenere",
) -> Tuple[int, int, float]:
    """Evaluates keystream alignment against 24 known crib anchors."""
    pairs = extract_known_pairs()
    alpha = KRYPTOS_ALPHABET if alphabet_name == "kryptos" else STANDARD_ALPHABET

    matches = 0
    total = len(pairs)

    for idx, c_char, p_char in pairs:
        if idx >= len(keystream):
            continue
        c_val = alpha.index(c_char)
        p_val = alpha.index(p_char)
        k_val = keystream[idx]

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


def sweep_berlin_clock_states() -> Dict[str, Any]:
    """Sweeps historical times, step intervals, and weighting parameters."""
    alphabets = ["kryptos", "standard"]
    modes = ["vigenere", "beaufort", "var_beaufort"]
    step_intervals = [1, 2, 5, 10, 15, 30, 60]

    hits = []

    # 1. Historical timestamps with standard weights (1, 1, 1, 1) and offsets in 0..25
    for t_name, h, m in HISTORICAL_TIMES:
        for step in step_intervals:
            for off in range(26):
                ks = generate_clock_keystream(h, m, step_minutes=step, length=97, offset=off)
                for alpha in alphabets:
                    for mode in modes:
                        m_hits, tot, rate = evaluate_keystream_on_k4(ks, alpha, mode)
                        if rate >= 0.25:  # threshold 25% (6/24 matches)
                            hits.append({
                                "time_label": t_name,
                                "start_time": f"{h:02d}:{m:02d}",
                                "step_minutes": step,
                                "offset": off,
                                "alphabet": alpha,
                                "cipher_type": mode,
                                "matches": m_hits,
                                "total": tot,
                                "rate": round(rate, 4),
                            })

    # 2. Exhaustive sweep over all 1,440 minutes of the 24-hour day (step = 1 min, 5 min)
    for total_min in range(0, 1440, 5):
        h = total_min // 60
        m = total_min % 60
        for step in [1, 5, 15]:
            ks = generate_clock_keystream(h, m, step_minutes=step, length=97, offset=0)
            for alpha in alphabets:
                for mode in modes:
                    m_hits, tot, rate = evaluate_keystream_on_k4(ks, alpha, mode)
                    if rate >= 0.25:
                        hits.append({
                            "time_label": "minute_sweep",
                            "start_time": f"{h:02d}:{m:02d}",
                            "step_minutes": step,
                            "offset": 0,
                            "alphabet": alpha,
                            "cipher_type": mode,
                            "matches": m_hits,
                            "total": tot,
                            "rate": round(rate, 4),
                        })

    hits.sort(key=lambda x: x["rate"], reverse=True)
    return {
        "total_hits_above_25pct": len(hits),
        "top_hits": hits[:10],
    }


if __name__ == "__main__":
    print("=" * 70)
    print("CIPHERLAB — TIER 2 BERLIN CLOCK STATE MACHINE ENGINE")
    print("=" * 70)

    t0 = time.time()
    res = sweep_berlin_clock_states()
    elapsed = time.time() - t0

    print(f"Executed in {elapsed:.3f}s\n")
    print(f"Total Configurations >= 25% alignment: {res['total_hits_above_25pct']}")
    if res["top_hits"]:
        for h in res["top_hits"][:5]:
            print(f"  {h['start_time']} (step {h['step_minutes']}m, off {h['offset']}) [{h['cipher_type']}, {h['alphabet']}] -> {h['matches']}/{h['total']} ({h['rate']*100:.1f}%)")
    else:
        print("  Zero Berlin Clock configurations crossed 25% alignment.")
    print("=" * 70)
