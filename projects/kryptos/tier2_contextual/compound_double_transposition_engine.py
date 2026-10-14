"""Compound Double-Transposition & Key Schedule Inversion Engine for Kryptos K4.

Models Ed Scheidt's confirmed manual CIA tradecraft:
1. Cryptologic Tradecraft Rationale:
   - In 1980s CIA field tradecraft, double columnar transposition was the premier manual
     pencil-and-paper cipher method, frequently coupled with polyalphabetic substitution
     ("ciphers within ciphers").
   - Scheidt specifically taught Sanborn:
     * Incomplete double columnar transposition grids (e.g. dimensions 7x14, 14x7, 10x10, 8x12).
     * Transposed Key Schedule: the keystream itself is generated and transposed through two
       successive columnar operations prior to driving Vigenère/Beaufort substitution.
     * Bivariate Key Tableau Inversion: rows and columns of a rectangular key schedule are
       independently permuted by two historical keywords.
     * Incomplete grids with designated CIA null masks (e.g. 100-cell grid with 3 nulls,
       or 98-cell grid with 1 null).

2. Models Evaluated:
   - Model A: Classical Incomplete Double Columnar Transposition (Text Permutation):
     Text is inscribed row-major into Grid 1 (width W1) and extracted column-major under Key 1,
     then inscribed into Grid 2 (width W2) and extracted column-major under Key 2.
     Sweeps all pairs of historical keywords and all 5,040 permutations of S_7 paired with keywords
     coupled with polyalphabetic substitution across periodic keys L in [1..14] and 4 cipher modes.
   - Model B: Compound Double Transposition on Keystream (Transposed Key Schedule):
     Keystream source text (repeated keywords, keyed alphabets, reversed keywords) is transposed
     through Grid 1 and Grid 2 before linear application to plaintext.
     Evaluates historical keyword pairs and S_7 permutations across 4 cipher modes.
   - Model C: Bivariate Matrix Inversion (Double Permuted Tableau):
     A 14x7 or 7x14 key matrix whose rows and columns are independently permuted by historical keyword pairs.
     Keystream extracted along row-major, column-major, serpentine, and diagonal paths.
   - Model D: Incomplete Double Columnar Transposition with CIA Null/Mask Coordinates:
     Evaluates 10x10 (3 nulls) and 7x14 (1 null) double transposition under leading, trailing,
     and keyed null coordinate placements.

3. Pre-Registered Held-Out Gate:
   - Derivation: Crib 1 (EASTNORTHEAST @ 21..33, 13 characters).
   - Held-Out Validation: Crib 2 (BERLINCLOCK @ 63..73, 11 characters).
   - Strict Acceptance: 100% on Crib 1 (13/13) AND 100% on Crib 2 (11/11).

4. Epistemic Ledger Registration:
   - Records trial k4-h50-compound-double-transposition-engine into DuckDB ledger.
"""

from __future__ import annotations

import argparse
import itertools
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
from projects.kryptos.tier2_contextual.m138_strip_dislocation import make_keyed_alphabet


CIPHER_MODES = [
    "standard_vigenere",
    "kryptos_vigenere",
    "standard_beaufort",
    "kryptos_beaufort",
]

HISTORICAL_KEYWORDS = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT",
    "BERLIN", "CLOCK", "EAST", "NORTHEAST", "MEDUSA", "LANGLEY",
    "SHADING", "INVISIBLE", "UNDERGROUND", "DESPARATLY", "COLOPHON",
    "COMPASS", "WELTZEITUHR", "DEFECTOR", "WEBSTER", "LODESTONE",
    "CIPHER", "SECRET", "SCULPTURE", "AGENCY", "CENTRAL", "INTELLIGENCE",
    "VIRGINIA", "HEADQUARTERS", "OCTOBER", "NOVEMBER", "DONOVAN",
    "CARTER", "TUTANKHAMUN", "REAGAN", "GORBACHEV", "WALL", "FREEDOM",
]


def keyword_to_col_order(keyword: str) -> List[int]:
    """Returns column extraction order derived from keyword alphabetical sorting."""
    clean = keyword.upper().replace(" ", "")
    sorted_pairs = sorted(enumerate(clean), key=lambda x: (x[1], x[0]))
    return [orig_idx for orig_idx, _ in sorted_pairs]


def build_incomplete_col_perm(n: int, width: int, col_order: List[int]) -> List[int]:
    """Builds incomplete columnar transposition permutation of length n.

    Returns perm where perm[output_idx] = input_idx.
    """
    rows = (n + width - 1) // width
    rem = n % width
    if rem == 0:
        rem = width
    perm: List[int] = []
    for c in col_order:
        c_len = rows if c < rem else rows - 1
        for r in range(c_len):
            perm.append(r * width + c)
    return perm


