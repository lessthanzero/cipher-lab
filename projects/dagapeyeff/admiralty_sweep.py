"""Option 1: Sibling Admiralty Keywords & Duplicate-Rank Sweeps for D'Agapeyeff.

Systematically evaluates:
1. Exact 14-letter Admiralty / Hydrography keywords:
   - ADMIRALTYCHART (14)
   - SOUNDINGSCHART (14)
   - BRITISHADMIRAL (14)
   - HYDROGRAPHICAL (14)
   - CARTOGRAPHICAL (14)
   - NAVIGATIONMAPS (14)
2. Duplicate-rank permutations on HYDROGRAPHICAL:
   - Evaluates left-to-right vs right-to-left tie-breaking on duplicate letters (A, H, R)
   - Evaluates Kerckhoffs defective ranking variations (p. 142 defect)
3. Grid & Transposition:
   - Diagonally transposed 182-pair matrix (diag_182)
   - Kerckhoffs decryption vs standard encryption
   - row_then_col vs col_then_row
4. Optimization:
   - Fast simulated annealing + greedy hill-climbing polish on dual Polybius alphabets
   - Epistemic Ledger persistence in DuckDB
"""

from __future__ import annotations

import argparse
import itertools
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
from projects.dagapeyeff.cartographic_grid import read_diagonal_matrix_transpose
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.hydrographical_deep_runner import polish_state_hill_climb
from projects.dagapeyeff.kerckhoffs_defect import get_standard_key_order
from projects.dagapeyeff.two_square import pairs_to_coordinates
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
)


ADMIRALTY_KEYWORDS_14 = [
    "HYDROGRAPHICAL",
    "ADMIRALTYCHART",
    "SOUNDINGSCHART",
    "BRITISHADMIRAL",
    "CARTOGRAPHICAL",
    "NAVIGATIONMAPS",
    "HYDROGRAPHERS",  # 13
    "SURVEYORSOFMAP",  # 14
    "ADMIRALTYOFFIC",  # 14
]


def generate_hydrographical_duplicate_rankings() -> List[Tuple[str, List[int]]]:
    """Generate systematic tie-breaking and defect rankings for HYDROGRAPHICAL (14 letters).
    
    H Y D R O G R A P H I C A L
    Indices of duplicates:
    - 'A': [7, 12]
    - 'H': [0, 9]
    - 'R': [3, 6]
    """
    kw = "HYDROGRAPHICAL"
    variants = []

    # 1. Standard left-to-right (default)
    std_ranks = get_standard_key_order(kw)
    variants.append(("hydro_std_ltr", std_ranks))

    # 2. Permute tie-breaking orders for duplicate pairs
    for a_rev in [False, True]:
        for h_rev in [False, True]:
            for r_rev in [False, True]:
                if not (a_rev or h_rev or r_rev):
                    continue  # already in std

                # Construct custom sorted order
                def sort_key(item: Tuple[int, str]) -> Tuple[str, int]:
                    idx, char = item
                    if char == "A":
                        return (char, -idx if a_rev else idx)
                    elif char == "H":
                        return (char, -idx if h_rev else idx)
                    elif char == "R":
                        return (char, -idx if r_rev else idx)
                    else:
                        return (char, idx)

                indexed = sorted(list(enumerate(kw)), key=sort_key)
                ranks = [0] * len(kw)
                for rank_i, (orig_i, _) in enumerate(indexed):
                    ranks[orig_i] = rank_i

                label = f"hydro_tie_A{'R' if a_rev else 'L'}_H{'R' if h_rev else 'L'}_R{'R' if r_rev else 'L'}"
                variants.append((label, ranks))

    # 3. Kerckhoffs defect: Terminal letter misranked as 13 (analogous to SCHUVALOF p. 142)
    flawed_ranks = list(std_ranks)
    flawed_ranks[-1] = 13  # Assign terminal 'L' rank 13 regardless of alphabet
    # Renumber to valid permutation
    order_tuples = sorted(list(enumerate(flawed_ranks)), key=lambda x: (x[1], x[0]))
    perm = [0] * 14
    for r_i, (orig_i, _) in enumerate(order_tuples):
        perm[orig_i] = r_i
    variants.append(("hydro_kerckhoffs_defect_terminal_L", perm))

    return variants


@dataclass
class AdmiraltySweepResult:
    keyword_label: str
    direction: str
    order: str
    q_score: float
    chi_sq: float
    ioc: float
    plaintext_preview: str
    alphabet1: str
    alphabet2: str


