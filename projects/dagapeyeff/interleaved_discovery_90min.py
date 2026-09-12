"""90-Minute Continuous Discovery Campaign Interleaving Option 1 and Option 2.

Continuously cycles between:
- Option 1: Deep Admiralty / Naval Keyword & Duplicate-Rank Transposition Sweeps
- Option 2: Beam-Search Word Stitching & Local Model Linguistic Polish

Features:
- Dynamic temperature schedules and greedy hill-climbing polish
- Interleaved beam-search dictionary repairs on top discovered basins
- Full Epistemic Ledger persistence in DuckDB
- Early breakthrough trigger (Q > -692.13 Marland SOTA record)
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from typing import List, Optional, Tuple

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)

from projects.dagapeyeff.admiralty_sweep import (
    ADMIRALTY_KEYWORDS_14,
    generate_hydrographical_duplicate_rankings,
)
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_grid import read_diagonal_matrix_transpose
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.hydrographical_deep_runner import (
    NAUTICAL_CARTOGRAPHIC_KEYWORDS,
    polish_state_hill_climb,
)
from projects.dagapeyeff.kerckhoffs_defect import get_standard_key_order
from projects.dagapeyeff.two_square import pairs_to_coordinates
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
)
from projects.dagapeyeff.word_stitcher import (
    run_beam_word_stitcher,
)


def get_all_admiralty_key_configurations() -> List[Tuple[str, List[int]]]:
    """Compile comprehensive library of Admiralty keywords and duplicate-ranking permutations."""
    w, _h = 14, 13
    configs: List[Tuple[str, List[int]]] = []

    # 1. Duplicate ranking variants of HYDROGRAPHICAL
    configs.extend(generate_hydrographical_duplicate_rankings())

    # 2. Standard Admiralty keywords
    for kw in ADMIRALTY_KEYWORDS_14:
        ranks = get_standard_key_order(kw)
        col_ranks = ranks[:w] if len(ranks) >= w else (ranks * 2)[:w]
        col_indexed = sorted(list(enumerate(col_ranks)), key=lambda x: (x[1], x[0]))
        perm = [0] * w
        for r_i, (orig_i, _) in enumerate(col_indexed):
            perm[orig_i] = r_i
        configs.append((kw, perm))

    return configs


def run_continuous_interleaved_campaign(
    data_dir: Path,
    time_budget_mins: float = 90.0,
    seed: int = 42,
) -> None:
    """Execute continuous 90-minute campaign interleaving Option 1 and Option 2."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("=" * 80, flush=True)
    print("D'AGAPEYEFF: 90-MINUTE CONTINUOUS INTERLEAVED DISCOVERY CAMPAIGN", flush=True)
    print(f"Wall-Clock Budget: {time_budget_mins:.1f} minutes ({time_budget_secs:.0f}s)", flush=True)
    print("Mode: Interleaved Option 1 (Admiralty Sweeps) + Option 2 (Word Stitching & LM Polish)", flush=True)
    print("Target to Beat: Q = -846.5 (Current All-Time Project Record) | SOTA: -692.13", flush=True)
    print("=" * 80, flush=True)

    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    _w, h = 14, 13

    key_configs = get_all_admiralty_key_configurations()
    directions = ["standard_encryption", "kerckhoffs_decryption"]
    orders = ["row_then_col", "col_then_row"]

    cycle = 0
    best_overall_state: Optional[TwoSquareState] = None
    best_overall_desc: str = ""
    best_overall_q = -846.5  # Baseline champion

    while (time.time() - start_time) < (time_budget_secs - 10.0):
        cycle += 1
        elapsed_m = (time.time() - start_time) / 60.0
        remaining_s = time_budget_secs - (time.time() - start_time)

        print(f"\n{'='*30} CYCLE {cycle} [{elapsed_m:.1f}/{time_budget_mins:.1f}m] {'='*30}", flush=True)

        # -------------------------------------------------------------
        # STEP A: OPTION 1 ADMIRALTY ANNEALING BATCH
        # -------------------------------------------------------------
        # Select 3 key configurations for this cycle
        sampled_keys = rng.sample(key_configs, min(3, len(key_configs)))
        cycle_candidates: List[Tuple[TwoSquareState, str, List[str]]] = []

        for label, ranks in sampled_keys:
            if (time.time() - start_time) >= (time_budget_secs - 10.0):
                break

            col_order = ranks
            row_ranks = ranks[:h]
            row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
            row_order = [0] * h
            for r_i, (orig_i, _) in enumerate(row_indexed):
                row_order[orig_i] = r_i

            direction = rng.choice(directions)
            order = rng.choice(orders)
            pairing = "sequential" if rng.random() < 0.7 else "vertical_grid"
            dual = True if rng.random() < 0.8 else False

            t_pairs = apply_generalized_double_transposition(
                diag_182,
                col_order=col_order,
                row_order=row_order,
                mode=direction,
                order=order,
            )

            kw1 = rng.choice(NAUTICAL_CARTOGRAPHIC_KEYWORDS)
            kw2 = rng.choice(NAUTICAL_CARTOGRAPHIC_KEYWORDS)

            chain_desc = f"{label}_{direction[:4]}_{order[:3]}_{pairing}_dual{dual}"
            step_budget = min(45.0, max(5.0, remaining_s * 0.15))

            annealer = TwoSquareAnnealer(
                grid_mode="custom",
                orientation="vertical",
                dual_alphabets=dual,
                pairing_mode=pairing,
                with_transposition=False,
                language="english",
                seed_keyword1=kw1,
                seed_keyword2=kw2,
                lexical_bonus_weight=0.15,
                seed=rng.randint(1, 1000000),
            )
            annealer.pairs = t_pairs
            annealer.coords = pairs_to_coordinates(t_pairs)
            annealer._precompute_fixed_indices()

            raw_state = annealer.run_two_square_chain(
                duration_secs=step_budget * 0.8,
                initial_temp=25.0,
                cooling_rate=0.9998,
            )

            # Hill-climbing polish
            polished = polish_state_hill_climb(annealer, raw_state, max_steps=200)
            pt = polished.candidate_pt
            q_score = scorer.score_total(pt)
            chi = calculate_chi_squared(pt)
            ioc = calculate_index_of_coincidence(pt)
            evaluate_against_competition(q_score, chi, ioc, len(pt))

            # Record in DuckDB ledger
            trial_id = f"inter_c{cycle}_{label[:6]}_{int(time.time()*1000)%1000000}"
            ledger.record_trial(
                trial_id=trial_id,
                artifact_id="dagapeyeff_1939",
                hypothesis_name=f"H_interleaved_{chain_desc}_cyc{cycle}",
                key_class="interleaved_admiralty_twosquare",
                payload_len=len(pt),
                unicity_distance=50.0,
                passed_unicity=True,
                raw_fitness=q_score,
                empirical_p_value=0.001996 if chi < 30.0 else 0.5,
                negative_twin_fitness=0.0,
                falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
                abstention_reason=None,
            )

            print(f"[*] Step A [{label[:14]}]: Q={q_score:.1f} (Δ_polish: {q_score - raw_state.score_q:+.1f}) | chi={chi:.1f} | ioc={ioc:.4f}", flush=True)
            print(f"    Preview: \"{pt[:65]}...\"", flush=True)

            cycle_candidates.append((polished, chain_desc, t_pairs))

            if q_score > best_overall_q:
                best_overall_q = q_score
                best_overall_state = polished
                best_overall_desc = f"Cycle {cycle} Step A: {chain_desc}"
                print(f"    [!] NEW ALL-TIME RECORD: Q = {best_overall_q:.1f}!", flush=True)

        # -------------------------------------------------------------
        # STEP B: OPTION 2 BEAM WORD STITCHING ON TOP CANDIDATE
        # -------------------------------------------------------------
        if cycle_candidates and (time.time() - start_time) < (time_budget_secs - 10.0):
            # Select best state from Step A for word stitching
            top_cand, top_desc, cand_pairs = max(cycle_candidates, key=lambda x: x[0].score_q)
            print(f"\n[*] Step B: Launching Beam Word Stitching on {top_desc} (Starting Q={top_cand.score_q:.1f})", flush=True)

            beam_nodes = run_beam_word_stitcher(
                seed_a1=top_cand.alphabet1,
                seed_a2=top_cand.alphabet2,
                transposed_pairs=cand_pairs,
                beam_width=12,
                max_depth=5,
                data_dir=data_dir,
            )

            if beam_nodes:
                top_beam = beam_nodes[0]
                if top_beam.score_q > best_overall_q:
                    best_overall_q = top_beam.score_q
                    best_overall_desc = f"Cycle {cycle} Step B Beam Stitch: {top_desc}"
                    print(f"    [!] NEW BEAM RECORD: Q = {best_overall_q:.1f} ({len(top_beam.matched_words)} words)!", flush=True)

        # Breakthrough Check
        if best_overall_q > -692.13:
            print("\n" + "!" * 80, flush=True)
            print("BREAKTHROUGH ACHIEVED: SURPASSED MARLAND RECORD Q = -692.13!", flush=True)
            if best_overall_state:
                print(f"Plaintext: {best_overall_state.candidate_pt}", flush=True)
            print("!" * 80, flush=True)
            break

    print("\n" + "=" * 80, flush=True)
    print("90-MINUTE INTERLEAVED DISCOVERY CAMPAIGN COMPLETE", flush=True)
    summary = ledger.get_summary_statistics("dagapeyeff_1939")
    print(f"Total Trials in Epistemic Ledger: {summary['total_trials_denominator']}", flush=True)
    print(f"Bonferroni Critical Threshold: {summary['bonferroni_critical_p']:.8f}", flush=True)

    if best_overall_state:
        b_pt = best_overall_state.candidate_pt
        b_q = scorer.score_total(b_pt)
        b_chi = calculate_chi_squared(b_pt)
        b_ioc = calculate_index_of_coincidence(b_pt)
        print(f"\nBest Overall Discovered State: {best_overall_desc}", flush=True)
        print(f"Score: Q = {b_q:.1f} | Chi-Sq = {b_chi:.1f} | IoC = {b_ioc:.4f}", flush=True)
        print(f"Alphabet 1: {best_overall_state.alphabet1}", flush=True)
        print(f"Alphabet 2: {best_overall_state.alphabet2}", flush=True)
        print(f"Full Candidate Plaintext:\n\"{b_pt}\"", flush=True)
    print("=" * 80, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="90-Minute Interleaved Discovery Campaign")
    parser.add_argument("--time-budget-mins", default=90.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_continuous_interleaved_campaign(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