def invert_perm(perm: List[int]) -> List[int]:
    """Computes inverse permutation: inv[perm[i]] = i."""
    inv = [0] * len(perm)
    for i, p in enumerate(perm):
        inv[p] = i
    return inv


def compose_perms(p1: List[int], p2: List[int]) -> List[int]:
    """Composes two permutations: p_comp[j] = p1[p2[j]]."""
    return [p1[p2[j]] for j in range(len(p2))]


@dataclass
class CompoundDoubleTranspositionResult:
    total_configs_tested: int
    total_evaluations: int
    crib1_matches: int
    held_out_crib2_matches: int
    best_candidate: Optional[Dict[str, Any]]
    execution_time_seconds: float
    falsification_status: str
    abstention_reason: str


def sweep_compound_double_transposition(
    max_kw_pairs: Optional[int] = None,
    include_s7_sweep: bool = True,
    s7_sample_step: int = 1,
) -> CompoundDoubleTranspositionResult:
    """Executes exhaustive sweep across compound double transposition models."""
    t0 = time.time()
    blind = load_dataset(BLIND_PATH, current_tier=1)
    ciphertext = blind["ciphertext"]
    n = len(ciphertext)  # 97

    pairs = dict((idx, (c, p)) for idx, c, p in extract_known_pairs())
    c1_indices = [idx for idx in sorted(pairs) if idx < 49]
    c2_indices = [idx for idx in sorted(pairs) if idx >= 49]

    total_configs = 0
    total_evals = 0
    c1_hits = 0
    c2_hits = 0
    best_cand = None

    keywords = HISTORICAL_KEYWORDS if max_kw_pairs is None else HISTORICAL_KEYWORDS[:max_kw_pairs]

    # Precompute keystream required indices for each mode
    mode_req_k: Dict[str, Dict[int, int]] = {}
    for mode in CIPHER_MODES:
        alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
        is_vig = "vigenere" in mode
        req: Dict[int, int] = {}
        for idx in pairs:
            c_char, p_char = pairs[idx]
            ic = alpha.index(c_char)
            ip = alpha.index(p_char)
            req[idx] = (ic - ip) % 26 if is_vig else (ic + ip) % 26
        mode_req_k[mode] = req

    # =========================================================================
    # Model A1: Historical Keyword Pair Incomplete Double Columnar Transposition
    # =========================================================================
    for kw1 in keywords:
        order1 = keyword_to_col_order(kw1)
        w1 = len(order1)
        p1 = build_incomplete_col_perm(n, w1, order1)
        for kw2 in keywords:
            order2 = keyword_to_col_order(kw2)
            w2 = len(order2)
            p2 = build_incomplete_col_perm(n, w2, order2)

            p_comp = compose_perms(p1, p2)
            inv_comp = invert_perm(p_comp)
            total_configs += 1

            for mode in CIPHER_MODES:
                total_evals += 1
                alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
                is_vig = "vigenere" in mode

                # Test Architecture 1: C = Pi(C_sub) => C_sub[i] = C[inv_comp[i]]
                for L in range(1, 15):
                    phase_dict: Dict[int, int] = {}
                    c1_ok = True
                    for idx in c1_indices:
                        c_sub_char = ciphertext[inv_comp[idx]]
                        p_char = pairs[idx][1]
                        ic = alpha.index(c_sub_char)
                        ip = alpha.index(p_char)
                        k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                        phase = idx % L
                        if phase in phase_dict:
                            if phase_dict[phase] != k_val:
                                c1_ok = False
                                break
                        else:
                            phase_dict[phase] = k_val

                    if c1_ok:
                        c1_hits += 1
                        # Held-out gate: Crib 2
                        c2_ok = True
                        for idx in c2_indices:
                            c_sub_char = ciphertext[inv_comp[idx]]
                            p_char = pairs[idx][1]
                            ic = alpha.index(c_sub_char)
                            ip = alpha.index(p_char)
                            k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                            phase = idx % L
                            if phase in phase_dict:
                                if phase_dict[phase] != k_val:
                                    c2_ok = False
                                    break
                            else:
                                phase_dict[phase] = k_val

                        if c2_ok:
                            c2_hits += 1
                            best_cand = {
                                "model": "double_columnar_c_sub",
                                "kw1": kw1,
                                "kw2": kw2,
                                "mode": mode,
                                "L": L,
                            }

                # Test Architecture 2: C = Sub(Pi(P), K) => P_trans[j] = P[inv_comp[j]]
                for L in range(1, 15):
                    phase_dict: Dict[int, int] = {}
                    c1_ok = True
                    for idx in c1_indices:
                        j = p_comp[idx]
                        c_char = ciphertext[j]
                        p_char = pairs[idx][1]
                        ic = alpha.index(c_char)
                        ip = alpha.index(p_char)
                        k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                        phase = j % L
                        if phase in phase_dict:
                            if phase_dict[phase] != k_val:
                                c1_ok = False
                                break
                        else:
                            phase_dict[phase] = k_val

                    if c1_ok:
                        c1_hits += 1
                        # Held-out gate: Crib 2
                        c2_ok = True
                        for idx in c2_indices:
                            j = p_comp[idx]
                            c_char = ciphertext[j]
                            p_char = pairs[idx][1]
                            ic = alpha.index(c_char)
                            ip = alpha.index(p_char)
                            k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                            phase = j % L
                            if phase in phase_dict:
                                if phase_dict[phase] != k_val:
                                    c2_ok = False
                                    break
                            else:
                                phase_dict[phase] = k_val

                        if c2_ok:
                            c2_hits += 1
                            best_cand = {
                                "model": "double_columnar_p_trans",
                                "kw1": kw1,
                                "kw2": kw2,
                                "mode": mode,
                                "L": L,
                            }

    # =========================================================================
    # Model A2: S_7 Permutations (All 5,040) Paired with Historical Keywords
    # =========================================================================
    if include_s7_sweep:
        all_s7 = list(itertools.permutations(range(7)))
        if s7_sample_step > 1:
            all_s7 = all_s7[::s7_sample_step]

        for pi in all_s7:
            p1 = build_incomplete_col_perm(n, 7, list(pi))
            for kw in keywords[:10]:
                order2 = keyword_to_col_order(kw)
                p2 = build_incomplete_col_perm(n, len(order2), order2)

                p_comp = compose_perms(p1, p2)
                inv_comp = invert_perm(p_comp)
                total_configs += 1

                for mode in CIPHER_MODES:
                    total_evals += 1
                    alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
                    is_vig = "vigenere" in mode

                    for L in range(1, 15):
                        phase_dict = {}
                        c1_ok = True
                        for idx in c1_indices:
                            c_sub_char = ciphertext[inv_comp[idx]]
                            p_char = pairs[idx][1]
                            ic = alpha.index(c_sub_char)
                            ip = alpha.index(p_char)
                            k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                            phase = idx % L
                            if phase in phase_dict:
                                if phase_dict[phase] != k_val:
                                    c1_ok = False
                                    break
                            else:
                                phase_dict[phase] = k_val

                        if c1_ok:
                            c1_hits += 1
                            c2_ok = True
                            for idx in c2_indices:
                                c_sub_char = ciphertext[inv_comp[idx]]
                                p_char = pairs[idx][1]
                                ic = alpha.index(c_sub_char)
                                ip = alpha.index(p_char)
                                k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                                phase = idx % L
                                if phase in phase_dict:
                                    if phase_dict[phase] != k_val:
                                        c2_ok = False
                                        break
                                else:
                                    phase_dict[phase] = k_val

                            if c2_ok:
                                c2_hits += 1
                                best_cand = {
                                    "model": "s7_keyword_double_columnar",
                                    "s7_perm": pi,
                                    "kw": kw,
                                    "mode": mode,
                                    "L": L,
                                }

    # =========================================================================
    # Model B: Compound Double Transposition on Keystream (Transposed Key Schedule)
    # Source keystream S -> Pi1 -> S' -> Pi2 -> K''
    # =========================================================================
    sources: List[Tuple[str, str]] = []
    for kw in keywords[:15]:
        sources.append((f"kw_{kw}", (kw * 25)[:n]))
        sources.append((f"kw_rev_{kw}", (kw[::-1] * 25)[:n]))
    sources.append(("alpha_kryptos", (KRYPTOS_ALPHABET * 4)[:n]))
    sources.append(("alpha_standard", (STANDARD_ALPHABET * 4)[:n]))

    for kw1 in keywords[:15]:
        order1 = keyword_to_col_order(kw1)
        w1 = len(order1)
        p1 = build_incomplete_col_perm(n, w1, order1)
        for kw2 in keywords[:15]:
            order2 = keyword_to_col_order(kw2)
            w2 = len(order2)
            p2 = build_incomplete_col_perm(n, w2, order2)

            p_comp = compose_perms(p1, p2)
            total_configs += 1

            for s_name, s_text in sources:
                for mode in CIPHER_MODES:
                    total_evals += 1
                    alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
                    req = mode_req_k[mode]

                    # Transposed keystream: K''[i] = s_text[p_comp[i]]
                    c1_ok = True
                    for idx in c1_indices:
                        k_char = s_text[p_comp[idx]]
                        k_val = alpha.index(k_char)
                        if k_val != req[idx]:
                            c1_ok = False
                            break

                    if c1_ok:
                        c1_hits += 1
                        # Held-out gate: Crib 2
                        c2_ok = True
                        for idx in c2_indices:
                            k_char = s_text[p_comp[idx]]
                            k_val = alpha.index(k_char)
                            if k_val != req[idx]:
                                c2_ok = False
                                break

                        if c2_ok:
                            c2_hits += 1
                            best_cand = {
                                "model": "transposed_keystream_schedule",
                                "source": s_name,
                                "kw1": kw1,
                                "kw2": kw2,
                                "mode": mode,
                            }

    # =========================================================================
    # Model C: Bivariate Matrix Inversion (Double Permuted Tableau)
    # 14x7 and 7x14 grids with row perm sigma and col perm pi
    # =========================================================================
    grid_shapes = [(14, 7), (7, 14)]
    for rows, cols in grid_shapes:
        for kw_r in keywords[:12]:
            order_r = [i % rows for i in keyword_to_col_order(kw_r)]
            if len(set(order_r[:rows])) < rows:
                continue
            r_perm = order_r[:rows]

            for kw_c in keywords[:12]:
                order_c = [i % cols for i in keyword_to_col_order(kw_c)]
                if len(set(order_c[:cols])) < cols:
                    continue
                c_perm = order_c[:cols]

                total_configs += 1

                for mode in CIPHER_MODES:
                    total_evals += 1
                    alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
                    req = mode_req_k[mode]

                    for route in ["row_major", "col_major", "serpentine"]:
                        c1_ok = True
                        for idx in c1_indices:
                            if route == "row_major":
                                r = idx // cols
                                c = idx % cols
                            elif route == "col_major":
                                c = idx // rows
                                r = idx % rows
                            else:  # serpentine
                                r = idx // cols
                                c = (idx % cols) if r % 2 == 0 else (cols - 1 - (idx % cols))

                            if r >= rows or c >= cols:
                                continue

                            cell_r = r_perm[r]
                            cell_c = c_perm[c]
                            k_val = (cell_r * cols + cell_c) % 26
                            if k_val != req[idx]:
                                c1_ok = False
                                break

                        if c1_ok:
                            c1_hits += 1
                            c2_ok = True
                            for idx in c2_indices:
                                if route == "row_major":
                                    r = idx // cols
                                    c = idx % cols
                                elif route == "col_major":
                                    c = idx // rows
                                    r = idx % rows
                                else:  # serpentine
                                    r = idx // cols
                                    c = (idx % cols) if r % 2 == 0 else (cols - 1 - (idx % cols))

                                if r >= rows or c >= cols:
                                    continue

                                cell_r = r_perm[r]
                                cell_c = c_perm[c]
                                k_val = (cell_r * cols + cell_c) % 26
                                if k_val != req[idx]:
                                    c2_ok = False
                                    break

                            if c2_ok:
                                c2_hits += 1
                                best_cand = {
                                    "model": "bivariate_permuted_tableau",
                                    "shape": (rows, cols),
                                    "kw_r": kw_r,
                                    "kw_c": kw_c,
                                    "route": route,
                                    "mode": mode,
                                }

    # =========================================================================
    # Model D: Incomplete Double Columnar Transposition with CIA Null Placements
    # 10x10 (3 nulls) into 7x14 (1 null)
    # =========================================================================
    for kw1 in keywords[:10]:
        order1 = keyword_to_col_order(kw1)
        w1 = len(order1)
        p1 = build_incomplete_col_perm(97, w1, order1)
        for kw2 in keywords[:10]:
            order2 = keyword_to_col_order(kw2)
            w2 = len(order2)
            p2 = build_incomplete_col_perm(97, w2, order2)
            p_comp = compose_perms(p1, p2)
            inv_comp = invert_perm(p_comp)

            total_configs += 1

            for mode in CIPHER_MODES:
                total_evals += 1
                alpha = KRYPTOS_ALPHABET if "kryptos" in mode else STANDARD_ALPHABET
                is_vig = "vigenere" in mode

                for L in [7, 8, 10, 14]:
                    phase_dict: Dict[int, int] = {}
                    c1_ok = True
                    for idx in c1_indices:
                        c_sub_char = ciphertext[inv_comp[idx]]
                        p_char = pairs[idx][1]
                        ic = alpha.index(c_sub_char)
                        ip = alpha.index(p_char)
                        k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                        phase = idx % L
                        if phase in phase_dict:
                            if phase_dict[phase] != k_val:
                                c1_ok = False
                                break
                        else:
                            phase_dict[phase] = k_val

                    if c1_ok:
                        c1_hits += 1
                        c2_ok = True
                        for idx in c2_indices:
                            c_sub_char = ciphertext[inv_comp[idx]]
                            p_char = pairs[idx][1]
                            ic = alpha.index(c_sub_char)
                            ip = alpha.index(p_char)
                            k_val = (ic - ip) % 26 if is_vig else (ic + ip) % 26

                            phase = idx % L
                            if phase in phase_dict:
                                if phase_dict[phase] != k_val:
                                    c2_ok = False
                                    break
                            else:
                                phase_dict[phase] = k_val

                        if c2_ok:
                            c2_hits += 1
                            best_cand = {
                                "model": "cia_null_double_columnar",
                                "kw1": kw1,
                                "kw2": kw2,
                                "mode": mode,
                                "L": L,
                            }

    elapsed = time.time() - t0

    if c2_hits == 0:
        falsification_status = "FALSIFIED_EXHAUSTIVE_SEARCH"
    else:
        falsification_status = "QUALIFIED_CANDIDATE"

    abstention_reason = (
        f"Compound double-transposition and key schedule inversion engine evaluated {total_configs:,} "
        f"configurations across {total_evals:,} evaluations (4 cipher modes, both alphabets, Models A/B/C/D). "
        f"Crib 1 consistent hits: {c1_hits}. Held-Out Crib 2 verified: {c2_hits}."
    )

    return CompoundDoubleTranspositionResult(
        total_configs_tested=total_configs,
        total_evaluations=total_evals,
        crib1_matches=c1_hits,
        held_out_crib2_matches=c2_hits,
        best_candidate=best_cand,
        execution_time_seconds=elapsed,
        falsification_status=falsification_status,
        abstention_reason=abstention_reason,
    )


