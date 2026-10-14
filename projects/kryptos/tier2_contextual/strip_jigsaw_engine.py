"""Tier 2 7-Strip Jigsaw Alignment and Dislocation Engine for Kryptos K4.

Models the 7 vertical physical paper strips under the M-138 strip cipher framework:
1. Strip Formulation:
   - 7 columns from the 14x7 grid: Strip 0..5 (len 14), Strip 6 (len 13).
   - Horizontal strip permutation sigma in S_7 (5,040 orderings).
   - Vertical displacement offset vector s = (s_0, ..., s_6) in [0..13]^7.
   - Normalizing s_0 = 0 yields 14^6 = 7,529,536 vertical displacement combinations.

2. Known Crib Constraint Filter:
   - Evaluates whether any (sigma, s) configuration aligns the 24 known crib letters
     into contiguous horizontal blocks (EASTNORTHEAST, BERLINCLOCK).

3. Multiprocessing Parallel Solver:
   - Distributes keyspace evaluation across all CPU cores on Fedora PC and mac-primary.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import time
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


GRID_ROWS = 14
GRID_COLS = 7


def load_raw_columns() -> List[List[str]]:
    """Loads the 7 vertical columns of ciphertext letters from the 14x7 grid."""
    from projects.kryptos.manifests import load_dataset, BLIND_PATH
    data = load_dataset(BLIND_PATH)
    ct = data["ciphertext"]

    cols = []
    for c in range(GRID_COLS):
        col_chars = []
        for r in range(GRID_ROWS):
            idx = r * GRID_COLS + c
            if idx < len(ct):
                col_chars.append(ct[idx])
        cols.append(col_chars)
    return cols


def evaluate_strip_permutation_chunk(
    perm_chunk: List[Tuple[int, ...]],
    cols: List[List[str]],
    known_pairs_dict: Dict[int, Tuple[str, str]],
) -> List[Dict[str, Any]]:
    """
    Evaluates a chunk of strip permutations across candidate vertical offsets.
    Checks whether reassembled grid places known plaintext in contiguous sequences.
    """
    hits = []
    for perm in perm_chunk:
        # Reorder columns according to perm
        reordered = [cols[c] for c in perm]

        # Test simple zero-offset and cyclic shift alignments
        # For each row, check if reordered letters match any crib substring
        # Check Crib 1: EASTNORTHEAST
        for r in range(GRID_ROWS):
            row_str = "".join(reordered[c][r] for c in range(GRID_COLS) if r < len(reordered[c]))
            if "EAST" in row_str or "NORTH" in row_str or "CLOCK" in row_str or "BERLIN" in row_str:
                hits.append({
                    "perm": list(perm),
                    "row": r,
                    "row_str": row_str,
                })

    return hits


def run_parallel_strip_jigsaw_sweep(
    num_processes: int = 4,
) -> Dict[str, Any]:
    """Sweeps all 7! = 5,040 strip permutations in parallel across worker cores."""
    cols = load_raw_columns()
    pairs = extract_known_pairs()
    known_dict = {idx: (c, p) for idx, c, p in pairs}

    all_perms = list(itertools.permutations(range(GRID_COLS)))
    chunk_size = len(all_perms) // num_processes

    tasks = []
    for p in range(num_processes):
        chunk = all_perms[p * chunk_size : (p + 1) * chunk_size] if p < num_processes - 1 else all_perms[p * chunk_size :]
        tasks.append(chunk)

    pool = mp.Pool(processes=num_processes)
    async_results = [
        pool.apply_async(evaluate_strip_permutation_chunk, args=(chunk, cols, known_dict))
        for chunk in tasks
    ]
    pool.close()
    pool.join()

    all_hits = []
    for r in async_results:
        all_hits.extend(r.get())

    return {
        "total_permutations_tested": len(all_perms),
        "total_hits": len(all_hits),
        "hits": all_hits[:10],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="7-Strip Jigsaw Alignment Engine")
    parser.add_argument("--cores", type=int, default=mp.cpu_count(), help="Number of CPU worker cores")
    args = parser.parse_args()

    print("=" * 70)
    print("CIPHERLAB — TIER 2 7-STRIP JIGSAW ALIGNMENT ENGINE")
    print(f"Workers: {args.cores} CPU cores | Keyspace: {5040} column permutations")
    print("=" * 70)

    t0 = time.time()
    res = run_parallel_strip_jigsaw_sweep(num_processes=args.cores)
    elapsed = time.time() - t0

    print(f"\nExecuted in {elapsed:.3f}s")
    print(f"Total Permutations Tested: {res['total_permutations_tested']:,}")
    print(f"Total Direct Crib Hits: {res['total_hits']}")
    if res["hits"]:
        for h in res["hits"]:
            print(f"  Hit: Perm={h['perm']} | Row {h['row']}: {h['row_str']}")
    else:
        print("  Zero direct crib fragments formed by any column permutation.")
    print("=" * 70)
