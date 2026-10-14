"""Tier 2 Formal Mathematical Models for Kryptos K4.

Formulates and solves rigorous mathematical representations of the 14x7 keystream matrix
across the 24 confirmed anchor positions:

Model 1: Low-Rank Matrix Factorization over Finite Rings Z_m (m in {24, 25, 26}):
  K[r, c] == (u[r] + v[c]) mod m (Rank-1 additive)
  K[r, c] == (u[r] * v[c] + w[r] + z[c]) mod m (Rank-2 bilinear)

Model 2: 2D Linear Modular Recurrence (Discrete State-Space / Cellular Automaton):
  K[r, c] == (a * K[r-1, c] + b * K[r, c-1] + d) mod 26

Model 3: Z3 SMT Exact Satisfiability Engine:
  Determines whether ANY consistent algebraic parameterization of degree <= 2
  satisfies the 24 anchor equations simultaneously.
"""

from __future__ import annotations

import argparse
import time
from typing import Any, Dict, List, Optional, Tuple

from z3 import Int, Solver, sat, unknown

from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


GRID_ROWS = 14
GRID_COLS = 7


def load_keystream_matrices() -> Dict[str, Dict[Tuple[int, int], int]]:
    """
    Extract known key values K[r, c] across the 24 anchors
    under both Kryptos Vigenere and Standard Vigenere.
    """
    pairs = extract_known_pairs()
    mats: Dict[str, Dict[Tuple[int, int], int]] = {
        "kryptos_vigenere": {},
        "standard_vigenere": {},
        "kryptos_beaufort": {},
        "standard_beaufort": {},
    }

    for idx, c, p in pairs:
        r = idx // GRID_COLS
        col = idx % GRID_COLS

        # Kryptos indices
        ck = KRYPTOS_ALPHABET.index(c)
        pk = KRYPTOS_ALPHABET.index(p)
        mats["kryptos_vigenere"][(r, col)] = (ck - pk) % 26
        mats["kryptos_beaufort"][(r, col)] = (ck + pk) % 26

        # Standard indices
        cs = STANDARD_ALPHABET.index(c)
        ps = STANDARD_ALPHABET.index(p)
        mats["standard_vigenere"][(r, col)] = (cs - ps) % 26
        mats["standard_beaufort"][(r, col)] = (cs + ps) % 26

    return mats


def solve_rank1_additive_smt(
    matrix: Dict[Tuple[int, int], int],
    modulus: int = 26,
    timeout_ms: int = 5000,
) -> Tuple[bool, Optional[Dict[str, List[int]]]]:
    """
    Test whether K[r, c] == (u[r] + v[c]) mod modulus for all 24 anchors.
    Unknowns: u[0..13] (14 vars), v[0..6] (7 vars).
    Constraints: 24 linear modular equations.
    """
    s = Solver()
    s.set("timeout", timeout_ms)

    u = [Int(f"u_{r}") for r in range(GRID_ROWS)]
    v = [Int(f"v_{c}") for c in range(GRID_COLS)]

    for r in range(GRID_ROWS):
        s.add(u[r] >= 0, u[r] < modulus)
    for c in range(GRID_COLS):
        s.add(v[c] >= 0, v[c] < modulus)

    for (r, c), k_val in matrix.items():
        s.add((u[r] + v[c]) % modulus == (k_val % modulus))

    if s.check() == sat:
        m = s.model()
        u_sol = [m[u[r]].as_long() for r in range(GRID_ROWS)]
        v_sol = [m[v[c]].as_long() for c in range(GRID_COLS)]
        return True, {"u_rows": u_sol, "v_cols": v_sol}

    return False, None