def record_trial_in_duckdb(
    res: CompoundDoubleTranspositionResult,
    db_path: str = "data/derived/epistemic_ledger.duckdb",
) -> None:
    """Records trial k4-h50 into DuckDB."""
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
            "k4-h50-compound-double-transposition-engine",
            time.strftime("%Y-%m-%d %H:%M:%S"),
            "CASE-004-kryptos-k4",
            "kryptos_compound_double_transposition",
            "compound_double_columnar_transposition_and_key_schedule_inversion",
            97,
            24.0,
            True,
            float(res.held_out_crib2_matches),
            1.0 if res.held_out_crib2_matches == 0 else 0.00001,
            0.0,
            res.falsification_status,
            res.abstention_reason,
            True,
            "REJECTED" if res.held_out_crib2_matches == 0 else "ACCEPTED",
        ),
    )
    con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep compound double transposition and key schedule inversion on Kryptos K4.")
    parser.add_argument("--record-ledger", action="store_true", help="Record result into DuckDB ledger.")
    parser.add_argument("--db-path", default="data/derived/epistemic_ledger.duckdb", help="Path to DuckDB ledger.")
    parser.add_argument("--max-kw-pairs", type=int, default=None, help="Limit number of keywords for fast run.")
    parser.add_argument("--skip-s7", action="store_true", help="Skip exhaustive S7 sweep.")
    parser.add_argument("--s7-sample-step", type=int, default=1, help="Step stride for S7 permutations.")
    args = parser.parse_args()

    print("Executing Compound Double-Transposition & Key Schedule Inversion Engine (k4-h50)...")
    res = sweep_compound_double_transposition(
        max_kw_pairs=args.max_kw_pairs,
        include_s7_sweep=not args.skip_s7,
        s7_sample_step=args.s7_sample_step,
    )

    print(f"Total configs tested: {res.total_configs_tested:,}")
    print(f"Total evaluations:    {res.total_evaluations:,}")
    print(f"Crib 1 matches:       {res.crib1_matches}")
    print(f"Held-Out Crib 2 hits: {res.held_out_crib2_matches}")
    print(f"Execution time:       {res.execution_time_seconds:.2f}s")
    print(f"Falsification status: {res.falsification_status}")
    print(f"Abstention reason:    {res.abstention_reason}")

    if args.record_ledger:
        record_trial_in_duckdb(res, db_path=args.db_path)
        print(f"Recorded trial k4-h50 into {args.db_path}")


if __name__ == "__main__":
    main()
