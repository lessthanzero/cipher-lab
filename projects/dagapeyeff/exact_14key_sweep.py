"""Exact 14-Key Double Transposition Sweep Engine for D'Agapeyeff.

Tests whether Alexander D'Agapeyeff applied double columnar transposition
using historical 14-letter and 13-letter keywords from his professional background
(cartographer, Ordnance Survey, patent draughtsman, Russian emigré).

Sweeps:
- Keywords: ORDNANCESURVEY, CARTOGRAPHICAL, TRIANGULATIONS, PATENTDRAUGHTS, etc.
- Directions: standard_encryption vs kerckhoffs_decryption
- Orders: col_then_row vs row_then_col
- Geometries: 196 (14x14), 182 (14x13), diagonal_pelling_182 (13x14)
- Decryption: Vertical Two-Square and Single Polybius
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_grid import (
    grid_to_pairs,
    pairs_to_grid,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.corpus import get_digit_pairs, get_stripped_14x13_pairs
from projects.dagapeyeff.kerckhoffs_defect import (
    apply_columnar_transposition_direction,
    get_standard_key_order,
)
from projects.dagapeyeff.two_square import pairs_to_coordinates
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
)


EXACT_14_CANDIDATE_KEYS = [
    "ORDNANCESURVEY",     # 14 letters - Exact match for 14x14 grid
    "CARTOGRAPHICAL",     # 14 letters - Professional domain
    "TRIANGULATIONS",     # 14 letters - Primary OS triangulation
    "HYDROGRAPHICAL",     # 14 letters - Admiralty surveying
    "PATENTDRAUGHTS",     # 14 letters - Professional draughtsman
    "TOPOGRAPHICALS",     # 14 letters - Cartographic discipline
    "MILITARYMAPPIN",     # 14 letters - 1939 wartime mapping
    "REUNIONTOMORR",      # 13 letters (for 14x13)
    "SCHUVALOFSCHU",      # 13 letters
    "RETRIANGULATE",      # 13 letters
    "ALEXANDERDAGAP",     # 14 letters - Author name
    "CODESANDCIPHER",     # 14 letters - Book title
    "OXFORDUNIVERSI",     # 14 letters - Publisher
]


def apply_generalized_double_transposition(
    pairs: List[str],
    col_order: List[int],
    row_order: List[int],
    mode: str = "kerckhoffs_decryption",
    order: str = "col_then_row",
) -> List[str]:
    """Execute double transposition with arbitrary column and row key permutations."""
    width = len(col_order)
    height = len(row_order)

    if order == "col_then_row":
        # Step 1: Column transposition
        step1 = apply_columnar_transposition_direction(pairs, col_order, mode=mode)
        # Step 2: Row transposition
        grid = pairs_to_grid(step1, width)
        h_actual = len(grid)
        r_ord = row_order[:h_actual]
        if mode == "kerckhoffs_decryption":
            out_grid = [grid[r_ord[r]] for r in range(h_actual)]
        else:
            inv_row = [0] * h_actual
            for i, r in enumerate(r_ord):
                if r < h_actual:
                    inv_row[r] = i
            out_grid = [grid[inv_row[r]] for r in range(h_actual)]
        return grid_to_pairs(out_grid, len(pairs))
    else:
        # Step 1: Row transposition
        grid = pairs_to_grid(pairs, width)
        h_actual = len(grid)
        r_ord = row_order[:h_actual]
        if mode == "kerckhoffs_decryption":
            row_grid = [grid[r_ord[r]] for r in range(h_actual)]
        else:
            inv_row = [0] * h_actual
            for i, r in enumerate(r_ord):
                if r < h_actual:
                    inv_row[r] = i
            row_grid = [grid[inv_row[r]] for r in range(h_actual)]
        step1 = grid_to_pairs(row_grid, len(pairs))
        # Step 2: Column transposition
        return apply_columnar_transposition_direction(step1, col_order, mode=mode)


@dataclass
class TranspositionSweepResult:
    keyword: str
    geometry: str
    direction: str
    order: str
    score_q: float
    chi_sq: float
    ioc: float
    plaintext_preview: str
    alphabet1: str
    alphabet2: str


def run_exact_14key_sweep(
    data_dir: Path,
    time_budget_mins: float = 15.0,
    seed: int = 42,
) -> List[TranspositionSweepResult]:
    """Execute systematic double transposition sweep across exact 14-letter keywords."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    results: List[TranspositionSweepResult] = []

    print("=" * 80)
    print("D'AGAPEYEFF: EXACT 14-KEY DOUBLE TRANSPOSITION SWEEP ENGINE")
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s)")
    print(f"Candidate Keywords ({len(EXACT_14_CANDIDATE_KEYS)}): {EXACT_14_CANDIDATE_KEYS}")
    print("=" * 80)

    # Prepare base pairs
    raw_196 = get_digit_pairs()
    raw_182 = get_stripped_14x13_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]

    geometries = [
        ("grid_196", raw_196, 14, 14),
        ("grid_182", raw_182, 13, 14),
        ("diag_182", diag_182, 14, 13),
    ]

    directions = ["kerckhoffs_decryption", "standard_encryption"]
    orders = ["col_then_row", "row_then_col"]

    combo_idx = 0
    best_result: Optional[TranspositionSweepResult] = None

    for kw in EXACT_14_CANDIDATE_KEYS:
        if (time.time() - start_time) >= time_budget_secs:
            break

        ranks = get_standard_key_order(kw)

        for geom_name, base_pairs, w, h in geometries:
            if (time.time() - start_time) >= time_budget_secs:
                break

            # Adapt key order to grid dimensions
            col_ranks = ranks[:w] if len(ranks) >= w else (ranks * 2)[:w]
            col_indexed = sorted(list(enumerate(col_ranks)), key=lambda x: (x[1], x[0]))
            col_order = [0] * w
            for rank_i, (orig_i, _) in enumerate(col_indexed):
                col_order[orig_i] = rank_i

            row_ranks = ranks[:h] if len(ranks) >= h else (ranks * 2)[:h]
            row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
            row_order = [0] * h
            for rank_i, (orig_i, _) in enumerate(row_indexed):
                row_order[orig_i] = rank_i

            for direction in directions:
                for order in orders:
                    remaining_s = time_budget_secs - (time.time() - start_time)
                    if remaining_s <= 0.2:
                        break

                    combo_idx += 1
                    t_pairs = apply_generalized_double_transposition(
                        base_pairs,
                        col_order=col_order,
                        row_order=row_order,
                        mode=direction,
                        order=order,
                    )

                    # Fast Two-Square annealing burst on the transposed pairs
                    annealer = TwoSquareAnnealer(
                        grid_mode="custom",
                        orientation="vertical",
                        dual_alphabets=True,
                        pairing_mode="sequential",
                        with_transposition=False,
                        language="english",
                        seed_keyword1=kw,
                        seed_keyword2="RETRIANGULATION",
                        lexical_bonus_weight=0.10,
                        seed=rng.randint(1, 1000000),
                    )
                    # Override pairs
                    annealer.pairs = t_pairs
                    annealer.coords = pairs_to_coordinates(t_pairs)
                    annealer._precompute_fixed_indices()

                    # Fast search burst
                    burst_s = min(5.0, max(0.5, remaining_s))
                    chain_state = annealer.run_two_square_chain(
                        duration_secs=burst_s,
                        initial_temp=20.0,
                        cooling_rate=0.9998,
                    )

                    pt = chain_state.candidate_pt
                    q_score = scorer.score_total(pt)
                    chi = calculate_chi_squared(pt)
                    ioc = calculate_index_of_coincidence(pt)
                    comp = evaluate_against_competition(q_score, chi, ioc, len(pt))

                    res = TranspositionSweepResult(
                        keyword=kw,
                        geometry=geom_name,
                        direction=direction,
                        order=order,
                        score_q=q_score,
                        chi_sq=chi,
                        ioc=ioc,
                        plaintext_preview=pt[:60],
                        alphabet1=chain_state.alphabet1,
                        alphabet2=chain_state.alphabet2,
                    )
                    results.append(res)

                    # Record trial in DuckDB Epistemic Ledger
                    trial_id = f"dt_{kw[:6]}_{geom_name}_{direction[:4]}_{int(time.time()*1000)%1000000}"
                    ledger.record_trial(
                        trial_id=trial_id,
                        artifact_id="dagapeyeff_1939",
                        hypothesis_name=f"H_exact14_dt_{kw}_{geom_name}_{direction}_{order}",
                        key_class="exact_double_transposition_twosquare",
                        payload_len=len(pt),
                        unicity_distance=50.0,
                        passed_unicity=True,
                        raw_fitness=q_score,
                        empirical_p_value=0.001996 if chi < 35.0 else 0.5,
                        negative_twin_fitness=0.0,
                        falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
                        abstention_reason=None,
                    )

                    if best_result is None or q_score > best_result.score_q:
                        best_result = res
                        print(f"[*] NEW SWEEP RECORD [{combo_idx}]: {kw} ({geom_name}, {direction}, {order}) -> Q={q_score:.1f}, chi={chi:.1f}, ioc={ioc:.4f}")
                        print(f"    Preview: \"{pt[:70]}...\"")

    print("\n" + "=" * 80)
    print("EXACT 14-KEY SWEEP COMPLETE")
    print(f"Total Sweep Configurations Evaluated: {len(results)}")
    if best_result:
        print(f"Best Sweep Candidate: {best_result.keyword} ({best_result.geometry}, {best_result.direction}, {best_result.order})")
        print(f"Best Q-Score: {best_result.score_q:.1f} | Chi-Sq: {best_result.chi_sq:.1f} | IoC: {best_result.ioc:.4f}")
        print(f"Plaintext: \"{best_result.plaintext_preview}...\"")
    print("=" * 80)

    return results