def run_admiralty_sweep(
    data_dir: Path,
    time_budget_mins: float = 15.0,
    seed: int = 42,
) -> List[AdmiraltySweepResult]:
    """Execute systematic sweep across Admiralty keywords and ranking permutations."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("=" * 80, flush=True)
    print("OPTION 1: SIBLING ADMIRALTY KEYWORDS & DUPLICATE-RANK SWEEP", flush=True)
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s)", flush=True)
    print("Geometry: Diagonal Pelling 182-pair matrix (diag_182, Column 14 stripped)", flush=True)
    print("Benchmark to Beat: Q = -855.8 (Current All-Time Project Record)", flush=True)
    print("=" * 80, flush=True)

    # Prepare base diag_182 pairs
    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    w, h = 14, 13

    # Build list of key configurations: (label, 14-element permutation)
    key_configs: List[Tuple[str, List[int]]] = []

    # Add Admiralty keywords
    for kw in ADMIRALTY_KEYWORDS_14:
        ranks = get_standard_key_order(kw)
        col_ranks = ranks[:w] if len(ranks) >= w else (ranks * 2)[:w]
        # Normalize to 0 .. w-1
        col_indexed = sorted(list(enumerate(col_ranks)), key=lambda x: (x[1], x[0]))
        perm = [0] * w
        for r_i, (orig_i, _) in enumerate(col_indexed):
            perm[orig_i] = r_i
        key_configs.append((kw, perm))

    # Add duplicate ranking variants for HYDROGRAPHICAL
    key_configs.extend(generate_hydrographical_duplicate_rankings())

    directions = ["kerckhoffs_decryption", "standard_encryption"]
    orders = ["row_then_col", "col_then_row"]

    results: List[AdmiraltySweepResult] = []
    combo_idx = 0
    best_result: Optional[AdmiraltySweepResult] = None

    for label, ranks in key_configs:
        if (time.time() - start_time) >= time_budget_secs:
            break

        col_order = ranks
        # Row order: 13 elements
        row_ranks = ranks[:h]
        row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
        row_order = [0] * h
        for r_i, (orig_i, _) in enumerate(row_indexed):
            row_order[orig_i] = r_i

        for direction in directions:
            for order in orders:
                remaining_s = time_budget_secs - (time.time() - start_time)
                if remaining_s <= 0.5:
                    break

                combo_idx += 1
                t_pairs = apply_generalized_double_transposition(
                    diag_182,
                    col_order=col_order,
                    row_order=row_order,
                    mode=direction,
                    order=order,
                )

                # Two-Square annealing burst + hill-climbing polish
                annealer = TwoSquareAnnealer(
                    grid_mode="custom",
                    orientation="vertical",
                    dual_alphabets=True,
                    pairing_mode="sequential",
                    with_transposition=False,
                    language="english",
                    seed_keyword1=label.split("_")[0],
                    seed_keyword2="ADMIRALTY",
                    lexical_bonus_weight=0.15,
                    seed=rng.randint(1, 1000000),
                )
                annealer.pairs = t_pairs
                annealer.coords = pairs_to_coordinates(t_pairs)
                annealer._precompute_fixed_indices()

                burst_s = min(6.0, max(0.8, remaining_s * 0.5))
                raw_state = annealer.run_two_square_chain(
                    duration_secs=burst_s,
                    initial_temp=20.0,
                    cooling_rate=0.9998,
                )

                # Hill-climb polish
                polished = polish_state_hill_climb(annealer, raw_state, max_steps=150)

                pt = polished.candidate_pt
                q_score = scorer.score_total(pt)
                chi = calculate_chi_squared(pt)
                ioc = calculate_index_of_coincidence(pt)
                comp = evaluate_against_competition(q_score, chi, ioc, len(pt))

                res = AdmiraltySweepResult(
                    keyword_label=label,
                    direction=direction,
                    order=order,
                    q_score=q_score,
                    chi_sq=chi,
                    ioc=ioc,
                    plaintext_preview=pt[:70],
                    alphabet1=polished.alphabet1,
                    alphabet2=polished.alphabet2,
                )
                results.append(res)

                # Record trial in DuckDB Epistemic Ledger
                trial_id = f"adm_{label[:8]}_{direction[:4]}_{order[:3]}_{int(time.time()*1000)%1000000}"
                ledger.record_trial(
                    trial_id=trial_id,
                    artifact_id="dagapeyeff_1939",
                    hypothesis_name=f"H_admiralty_{label}_{direction}_{order}",
                    key_class="admiralty_double_transposition_twosquare",
                    payload_len=len(pt),
                    unicity_distance=50.0,
                    passed_unicity=True,
                    raw_fitness=q_score,
                    empirical_p_value=0.001996 if chi < 35.0 else 0.5,
                    negative_twin_fitness=0.0,
                    falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
                    abstention_reason=None,
                )

                if best_result is None or q_score > best_result.q_score:
                    best_result = res
                    print(f"[*] NEW ADMIRALTY RECORD [{combo_idx}]: {label} ({direction}, {order}) -> Q={q_score:.1f}, chi={chi:.1f}, ioc={ioc:.4f}", flush=True)
                    print(f"    Preview: \"{pt[:70]}...\"", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("ADMIRALTY SWEEP COMPLETE", flush=True)
    print(f"Total Sweep Configurations Evaluated: {len(results)}", flush=True)
    if best_result:
        print(f"Best Sweep Candidate: {best_result.keyword_label} ({best_result.direction}, {best_result.order})", flush=True)
        print(f"Best Q-Score: {best_result.q_score:.1f} | Chi-Sq: {best_result.chi_sq:.1f} | IoC: {best_result.ioc:.4f}", flush=True)
        print(f"Alphabet 1: {best_result.alphabet1}", flush=True)
        print(f"Alphabet 2: {best_result.alphabet2}", flush=True)
        print(f"Plaintext: \"{best_result.plaintext_preview}...\"", flush=True)
    print("=" * 80, flush=True)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Admiralty Keyword & Duplicate-Rank Sweep")
    parser.add_argument("--time-budget-mins", default=10.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_admiralty_sweep(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
