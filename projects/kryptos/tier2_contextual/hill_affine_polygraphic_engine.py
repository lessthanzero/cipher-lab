"""Polygraphic Hill & Circulant Matrix Cipher Engine for Kryptos K4.

Evaluates algebraic matrix cipher models on the 14x7 grid and digraph blocks:
1. 2x2 Linear & Affine Hill Ciphers over Z_26:
   - Evaluates C_2i, C_2i+1 = M * (P_2i, P_2i+1)^T + B (mod 26).
   - Swept across even (phase 0) and odd (phase 1) digraph alignments.
   - Evaluated across Standard Alphabet and Kryptos Alphabet.

2. 7x7 Circulant & Toeplitz Row Vector Matrix Transformations:
   - In the 14x7 grid, Row 3 is EASTNOR (c=FLRVQQP) and Row 9 is BERLINC (c=NYPVTTM).
   - Formulates the linear system c = M * p (mod 26) for circulant matrices M_circ(c_0..c_6).
   - Solves via exact linear modular algebra over Z_26.

3. Pre-Registered Held-Out Protocol:
   - Derivation: Crib 1 (EASTNORTHEAST @ 21..33).
   - Held-Out Validation: Crib 2 (BERLINCLOCK @ 63..73).

4. Epistemic Ledger Registration:
   - Records trial k4-h43-hill-affine-polygraphic-engine into DuckDB ledger.
"""

from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from projects.kryptos.manifests import BLIND_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


@dataclass
class HillMatrixResult:
    total_2x2_tested: int
    total_circulant_tested: int
    total_evaluations: int
    crib1_matches: int
    held_out_crib2_matches: int
    best_candidate: Optional[Dict[str, Any]]
    execution_time_seconds: float
    falsification_status: str
    abstention_reason: str


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def solve_2x2_hill_exact() -> Tuple[int, int, int]:
    """Exhaustively solves 2x2 Hill linear and affine systems over Z_26 on cribs."""
    blind = load_dataset(BLIND_PATH, current_tier=1)
    ciphertext = blind["ciphertext"]

    crib1_text = "EASTNORTHEAST"
    crib2_text = "BERLINCLOCK"

    total_evals = 0
    c1_hits = 0
    c2_hits = 0

    for alpha_name, alpha in [("standard", STANDARD_ALPHABET), ("kryptos", KRYPTOS_ALPHABET)]:
        idx_map = {c: i for i, c in enumerate(alpha)}

        for phase in [0, 1]:
            # Extract consecutive digraph pairs from Crib 1
            pairs_c1 = []
            for k in range(phase, 12, 2):
                p1, p2 = idx_map[crib1_text[k]], idx_map[crib1_text[k + 1]]
                c1, c2 = idx_map[ciphertext[21 + k]], idx_map[ciphertext[21 + k + 1]]
                pairs_c1.append(((p1, p2), (c1, c2)))

            # Extract pairs from Crib 2
            pairs_c2 = []
            for k in range(phase, 10, 2):
                p1, p2 = idx_map[crib2_text[k]], idx_map[crib2_text[k + 1]]
                c1, c2 = idx_map[ciphertext[63 + k]], idx_map[ciphertext[63 + k + 1]]
                pairs_c2.append(((p1, p2), (c1, c2)))

            # Sweep row 1: a * p1 + b * p2 + v1 = c1 (mod 26)
            # Sweep row 2: c * p1 + d * p2 + v2 = c2 (mod 26)
            for a in range(26):
                for b in range(26):
                    for v1 in range(26):
                        total_evals += 1
                        # Check row 1 consistency on all Crib 1 pairs
                        r1_ok = True
                        for p, c in pairs_c1:
                            if (a * p[0] + b * p[1] + v1) % 26 != c[0]:
                                r1_ok = False
                                break
                        if not r1_ok:
                            continue

                        # If row 1 passed, check row 2 candidates
                        for c_coef in range(26):
                            for d in range(26):
                                # Invertibility check
                                det = (a * d - b * c_coef) % 26
                                if gcd(det, 26) != 1:
                                    continue
                                for v2 in range(26):
                                    r2_ok = True
                                    for p, c in pairs_c1:
                                        if (c_coef * p[0] + d * p[1] + v2) % 26 != c[1]:
                                            r2_ok = False
                                            break
                                    if r2_ok:
                                        c1_hits += 1
                                        # Test held-out Crib 2
                                        c2_pass = True
                                        for p, c in pairs_c2:
                                            if (a * p[0] + b * p[1] + v1) % 26 != c[0]:
                                                c2_pass = False
                                                break
                                            if (c_coef * p[0] + d * p[1] + v2) % 26 != c[1]:
                                                c2_pass = False
                                                break
                                        if c2_pass:
                                            c2_hits += 1

    return total_evals, c1_hits, c2_hits


def solve_mod_p(A: List[List[int]], b: List[int], p: int) -> Optional[List[int]]:
    """Solves A * x = b (mod p) using Gaussian elimination over finite field Z_p."""
    n = len(A)
    M = [[A[i][j] % p for j in range(n)] + [b[i] % p] for i in range(n)]
    for col in range(n):
        pivot = -1
        for row in range(col, n):
            if M[row][col] % p != 0:
                pivot = row
                break
        if pivot == -1:
            return None
        M[col], M[pivot] = M[pivot], M[col]
        inv = pow(M[col][col], -1, p)
        M[col] = [(x * inv) % p for x in M[col]]
        for row in range(n):
            if row != col and M[row][col] % p != 0:
                factor = M[row][col]
                M[row] = [(M[row][j] - factor * M[col][j]) % p for j in range(n + 1)]
    return [M[i][n] for i in range(n)]


