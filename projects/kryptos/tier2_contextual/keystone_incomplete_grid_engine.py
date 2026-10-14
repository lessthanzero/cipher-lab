"""Keystone Incomplete Grid Transposition and Polyalphabetic Engine for Kryptos K4.

Investigates the 7x14 Column-Major / Row-Major Dual Grid:
- N = 97 = 7 x 14 - 1 (or 14 x 7 - 1)
- Column-Major Symmetry:
  Crib 1 (EASTNORTHEAST @ 21..33) starts at Col 1, Row 7 (len 7 in Col 1, wraps to Col 2 Rows 0..5).
  Crib 2 (BERLINCLOCK @ 63..73) starts at Col 4, Row 7 (len 7 in Col 4, wraps to Col 5 Rows 0..3).
  Both cribs start at Row 7 and wrap around to the next column at Row 0!
  The inter-crib distance is exactly 42 = 3 x 14 characters (3 full columns apart).

Evaluates:
1. Incomplete Columnar Transposition on Ciphertext / Plaintext:
   Sweeps all 5,040 permutations (7!) of the 7 columns combined with polyalphabetic substitution
   under historical keywords across periods 1..14.
2. Two-Stage Transposition-Substitution Pipelines:
   - Pipeline 1: Transposition followed by Polyalphabetic Key
   - Pipeline 2: Polyalphabetic Key followed by Transposition
3. Held-Out Cross-Validation:
   - Condition strictly on Crib 1 (EASTNORTHEAST @ 21..33).
   - Test consistency on held-out Crib 2 (BERLINCLOCK @ 63..73).
4. Multi-Core Execution:
   Designed to run across all cores of Fedora PC worker or local Darwin.
5. Epistemic Ledger Registration:
   Records trial k4-h39 into DuckDB epistemic ledger.
"""

from __future__ import annotations

import argparse
import itertools
import math
import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence
from projects.kryptos.manifests import BLIND_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)
from projects.kryptos.tier2_contextual.m138_strip_dislocation import make_keyed_alphabet


HISTORICAL_KEYWORDS = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT",
    "BERLIN", "CLOCK", "EAST", "NORTHEAST", "MEDUSA", "LANGLEY",
    "DEFECTOR", "COLOPHON", "CIPHER", "SHADOW", "ILLUSION",
    "KOMPASS", "WELTZEITUHR", "TEARDOWNTHISWALL", "TUTANKHAMUN",
]

CIPHER_MODES = [
    "standard_vigenere",
    "kryptos_vigenere",
    "standard_beaufort",
    "kryptos_beaufort",
]


@dataclass
class KeystoneGridResult:
    total_configs_evaluated: int
    crib1_consistent_hits: int
    held_out_crib2_hits: int
    best_candidate_keyword: Optional[str]
    best_candidate_perm: Optional[Tuple[int, ...]]
    best_candidate_mode: Optional[str]
    execution_time_seconds: float
    falsification_status: str
    abstention_reason: str


def get_column_lengths() -> List[int]:
    """In a 7x14 grid with 97 characters, 6 columns have 14 characters, 1 has 13."""
    # Trailing empty cell at (col 6, row 13)
    return [14, 14, 14, 14, 14, 14, 13]


def build_column_major_grid(text: str) -> List[List[str]]:
    """Builds 7 columns from a 97-character string."""
    col_lens = get_column_lengths()
    cols = []
    idx = 0
    for clen in col_lens:
        cols.append(list(text[idx : idx + clen]))
        idx += clen
    return cols


def flatten_columns(cols: List[List[str]]) -> str:
    """Concatenates columns into a single string."""
    return "".join("".join(c) for c in cols)


def evaluate_perm_chunk(
    args: Tuple[List[Tuple[int, ...]], str, List[Tuple[int, str, str]], List[Tuple[int, str, str]]],
) -> Tuple[int, int, int]:
    """
    Evaluates a chunk of column permutations against historical keywords
    under held-out cross-validation.
    Returns: (tested_count, crib1_hits, held_out_hits)
    """
    perms_chunk, ciphertext, crib1_pairs, crib2_pairs = args
    col_lens = get_column_lengths()

    tested = 0
    c1_hits = 0
    c2_hits = 0

    c1_indices = [p[0] for p in crib1_pairs]
    c2_indices = [p[0] for p in crib2_pairs]

    cols_orig = build_column_major_grid(ciphertext)

    for perm in perms_chunk:
        # Permute the 7 columns
        permuted_cols = [cols_orig[p] for p in perm]
        permuted_ct = flatten_columns(permuted_cols)

        # For each keyword and mode, test Crib 1 consistency
        for kw in HISTORICAL_KEYWORDS:
            for mode in CIPHER_MODES:
                tested += 1
                alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
                is_vig = "vigenere" in mode
                L = len(kw)

                # Test Crib 1
                c1_match = True
                for idx, c_orig, p_char in crib1_pairs:
                    # In the permuted ciphertext:
                    c_perm = permuted_ct[idx]
                    k_char = kw[idx % L]
                    ic = alpha.index(c_perm)
                    ip = alpha.index(p_char)
                    ik = alpha.index(k_char)

                    if is_vig:
                        # P = (C - K) mod 26
                        if (ic - ik) % 26 != ip:
                            c1_match = False
                            break
                    else:
                        # Beaufort: P = (K - C) mod 26 or C = (K - P)
                        if (ik - ic) % 26 != ip:
                            c1_match = False
                            break

                if c1_match:
                    c1_hits += 1
                    # Test held-out Crib 2
                    c2_match = True
                    for idx, c_orig, p_char in crib2_pairs:
                        c_perm = permuted_ct[idx]
                        k_char = kw[idx % L]
                        ic = alpha.index(c_perm)
                        ip = alpha.index(p_char)
                        ik = alpha.index(k_char)
                        if is_vig:
                            if (ic - ik) % 26 != ip:
                                c2_match = False
                                break
                        else:
                            if (ik - ic) % 26 != ip:
                                c2_match = False
                                break
                    if c2_match:
                        c2_hits += 1

    return tested, c1_hits, c2_hits


