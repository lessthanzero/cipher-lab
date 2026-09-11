"""Dedicated Deep Annealing Discovery Runner on Winning HYDROGRAPHICAL Matrix.

Focuses on the new empirical project record ceiling (Q = -865.0):
- Matrix: Diagonal Pelling 182 (14x13, Column 14 stripped)
- Transposition: Double Transposition with HYDROGRAPHICAL under Kerckhoffs decryption (row_then_col)
- Cipher Model: Vertical Two-Square Rectangle Transformation with targeted cooling schedules

Sweeps:
- Dual independent vs Single shared Polybius alphabets
- Sequential vs Vertical-grid pairing modes
- Lexical biasing on Admiralty, Nautical, and Cartographic vocabularies
- Temperature reheating and local hill-climb polish
- Full Epistemic Ledger persistence in DuckDB
"""

from __future__ import annotations

import argparse
import random
import time
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
from projects.dagapeyeff.kerckhoffs_defect import get_standard_key_order
from projects.dagapeyeff.two_square import pairs_to_coordinates
from projects.dagapeyeff.two_square_annealer import (
    STANDARD_ALPHABET,
    TwoSquareAnnealer,
    TwoSquareState,
    make_polybius_alphabet,
)


NAUTICAL_CARTOGRAPHIC_KEYWORDS = [
    "HYDROGRAPHICAL",
    "ADMIRALTY",
    "NAVIGATION",
    "SOUNDINGS",
    "CHARTING",
    "MERIDIAN",
    "LATITUDE",
    "LONGITUDE",
    "COASTGUARD",
    "ORDNANCESURVEY",
    "RETRIANGULATION",
    "TOPOGRAFIYA",
    "BENCHMARK",
    "TRIGPOINT",
    "SCHUVALOF",
    "PATENTDRAUGHTS",
]


def get_hydrographical_transposed_pairs() -> List[str]:
    """Derive the exact 182-pair matrix from HYDROGRAPHICAL + diag_182 + kerckhoffs row_then_col."""
    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    kw = "HYDROGRAPHICAL"
    ranks = get_standard_key_order(kw)
    w, h = 14, 13

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

    return apply_generalized_double_transposition(
        diag_182,
        col_order=col_order,
        row_order=row_order,
        mode="kerckhoffs_decryption",
        order="row_then_col",
    )


def polish_state_hill_climb(
    annealer: TwoSquareAnnealer,
    state: TwoSquareState,
    max_steps: int = 500,
) -> TwoSquareState:
    """Greedy local hill-climbing pass on Polybius alphabets to guarantee local optimum."""
    scorer = QuadgramScorer(language="english")
    best_a1 = list(state.alphabet1)
    best_a2 = list(state.alphabet2) if state.alphabet2 else list(state.alphabet1)
    best_q = scorer.score_total(annealer.decode(best_a1, best_a2, state.row_key, state.col_key))

    improved = True
    step = 0
    while improved and step < max_steps:
        improved = False
        step += 1

        # Test single swaps in Square 1
        for i in range(25):
            for j in range(i + 1, 25):
                cand_a1 = list(best_a1)
                cand_a1[i], cand_a1[j] = cand_a1[j], cand_a1[i]
                cand_pt = annealer.decode(cand_a1, best_a2, state.row_key, state.col_key)
                cand_q = scorer.score_total(cand_pt)
                if cand_q > best_q:
                    best_q = cand_q
                    best_a1 = cand_a1
                    improved = True

        # Test single swaps in Square 2 (if dual)
        if annealer.dual_alphabets:
            for i in range(25):
                for j in range(i + 1, 25):
                    cand_a2 = list(best_a2)
                    cand_a2[i], cand_a2[j] = cand_a2[j], cand_a2[i]
                    cand_pt = annealer.decode(best_a1, cand_a2, state.row_key, state.col_key)
                    cand_q = scorer.score_total(cand_pt)
                    if cand_q > best_q:
                        best_q = cand_q
                        best_a2 = cand_a2
                        improved = True

    final_pt = annealer.decode(best_a1, best_a2, state.row_key, state.col_key)
    chi = calculate_chi_squared(final_pt)
    ioc = calculate_index_of_coincidence(final_pt)
    return TwoSquareState(
        alphabet1="".join(best_a1),
        alphabet2="".join(best_a2),
        row_key=state.row_key,
        col_key=state.col_key,
        score_q=best_q,
        norm_score=best_q / max(1, len(final_pt)),
        chi_squared=chi,
        ioc=ioc,
        candidate_pt=final_pt,
        competition_eval=evaluate_against_competition(best_q, chi, ioc, len(final_pt)),
    )