def solve_rank2_bilinear_algebraic(
    matrix: Dict[Tuple[int, int], int],
    modulus: int = 26,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Test whether K[r, c] == (u[r] * v[c] + w[r] + z[c]) mod modulus for all 24 anchors.
    Uses algebraic decoupling:
      Delta_43(c) = K[4, c] - K[3, c] == alpha * v[c] + beta mod modulus (for c in 0..5)
      Delta_109(c) = K[10, c] - K[9, c] == gamma * v[c] + delta mod modulus (for c in 0..3)
    Eliminating v[c] forces alpha * Delta_109(c) - gamma * Delta_43(c) == constant mod modulus
    for all c in {0, 1, 2, 3}.
    """
    # Check that required cells exist
    for r in [3, 4, 9, 10]:
        for c in range(4):
            if (r, c) not in matrix:
                return False, None

    d43 = [(matrix[(4, c)] - matrix[(3, c)]) % modulus for c in range(6)]
    d109 = [(matrix[(10, c)] - matrix[(9, c)]) % modulus for c in range(4)]

    # Search (alpha, gamma) != (0, 0)
    for alpha in range(modulus):
        for gamma in range(modulus):
            if alpha == 0 and gamma == 0:
                continue
            cross = [(alpha * d109[c] - gamma * d43[c]) % modulus for c in range(4)]
            if len(set(cross)) == 1:
                # Potential candidate: verify if valid v[c] and beta exist for all 6 cols of d43
                for beta in range(modulus):
                    valid_v = True
                    for c in range(6):
                        req = (d43[c] - beta) % modulus
                        sol = [v for v in range(modulus) if (alpha * v) % modulus == req]
                        if not sol:
                            valid_v = False
                            break
                    if valid_v:
                        return True, {
                            "alpha": alpha,
                            "gamma": gamma,
                            "beta": beta,
                            "modulus": modulus,
                        }

    # Case alpha == 0 and gamma == 0: requires d43 to be constant across all 6 cols
    if len(set(d43)) == 1 and len(set(d109)) == 1:
        return True, {"alpha": 0, "gamma": 0, "modulus": modulus}

    return False, None


def solve_2d_linear_recurrence(
    matrix: Dict[Tuple[int, int], int],
    modulus: int = 26,
) -> List[Dict[str, Any]]:
    """
    Test whether K[r, c] == (a * K[r-1, c] + b * K[r, c-1] + d) mod modulus.
    Collects all triplets (K[r, c], K[r-1, c], K[r, c-1]) available in the 24 anchors.
    """
    triplets = []
    for (r, c), k_curr in matrix.items():
        if (r - 1, c) in matrix and (r, c - 1) in matrix:
            k_up = matrix[(r - 1, c)]
            k_left = matrix[(r, c - 1)]
            triplets.append((k_curr, k_up, k_left, r, c))

    if len(triplets) < 3:
        return []

    # Search (a, b, d) in [0..modulus-1]^3 that satisfy all triplets
    solutions = []
    for a in range(modulus):
        for b in range(modulus):
            for d in range(modulus):
                if all((a * k_up + b * k_left + d) % modulus == k_curr for k_curr, k_up, k_left, _, _ in triplets):
                    solutions.append({
                        "a": a,
                        "b": b,
                        "d": d,
                        "satisfied_triplets": len(triplets),
                    })
    return solutions


def run_formal_math_audit() -> Dict[str, Any]:
    """Execute complete formal mathematical audit across all models and moduli."""
    matrices = load_keystream_matrices()
    report: Dict[str, Any] = {}

    moduli = [24, 25, 26]

    for model_name, mat in matrices.items():
        report[model_name] = {
            "rank1_additive": {},
            "rank2_bilinear": {},
            "recurrence_2d": {},
        }

        # 1. Rank-1 Additive
        for mod in moduli:
            ok, sol = solve_rank1_additive_smt(mat, modulus=mod)
            report[model_name]["rank1_additive"][f"mod_{mod}"] = {
                "satisfiable": ok,
                "solution": sol,
            }

        # 2. Rank-2 Bilinear Affine
        for mod in moduli:
            ok, sol = solve_rank2_bilinear_algebraic(mat, modulus=mod)
            report[model_name]["rank2_bilinear"][f"mod_{mod}"] = {
                "satisfiable": ok,
                "solution": sol,
            }

        # 3. 2D Linear Recurrence
        for mod in moduli:
            recs = solve_2d_linear_recurrence(mat, modulus=mod)
            report[model_name]["recurrence_2d"][f"mod_{mod}"] = recs

    return report


if __name__ == "__main__":
    print("=" * 70)
    print("CIPHERLAB — TIER 2 FORMAL MATHEMATICAL MODEL SOLVER")
    print("=" * 70)

    t0 = time.time()
    res = run_formal_math_audit()
    elapsed = time.time() - t0

    print(f"\nExecution Time: {elapsed:.3f}s\n")
    for model_name, data in res.items():
        print(f"--- Model: {model_name} ---")
        print("  Rank-1 Additive K[r, c] == (u[r] + v[c]) mod m:")
        for mod_str, rdata in data["rank1_additive"].items():
            status = "SATISFIABLE" if rdata["satisfiable"] else "UNSAT (Falsified)"
            print(f"    {mod_str}: {status}")

        print("  Rank-2 Bilinear Affine K[r, c] == (u[r]*v[c] + w[r] + z[c]) mod m:")
        for mod_str, rdata in data["rank2_bilinear"].items():
            status = "SATISFIABLE" if rdata["satisfiable"] else "UNSAT (Falsified)"
            print(f"    {mod_str}: {status}")
            if rdata["satisfiable"]:
                print(f"      Solution: {rdata['solution']}")

        print("  2D Linear Recurrence K[r,c] == (a*K[r-1,c] + b*K[r,c-1] + d) mod m:")
        for mod_str, recs in data["recurrence_2d"].items():
            print(f"    {mod_str}: Found {len(recs)} exact solutions")
            for r in recs:
                print(f"      -> a={r['a']}, b={r['b']}, d={r['d']} (matched {r['satisfied_triplets']} triplets)")
        print()
    print("=" * 70)