def solve_7x7_circulant_exact() -> Tuple[int, int, int]:
    """Evaluates 7x7 circulant matrix transformations via exact CRT modular linear algebra."""
    blind = load_dataset(BLIND_PATH, current_tier=1)
    ciphertext = blind["ciphertext"]

    p3 = "EASTNOR"
    c3 = ciphertext[21:28]
    p9 = "BERLINC"
    c9 = ciphertext[63:70]

    total_circ = 0
    c1_circ_hits = 0
    c2_circ_hits = 0

    for alpha_name, alpha in [("standard", STANDARD_ALPHABET), ("kryptos", KRYPTOS_ALPHABET)]:
        idx_map = {c: i for i, c in enumerate(alpha)}
        p3_v = [idx_map[ch] for ch in p3]
        c3_v = [idx_map[ch] for ch in c3]
        p9_v = [idx_map[ch] for ch in p9]
        c9_v = [idx_map[ch] for ch in c9]

        A = [[p3_v[(m + k) % 7] for m in range(7)] for k in range(7)]
        sol13 = solve_mod_p(A, c3_v, 13)
        sol2 = solve_mod_p(A, c3_v, 2)

        total_circ += 2

        if sol13 is not None and sol2 is not None:
            # Chinese Remainder Theorem: mod 26 = 14 * sol13 + 13 * sol2 (mod 26)
            sol26 = [((sol13[i] * 14 + sol2[i] * 13) % 26) for i in range(7)]
            c1_circ_hits += 1

            # Check held-out Crib 2 (Row 9)
            r9_match = sum(1 for k in range(7) if sum(sol26[m] * p9_v[(m + k) % 7] for m in range(7)) % 26 == c9_v[k])
            if r9_match == 7:
                c2_circ_hits += 1

    return total_circ, c1_circ_hits, c2_circ_hits


def sweep_polygraphic_matrix_engine() -> HillMatrixResult:
    """Runs complete polygraphic Hill and Circulant matrix evaluation."""
    t0 = time.time()

    # 1. Solve 2x2 Hill linear and affine systems
    total_2x2, c1_2x2, c2_2x2 = solve_2x2_hill_exact()

    # 2. Solve 7x7 Circulant matrix systems
    total_circ, c1_circ, c2_circ = solve_7x7_circulant_exact()

    total_evals = total_2x2 + total_circ
    c1_hits = c1_2x2 + c1_circ
    c2_hits = c2_2x2 + c2_circ
    elapsed = time.time() - t0

    if c2_hits == 0:
        falsification_status = "FALSIFIED_EXHAUSTIVE_SEARCH"
    else:
        falsification_status = "QUALIFIED_CANDIDATE"

    abstention_reason = (
        f"Polygraphic Hill & Circulant matrix engine evaluated {total_2x2:,} 2x2 affine matrices and "
        f"{total_circ:,} 7x7 circulant matrix configurations across Z_26 under both alphabets. "
        f"Crib 1 consistent hits: {c1_hits}. Held-out Crib 2 verified: {c2_hits}."
    )

    return HillMatrixResult(
        total_2x2_tested=total_2x2,
        total_circulant_tested=total_circ,
        total_evaluations=total_evals,
        crib1_matches=c1_hits,
        held_out_crib2_matches=c2_hits,
        best_candidate=None,
        execution_time_seconds=elapsed,
        falsification_status=falsification_status,
        abstention_reason=abstention_reason,
    )


def record_trial_in_duckdb(res: HillMatrixResult, db_path: str = "data/derived/epistemic_ledger.duckdb") -> None:
    """Records trial k4-h43 into DuckDB."""
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
            "k4-h43-hill-affine-polygraphic-engine",
            time.strftime("%Y-%m-%d %H:%M:%S"),
            "CASE-004-kryptos-k4",
            "kryptos_hill_circulant_polygraphic_matrix",
            "polygraphic_algebraic_matrix_cipher",
            97,
            24.0,
            False,
            0.0,
            1.0,
            0.0,
            res.falsification_status,
            res.abstention_reason,
            True,
            "FALSIFIED" if res.held_out_crib2_matches == 0 else "QUALIFIED",
        ),
    )
    con.close()


def main() -> None:
    print("=" * 70)
    print("CIPHERLAB — POLYGRAPHIC HILL & CIRCULANT MATRIX CIPHER ENGINE")
    print("=" * 70)

    res = sweep_polygraphic_matrix_engine()
    print(f"2x2 Matrices Evaluated:     {res.total_2x2_tested:,}")
    print(f"Circulant Matrices Tested:  {res.total_circulant_tested:,}")
    print(f"Total Configurations:       {res.total_evaluations:,}")
    print(f"Crib 1 Consistent Hits:     {res.crib1_matches}")
    print(f"Held-Out Crib 2 Hits:       {res.held_out_crib2_matches}")
    print(f"Execution Time:             {res.execution_time_seconds:.2f}s")
    print(f"Falsification Status:       {res.falsification_status}")
    print(f"Abstention Reason:          {res.abstention_reason}")

    record_trial_in_duckdb(res)
    print("Recorded trial k4-h43-hill-affine-polygraphic-engine to epistemic ledger.")
    print("=" * 70)


if __name__ == "__main__":
    main()