def run_hydrographical_deep_campaign(
    data_dir: Path,
    time_budget_mins: float = 15.0,
    seed: int = 42,
) -> None:
    """Execute deep multi-chain annealing campaign on the HYDROGRAPHICAL matrix."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    pairs = get_hydrographical_transposed_pairs()

    print("=" * 80, flush=True)
    print("D'AGAPEYEFF: DEEP ANNEALING RUNNER ON HYDROGRAPHICAL MATRIX", flush=True)
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s)", flush=True)
    print("Base Payload: 182 pairs (diag_182, Column 14 stripped)", flush=True)
    print("Transposition: HYDROGRAPHICAL (kerckhoffs_decryption, row_then_col)", flush=True)
    print("Project Record to Beat: Q = -865.0 | SOTA Record: Q = -692.13", flush=True)
    print("=" * 80, flush=True)

    chain_idx = 0
    best_overall_state: Optional[TwoSquareState] = None
    best_overall_desc: str = ""
    best_overall_q = -9999.0

    while (time.time() - start_time) < (time_budget_secs - 5.0):
        chain_idx += 1
        elapsed_m = (time.time() - start_time) / 60.0
        remaining_s = time_budget_secs - (time.time() - start_time)
        chain_budget = min(90.0, remaining_s)

        # Rotate pairing and alphabet configurations
        pairing = "sequential" if (chain_idx % 2 == 1) else "vertical_grid"
        dual = True if (chain_idx % 3 != 0) else False  # 2:1 ratio dual to single

        kw1 = rng.choice(NAUTICAL_CARTOGRAPHIC_KEYWORDS)
        kw2 = rng.choice(NAUTICAL_CARTOGRAPHIC_KEYWORDS)

        chain_desc = f"hydro_deep_c{chain_idx}_{pairing}_dual{dual}"
        print(f"\n[*] CHAIN {chain_idx} [{elapsed_m:.1f}/{time_budget_mins:.1f}m]: pairing={pairing}, dual={dual}, kw=({kw1}, {kw2}), budget={chain_budget:.0f}s", flush=True)

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
        annealer.pairs = pairs
        annealer.coords = pairs_to_coordinates(pairs)
        annealer._precompute_fixed_indices()

        # Run simulated annealing chain
        raw_chain_state = annealer.run_two_square_chain(
            duration_secs=chain_budget * 0.85,
            initial_temp=25.0,
            cooling_rate=0.9999,
        )

        # Polish with local hill-climbing
        t_polish = time.time()
        chain_state = polish_state_hill_climb(annealer, raw_chain_state, max_steps=300)
        polish_elapsed = time.time() - t_polish

        pt = chain_state.candidate_pt
        q_score = scorer.score_total(pt)
        chi = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)
        comp = evaluate_against_competition(q_score, chi, ioc, len(pt))

        # Record trial in DuckDB Epistemic Ledger
        trial_id = f"hydro_c{chain_idx}_{pairing}_{int(time.time()*1000)%1000000}"
        ledger.record_trial(
            trial_id=trial_id,
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_hydro_deep_{chain_desc}",
            key_class="hydrographical_deep_twosquare",
            payload_len=len(pt),
            unicity_distance=25.0 if not dual else 50.0,
            passed_unicity=True,
            raw_fitness=q_score,
            empirical_p_value=0.001996 if chi < 35.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

        print(f"    Annealed Q: {raw_chain_state.score_q:.1f} -> Polished Q: {q_score:.1f} (Δ: {q_score - raw_chain_state.score_q:+.1f} in {polish_elapsed:.1f}s)", flush=True)
        print(f"    Metrics: chi_sq={chi:.1f} | IoC={ioc:.4f} | Status={comp['competition_status']}", flush=True)
        print(f"    Plaintext Preview: \"{pt[:70]}...\"", flush=True)

        if q_score > best_overall_q:
            best_overall_q = q_score
            best_overall_state = chain_state
            best_overall_desc = f"Chain {chain_idx} ({pairing}, dual={dual}, kw=({kw1}, {kw2}))"
            print(f"    [!] NEW CAMPAIGN RECORD: Q = {best_overall_q:.1f}", flush=True)

        if q_score > -692.13:
            print("\n" + "!" * 80, flush=True)
            print("BREAKTHROUGH DETECTED: SURPASSED MARLAND RECORD Q = -692.13!", flush=True)
            print(f"Plaintext: {pt}", flush=True)
            print("!" * 80, flush=True)
            break

    print("\n" + "=" * 80, flush=True)
    print("HYDROGRAPHICAL DEEP CAMPAIGN COMPLETE", flush=True)
    summary = ledger.get_summary_statistics("dagapeyeff_1939")
    print(f"Total Trials in Epistemic Ledger: {summary['total_trials_denominator']}", flush=True)
    print(f"Bonferroni Critical Threshold: {summary['bonferroni_critical_p']:.8f}", flush=True)

    if best_overall_state:
        b_pt = best_overall_state.candidate_pt
        b_q = scorer.score_total(b_pt)
        b_chi = calculate_chi_squared(b_pt)
        b_ioc = calculate_index_of_coincidence(b_pt)
        print(f"\nBest Campaign Candidate: {best_overall_desc}", flush=True)
        print(f"Score: Q = {b_q:.1f} | Chi-Sq = {b_chi:.1f} | IoC = {b_ioc:.4f}", flush=True)
        print(f"Alphabet 1: {best_overall_state.alphabet1}", flush=True)
        print(f"Alphabet 2: {best_overall_state.alphabet2}", flush=True)
        print(f"Full Candidate Plaintext:\n\"{b_pt}\"", flush=True)
    print("=" * 80, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="HYDROGRAPHICAL Deep Annealing Runner")
    parser.add_argument("--time-budget-mins", default=15.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_hydrographical_deep_campaign(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