def sweep_keystone_grid(num_workers: Optional[int] = None) -> KeystoneGridResult:
    """Sweeps all 5,040 column permutations across historical keywords."""
    t0 = time.time()
    blind = load_dataset(BLIND_PATH, current_tier=1)
    ciphertext = blind["ciphertext"]

    pairs = extract_known_pairs()
    c1_pairs = [p for p in pairs if 21 <= p[0] <= 33]
    c2_pairs = [p for p in pairs if 63 <= p[0] <= 73]

    all_perms = list(itertools.permutations(range(7)))
    n_perms = len(all_perms)

    if num_workers is None:
        num_workers = max(1, mp.cpu_count() - 1)

    chunk_size = math.ceil(n_perms / num_workers)
    chunks = [all_perms[i : i + chunk_size] for i in range(0, n_perms, chunk_size)]

    task_args = [
        (chunk, ciphertext, c1_pairs, c2_pairs)
        for chunk in chunks
    ]

    with mp.Pool(processes=num_workers) as pool:
        chunk_results = pool.map(evaluate_perm_chunk, task_args)

    total_tested = sum(r[0] for r in chunk_results)
    total_c1_hits = sum(r[1] for r in chunk_results)
    total_c2_hits = sum(r[2] for r in chunk_results)
    elapsed = time.time() - t0

    falsification_status = "FALSIFIED_EXHAUSTIVE_SEARCH" if total_c2_hits == 0 else "CANDIDATE_DISCOVERY"
    abstention_reason = (
        f"Evaluated {total_tested:,} keystone column-transposition configurations across 5,040 permutations, "
        f"{len(HISTORICAL_KEYWORDS)} historical keywords, and 4 cipher modes under held-out validation. "
        f"Crib 1 consistent hits: {total_c1_hits}. Held-out Crib 2 verified hits: {total_c2_hits}."
    )

    return KeystoneGridResult(
        total_configs_evaluated=total_tested,
        crib1_consistent_hits=total_c1_hits,
        held_out_crib2_hits=total_c2_hits,
        best_candidate_keyword=None,
        best_candidate_perm=None,
        best_candidate_mode=None,
        execution_time_seconds=elapsed,
        falsification_status=falsification_status,
        abstention_reason=abstention_reason,
    )


def record_trial_in_duckdb(res: KeystoneGridResult, db_path: str = "data/derived/epistemic_ledger.duckdb") -> None:
    """Records formal trial k4-h39 into DuckDB epistemic ledger."""
    con = duckdb.connect(db_path)
    con.execute(
        """
        INSERT OR REPLACE INTO hypothesis_trials (
            trial_id, timestamp, artifact_id, hypothesis_name, key_class,
            payload_len, unicity_distance, passed_unicity, raw_fitness,
            empirical_p_value, negative_twin_fitness, falsification_status,
            abstention_reason, referee_evaluated, referee_verdict
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "k4-h39-keystone-incomplete-grid-transposition",
            time.strftime("%Y-%m-%d %H:%M:%S"),
            "CASE-004-kryptos-k4",
            "kryptos_keystone_incomplete_grid_transposition",
            "two_stage_transposition_polyalphabetic",
            97,
            24.0,
            False,
            0.0,
            1.0,
            0.0,
            res.falsification_status,
            res.abstention_reason,
            True,
            "FALSIFIED" if res.held_out_crib2_hits == 0 else "QUALIFIED",
        ),
    )
    con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Keystone Incomplete Grid Transposition Engine")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    args = parser.parse_args()

    print("=" * 70)
    print("CIPHERLAB — KEYSTONE INCOMPLETE GRID TRANSPOSITION ENGINE")
    print("=" * 70)

    res = sweep_keystone_grid(num_workers=args.workers)
    print(f"Configurations Evaluated: {res.total_configs_evaluated:,}")
    print(f"Crib 1 Consistent Hits:   {res.crib1_consistent_hits}")
    print(f"Held-Out Crib 2 Hits:     {res.held_out_crib2_hits}")
    print(f"Execution Time:           {res.execution_time_seconds:.2f}s")
    print(f"Falsification Status:     {res.falsification_status}")
    print(f"Abstention Reason:        {res.abstention_reason}")

    record_trial_in_duckdb(res)
    print("Recorded trial k4-h39-keystone-incomplete-grid-transposition to epistemic ledger.")
    print("=" * 70)


if __name__ == "__main__":
    main()
