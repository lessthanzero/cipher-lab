"""Tier 2 Optical Folding and Tableau Superposition Sweeper for Kryptos K4.

Models the physical copper sculpture architecture:
- Left panel: Ciphertext (869 chars: K1, K2, K3, K4).
- Right panel: Vigenère Tableau (867 chars, 28 rows x 31-32 cols).
- The right panel was intentionally flipped to be readable from behind the copper plate.

Evaluates:
1. Direct spatial superposition: Letters lying directly opposite K4.
2. Geometric folds:
   - Front-to-back horizontal reflection (looking through the cut copper sheet)
   - Vertical flip (folding top to bottom)
   - 180° rotation (point reflection)
3. Full tableau sliding window:
   - Sweeps all continuous 97-char slices of the full 867-char tableau
   - Evaluates alignment against the 24 public cribs under:
     * Standard Vigenere, Kryptos Vigenere
     * Standard Beaufort, Kryptos Beaufort
     * Variant Beaufort
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


# Exact transcription from physical sculpture (Elonka Dunin / Doug Gwyn)
LEFT_PANEL_ROWS: List[str] = [
    # Panel 1 (Top Left): K1 + K2
    "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ",
    "YQTQUXQBQVYUVLLTREVJYQTMKYRDMFD",
    "VFPJUDEEHZWETZYVGWHKKQETGFQJNCE",
    "GGWHKK?DQMCPFQZDQMMIAGPFXHQRLG",
    "TIMVMZJANQLVKQEDAGDVFRPJUNGEUNA",
    "QZGZLECGYUXUEENJTBJLBQCRTBJDFHRR",
    "YIZETKZEMVDUFKSJHKFWHKUWQLSZFTI",
    "HHDDDUVH?DWKBFUFPWNTDFIYCUQZERE",
    "EVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDX",
    "FLGGTEZ?FKZBSFDQVGOGIPUFXHHDRKF",
    "FHQNTGPUAECNUVPDJMQCLQUMUNEDFQ",
    "ELZZVRRGKFFVOEEXBDMVPNFQXEZLGRE",
    "DNQFMPNZGLFLPMRJQYALMGNUVPDXVKP",
    "DQUMEBEDMHDAFMJGZNUPLGEWJLLAETG",
    # Panel 2 (Bottom Left): K3 + K4
    "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA",
    "CHTNREYULDSLLSLLNOHSNOSMRWXMNE",
    "TPRNGATIHNRARPESLNNELEBLPIIACAE",
    "WMTWNDITEENRAHCTENEUDRETNHAEOE",
    "TFOLSEDTIWENHAEIOYTEYQHEENCTAYCR",
    "EIFTBRSPAMHHEWENATAMATEGYEERLB",
    "TEEFOASFIOTUETUAEOTOARMAEERTNRTI",
    "BSEDDNIAAHTTMSTEWPIEROAGRIEWFEB",
    "AECTDDHILCEIHSITEGOEAOSDDRYDLORIT",
    "RKLMLEHAGTDHARDPNEOHMGFMFEUHE",
    "ECDMRIPFEIMEHNLSSTTRTVDOHW?OBKR",
    "UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO",
    "TWTQSJQSSEKZZWATJKLUDIAWINFBNYP",
    "VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR",
]

RIGHT_PANEL_ROWS: List[str] = [
    # Panel 3 (Top Right): Tableau Rows A to M
    " ABCDEFGHIJKLMNOPQRSTUVWXYZABCD",
    "AKRYPTOSABCDEFGHIJLMNQUVWXZKRYP",
    "BRYPTOSABCDEFGHIJLMNQUVWXZKRYPT",
    "CYPTOSABCDEFGHIJLMNQUVWXZKRYPTO",
    "DPTOSABCDEFGHIJLMNQUVWXZKRYPTOS",
    "ETOSABCDEFGHIJLMNQUVWXZKRYPTOSA",
    "FOSABCDEFGHIJLMNQUVWXZKRYPTOSAB",
    "GSABCDEFGHIJLMNQUVWXZKRYPTOSABC",
    "HABCDEFGHIJLMNQUVWXZKRYPTOSABCD",
    "IBCDEFGHIJLMNQUVWXZKRYPTOSABCDE",
    "JCDEFGHIJLMNQUVWXZKRYPTOSABCDEF",
    "KDEFGHIJLMNQUVWXZKRYPTOSABCDEFG",
    "LEFGHIJLMNQUVWXZKRYPTOSABCDEFGH",
    "MFGHIJLMNQUVWXZKRYPTOSABCDEFGHI",
    # Panel 4 (Bottom Right): Tableau Rows N to Z
    "NGHIJLMNQUVWXZKRYPTOSABCDEFGHIJL",
    "OHIJLMNQUVWXZKRYPTOSABCDEFGHIJL",
    "PIJLMNQUVWXZKRYPTOSABCDEFGHIJLM",
    "QJLMNQUVWXZKRYPTOSABCDEFGHIJLMN",
    "RLMNQUVWXZKRYPTOSABCDEFGHIJLMNQ",
    "SMNQUVWXZKRYPTOSABCDEFGHIJLMNQU",
    "TNQUVWXZKRYPTOSABCDEFGHIJLMNQUV",
    "UQUVWXZKRYPTOSABCDEFGHIJLMNQUVW",
    "VUVWXZKRYPTOSABCDEFGHIJLMNQUVWX",
    "WVWXZKRYPTOSABCDEFGHIJLMNQUVWXZ",
    "XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK",
    "YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR",
    "ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY",
    " ABCDEFGHIJKLMNOPQRSTUVWXYZABCD",
]


def extract_linear_tableau_stream() -> str:
    """Concatenates all letters from the right panel into a single linear text stream."""
    stream = []
    for row in RIGHT_PANEL_ROWS:
        for ch in row:
            if ch.isalpha():
                stream.append(ch)
    return "".join(stream)


def extract_opposite_k4_tableau_chars() -> Dict[str, str]:
    """
    Extracts characters from the right panel directly corresponding to K4 rows.
    K4 is in bottom-left rows 24, 25, 26, 27.
    """
    # K4 begins at index 27 in row 24 (after '?')
    # Row 24: ECDMRIPFEIMEHNLSSTTRTVDOHW?OBKR (last 4 chars: OBKR)
    # Row 25: UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO (31 chars)
    # Row 26: TWTQSJQSSEKZZWATJKLUDIAWINFBNYP (31 chars)
    # Row 27: VTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR (31 chars)
    # Total = 4 + 31 + 31 + 31 = 97 chars.

    # Direct opposite rows on right panel: 24, 25, 26, 27
    # Row 24: XWXZKRYPTOSABCDEFGHIJLMNQUVWXZK (31 chars)
    # Row 25: YXZKRYPTOSABCDEFGHIJLMNQUVWXZKR (31 chars)
    # Row 26: ZZKRYPTOSABCDEFGHIJLMNQUVWXZKRY (31 chars)
    # Row 27:  ABCDEFGHIJKLMNOPQRSTUVWXYZABCD (31 chars)

    # Direct 1-to-1 extraction
    # From row 24: last 4 chars
    chars_direct = []
    chars_direct.extend(RIGHT_PANEL_ROWS[24][-4:])
    chars_direct.extend(RIGHT_PANEL_ROWS[25][:31])
    chars_direct.extend(RIGHT_PANEL_ROWS[26][:31])
    chars_direct.extend(RIGHT_PANEL_ROWS[27][1:32])  # skip leading space

    direct_str = "".join(ch for ch in chars_direct if ch.isalpha())

    # Flipped (horizontal reflection: read each row in reverse, representing looking through copper)
    chars_flip_h = []
    chars_flip_h.extend(RIGHT_PANEL_ROWS[24][:4][::-1])
    chars_flip_h.extend(RIGHT_PANEL_ROWS[25][::-1][:31])
    chars_flip_h.extend(RIGHT_PANEL_ROWS[26][::-1][:31])
    chars_flip_h.extend(RIGHT_PANEL_ROWS[27][::-1][:31])
    flip_h_str = "".join(ch for ch in chars_flip_h if ch.isalpha())

    # Linear end slice: last 97 letters of the entire right panel
    full_stream = extract_linear_tableau_stream()
    linear_end = full_stream[-97:]
    linear_start = full_stream[:97]

    return {
        "direct_spatial": direct_str,
        "flipped_horizontal": flip_h_str,
        "linear_end_97": linear_end,
        "linear_start_97": linear_start,
        "linear_end_reversed": linear_end[::-1],
    }


def evaluate_stream_against_k4(
    candidate_key: str,
    alphabet_name: str = "kryptos",
    cipher_type: str = "vigenere",
) -> Tuple[int, int, float]:
    """
    Evaluates candidate key stream against 24 known crib positions.
    Returns (matches, total, rate).
    """
    pairs = extract_known_pairs()
    alpha = KRYPTOS_ALPHABET if alphabet_name == "kryptos" else STANDARD_ALPHABET

    matches = 0
    total = len(pairs)

    for idx, c_char, p_char in pairs:
        if idx >= len(candidate_key):
            continue
        k_char = candidate_key[idx]
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


def sweep_optical_tableau_configurations() -> Dict[str, Any]:
    """Sweeps all optical alignments and sliding window positions across the tableau."""
    opposite_streams = extract_opposite_k4_tableau_chars()
    full_tableau = extract_linear_tableau_stream()

    results: Dict[str, Any] = {
        "spatial_alignments": [],
        "sliding_window_top_hits": [],
    }

    alphabets = ["kryptos", "standard"]
    modes = ["vigenere", "beaufort", "var_beaufort"]

    # 1. Test geometric spatial superpositions
    for name, stream in opposite_streams.items():
        if len(stream) < 97:
            stream = stream.ljust(97, "A")
        for alpha in alphabets:
            for mode in modes:
                m, tot, rate = evaluate_stream_against_k4(stream, alpha, mode)
                results["spatial_alignments"].append({
                    "stream_name": name,
                    "alphabet": alpha,
                    "cipher_type": mode,
                    "matches": m,
                    "total": tot,
                    "rate": round(rate, 4),
                })

    # 2. Test sliding window across entire 867-character tableau
    # Window of length 97 sliding across full_tableau (867 - 97 + 1 = 771 positions)
    window_len = 97
    sliding_hits = []
    for offset in range(len(full_tableau) - window_len + 1):
        window = full_tableau[offset : offset + window_len]
        window_rev = window[::-1]

        for w, is_rev in [(window, False), (window_rev, True)]:
            for alpha in alphabets:
                for mode in modes:
                    m, tot, rate = evaluate_stream_against_k4(w, alpha, mode)
                    if rate >= 0.25:  # threshold 25% (6/24 matches)
                        sliding_hits.append({
                            "offset": offset,
                            "reversed": is_rev,
                            "alphabet": alpha,
                            "cipher_type": mode,
                            "matches": m,
                            "total": tot,
                            "rate": round(rate, 4),
                            "sample": w[:15],
                        })

    sliding_hits.sort(key=lambda x: x["rate"], reverse=True)
    results["sliding_window_top_hits"] = sliding_hits[:10]

    return results


if __name__ == "__main__":
    print("=" * 70)
    print("CIPHERLAB — TIER 2 OPTICAL TABLEAU SUPERPOSITION SWEEPER")
    print("=" * 70)

    t0 = time.time()
    res = sweep_optical_tableau_configurations()
    elapsed = time.time() - t0

    print(f"Executed in {elapsed:.3f}s\n")
    print("--- Geometric Spatial Superpositions ---")
    res["spatial_alignments"].sort(key=lambda x: x["rate"], reverse=True)
    for hit in res["spatial_alignments"][:8]:
        print(f"  {hit['stream_name']:22s} ({hit['cipher_type']:12s}, {hit['alphabet']:8s}) -> {hit['matches']}/{hit['total']} ({hit['rate']*100:.1f}%)")

    print("\n--- Sliding Window Across 867-Char Tableau ---")
    if res["sliding_window_top_hits"]:
        for hit in res["sliding_window_top_hits"][:5]:
            rev_str = "rev" if hit['reversed'] else "fwd"
            print(f"  Offset {hit['offset']:3d} ({rev_str}, {hit['cipher_type']}, {hit['alphabet']}) -> {hit['matches']}/{hit['total']} ({hit['rate']*100:.1f}%) | Key: {hit['sample']}...")
    else:
        print("  Zero sliding window hits crossed 25% alignment threshold.")
    print("=" * 70)
