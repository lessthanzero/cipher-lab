"""Historical Running Key Corpus Sweeper for Kryptos K4.

Sweeps historical texts (Carter Tutankhamun diary, Reagan Berlin Wall speech,
K1-K3 plaintexts, CIA charter) against the 24 fixed anchor cells in both:
1. Direct linear running key: K[i] = Corpus[offset + i]
2. 14x7 Columnar transposed running key: K[r, c] = Corpus[offset + c * 14 + r]
3. 14x7 Row-wise running key: K[r, c] = Corpus[offset + r * 7 + c]

Operates under:
- Standard Vigenere
- Beaufort
- Kryptos Tableau Vigenere (Quagmire III)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence

from projects.kryptos.manifests import BLIND_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


CORPORA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "corpora" / "kryptos_historical"


def clean_corpus_text(raw_text: str) -> str:
    """Strip all non-alphabetic characters and convert to uppercase."""
    return re.sub(r"[^A-Z]", "", raw_text.upper())


def load_all_historical_corpora() -> Dict[str, str]:
    """Load and clean all historical text files."""
    corpora = {}
    if not CORPORA_DIR.exists():
        return corpora
    for path in sorted(CORPORA_DIR.glob("*.txt")):
        with open(path, "r", encoding="utf-8") as f:
            clean = clean_corpus_text(f.read())
            if clean:
                corpora[path.stem] = clean
    return corpora


def evaluate_running_key_offset(
    corpus: str,
    offset: int,
    anchor_pairs: List[Tuple[int, str, str]],
    alphabet: str = STANDARD_ALPHABET,
    cipher_type: str = "vigenere",
    grid_mode: str = "linear",
) -> Tuple[int, int, float]:
    """
    Evaluate match count at given offset.
    Returns (matches, total_tested, match_rate).
    """
    m = len(alphabet)
    matches = 0
    total = len(anchor_pairs)

    for idx, c, p in anchor_pairs:
        # Determine index in running key
        if grid_mode == "linear":
            k_pos = offset + idx
        elif grid_mode == "col_major_14x7":
            r = idx // 7
            col = idx % 7
            k_pos = offset + (col * 14 + r)
        elif grid_mode == "row_major_14x7":
            k_pos = offset + idx
        else:
            k_pos = offset + idx

        if k_pos >= len(corpus):
            return 0, total, 0.0

        key_char = corpus[k_pos]
        c_val = alphabet.index(c)
        p_val = alphabet.index(p)
        k_val = alphabet.index(key_char)

        if cipher_type == "vigenere":
            expected_c = (p_val + k_val) % m
        elif cipher_type == "beaufort":
            expected_c = (k_val - p_val) % m
        else:
            expected_c = (p_val + k_val) % m

        if expected_c == c_val:
            matches += 1

    match_rate = matches / total if total > 0 else 0.0
    return matches, total, match_rate


def sweep_corpus(
    corpus_name: str,
    corpus: str,
    anchor_pairs: List[Tuple[int, str, str]],
    threshold_rate: float = 0.35,
) -> List[Dict[str, Any]]:
    """Sweep a corpus across all offsets and modes."""
    hits = []
    max_offset = len(corpus) - 97
    if max_offset <= 0:
        return hits

    configs = [
        ("vigenere_std", STANDARD_ALPHABET, "vigenere", "linear"),
        ("beaufort_std", STANDARD_ALPHABET, "beaufort", "linear"),
        ("vigenere_kryptos", KRYPTOS_ALPHABET, "vigenere", "linear"),
        ("vigenere_std_col14x7", STANDARD_ALPHABET, "vigenere", "col_major_14x7"),
        ("vigenere_kryptos_col14x7", KRYPTOS_ALPHABET, "vigenere", "col_major_14x7"),
    ]

    for cfg_name, alph, c_type, g_mode in configs:
        for off in range(max_offset):
            matches, total, rate = evaluate_running_key_offset(
                corpus=corpus,
                offset=off,
                anchor_pairs=anchor_pairs,
                alphabet=alph,
                cipher_type=c_type,
                grid_mode=g_mode,
            )
            if rate >= threshold_rate:
                hits.append({
                    "corpus": corpus_name,
                    "config": cfg_name,
                    "offset": off,
                    "matches": matches,
                    "total_anchors": total,
                    "match_rate": round(rate, 4),
                    "key_sample": corpus[off:off + 25],
                })

    return hits


def run_full_running_key_campaign(threshold_rate: float = 0.35) -> Dict[str, Any]:
    """Execute complete historical running key campaign across all corpora."""
    corpora = load_all_historical_corpora()
    anchors = extract_known_pairs()

    all_hits = []
    stats = {}
    for name, text in corpora.items():
        hits = sweep_corpus(name, text, anchors, threshold_rate=threshold_rate)
        all_hits.extend(hits)
        stats[name] = {"length": len(text), "hits": len(hits)}

    # Sort hits by match rate descending
    all_hits.sort(key=lambda x: x["match_rate"], reverse=True)

    return {
        "corpora_evaluated": stats,
        "total_hits": len(all_hits),
        "best_hits": all_hits[:10],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.25, help="Match rate threshold")
    args = parser.parse_args()

    results = run_full_running_key_campaign(threshold_rate=args.threshold)
    print("=" * 70)
    print("CIPHERLAB — HISTORICAL RUNNING KEY SWEEP SUMMARY")
    print("=" * 70)
    for cname, cinfo in results["corpora_evaluated"].items():
        print(f"Corpus: {cname:<35} | Length: {cinfo['length']:5d} chars | Hits: {cinfo['hits']}")
    print(f"\nTotal Candidate Hits (rate >= {args.threshold*100:.0f}%): {results['total_hits']}")
    if results["best_hits"]:
        print("\nTop Alignments:")
        for h in results["best_hits"][:5]:
            print(f"  [{h['match_rate']*100:.1f}%] {h['corpus']} ({h['config']}) @ offset {h['offset']}: '{h['key_sample']}'")
    else:
        print("\nNo historical running key offset crossed the significance threshold.")
    print("=" * 70)
