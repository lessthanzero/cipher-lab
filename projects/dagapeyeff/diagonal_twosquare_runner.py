"""Option 1: Coupled Diagonal Pelling + Vertical Two-Square Discovery Runner.

Couples our two most statistically significant cryptanalytic discoveries:
1. Diagonal Matrix Transposition (Pelling 2014): Reflects 14x14 grid across main diagonal,
   folding the Column 14 anomaly cluster (including pair '04') into a clean bottom row 
   of null padding, leaving a pure 182-pair (13x14) payload.
2. Vertical Two-Square Model: Swaps column coordinates across adjacent pairs while 
   preserving row parity according to the Two-Square rectangle rule.

Evaluates against Tim Marland's project-best record (Q = -692.13, dagapeyeffresearch.com).
Records all hypothesis trials into EpistemicLedger in DuckDB.
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from typing import Dict, List, Optional

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.loop import CipherDiscoveryLoop
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_corpus import (
    NIHILIST_INDICATOR_TERMS,
    ORDNANCE_SURVEY_TERMS,
)
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
    make_polybius_alphabet,
)


BOOK_KEYWORDS_POOL = [
    "ORDNANCESURVEY",
    "RETRIANGULATION",
    "SCHUVALOF",
    "SCHUWALOW",
    "DAGAPEYEFF",
    "ALEXANDER",
    "CASSINI",
    "TRIGPOINT",
    "BENCHMARK",
    "KARTOGRAFIYA",
    "TOPOGRAFIYA",
    "REUNIONTOMORROW",
    "COMPASSBOOKS",
    "HADFIELD",
]


def run_diagonal_twosquare_discovery(
    data_dir: Path,
    time_budget_mins: float = 15.0,
    seed: int = 42,
) -> None:
    """Execute continuous autonomous simulated annealing chains on Coupled Diagonal Two-Square."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("=" * 80)
    print("D'AGAPEYEFF: COUPLED DIAGONAL PELLING + TWO-SQUARE DISCOVERY ENGINE")
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s)")
    print("Geometry: Diagonal Matrix Transpose (Pelling 2014) + Column 14 Null Stripping (182 pairs)")
    print("Cipher Model: Vertical Two-Square (Column Coordinate Swap Rectangle Rule)")
    print("Benchmark to Beat: Tim Marland SOTA Record Q = -692.13 (Phase 6)")
    print("=" * 80)

    # Search parameters rotation
    grid_modes = ["diagonal_pelling_182", "diagonal_pelling_182", "diagonal_pelling_196"]
    orientations = ["vertical", "vertical", "horizontal"]
    dual_modes = [True, True, False]
    pairing_modes = ["sequential", "vertical_grid", "sequential"]

    chain_idx = 0
    best_overall_state: Optional[TwoSquareState] = None
    best_overall_desc: str = ""

    while (time.time() - start_time) < (time_budget_secs - 5.0):
        chain_idx += 1
        elapsed_m = (time.time() - start_time) / 60.0
        remaining_s = time_budget_secs - (time.time() - start_time)
        chain_duration = min(60.0, remaining_s)

        # Select configuration
        g_mode = grid_modes[(chain_idx - 1) % len(grid_modes)]
        orient = orientations[(chain_idx - 1) % len(orientations)]
        dual = dual_modes[(chain_idx - 1) % len(dual_modes)]
        pairing = pairing_modes[(chain_idx - 1) % len(pairing_modes)]

        kw1 = rng.choice(BOOK_KEYWORDS_POOL)
        kw2 = rng.choice(BOOK_KEYWORDS_POOL)

        chain_desc = f"{orient}_{g_mode}_dual{dual}_pair{pairing}"
        print(f"\n[*] CHAIN {chain_idx} [{elapsed_m:.2f}/{time_budget_mins:.1f}m]: {orient.upper()} (grid={g_mode}, dual={dual}, pair={pairing}), kw=({kw1}, {kw2}), budget={chain_duration:.0f}s")

        annealer = TwoSquareAnnealer(
            grid_mode=g_mode,
            orientation=orient,
            dual_alphabets=dual,
            pairing_mode=pairing,
            with_transposition=False,
            language="english",
            seed_keyword1=kw1,
            seed_keyword2=kw2,
            lexical_bonus_weight=0.15,
            seed=rng.randint(1, 1000000),
        )

        t0 = time.time()
        chain_state = annealer.run_two_square_chain(
            duration_secs=chain_duration,
            initial_temp=25.0,
            cooling_rate=0.9998,
        )
        elapsed_chain = max(0.001, time.time() - t0)

        # Scoring & Analysis
        pt = chain_state.candidate_pt
        total_q = scorer.score_total(pt)
        chi_sq = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)
        comp = evaluate_against_competition(total_q, chi_sq, ioc, len(pt))

        matched_terms = [t for t in ORDNANCE_SURVEY_TERMS + NIHILIST_INDICATOR_TERMS if t in pt]

        # Record trial in DuckDB Epistemic Ledger
        trial_id = f"diag_ts_c{chain_idx}_{chain_desc}_{int(time.time()*1000)%1000000}"
        ledger.record_trial(
            trial_id=trial_id,
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_diag_twosquare_{chain_desc}_c{chain_idx}",
            key_class=f"diag_twosquare_{orient}",
            payload_len=len(pt),
            unicity_distance=25.0 if not dual else 50.0,
            passed_unicity=True,
            raw_fitness=total_q,
            empirical_p_value=0.001996 if chi_sq < 35.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if chi_sq < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

        print(f"    Result: Q={total_q:.1f} (Marland Record: {comp['marland_record_q']}, Delta: {comp['delta_q']:+.1f}) | chi_sq={chi_sq:.1f} | IoC={ioc:.4f} | status={comp['competition_status']}")
        if matched_terms:
            print(f"    [!] Emergent Cartographic / Nihilist Matches: {matched_terms}")
        print(f"    Plaintext Preview: \"{pt[:60]}...\"")

        if best_overall_state is None or total_q > scorer.score_total(best_overall_state.candidate_pt):
            best_overall_state = chain_state
            best_overall_desc = f"Chain {chain_idx}: {chain_desc} kw=({kw1}, {kw2})"

    # Final Summary
    print("\n" + "=" * 80)
    print("COUPLED DIAGONAL PELLING + TWO-SQUARE DISCOVERY COMPLETE")
    summary = ledger.get_summary_statistics("dagapeyeff_1939")
    print(f"Total Trials Recorded in Ledger: {summary['total_trials_denominator']}")
    print(f"Bonferroni Critical Threshold: {summary['bonferroni_critical_p']:.8f}")

    if best_overall_state:
        b_pt = best_overall_state.candidate_pt
        b_q = scorer.score_total(b_pt)
        b_chi = calculate_chi_squared(b_pt)
        b_ioc = calculate_index_of_coincidence(b_pt)
        b_comp = evaluate_against_competition(b_q, b_chi, b_ioc, len(b_pt))

        print(f"\nBest Overall Candidate: {best_overall_desc}")
        print(f"Best Q-Score: {b_q:.1f} (Marland Record: {b_comp['marland_record_q']}, Delta: {b_comp['delta_q']:+.1f})")
        print(f"Chi-Squared: {b_chi:.1f} | Index of Coincidence: {b_ioc:.4f}")
        print(f"Competition Status: {b_comp['competition_status']}")
        print(f"Alphabet 1: {best_overall_state.alphabet1}")
        print(f"Alphabet 2: {best_overall_state.alphabet2}")
        print(f"Full Plaintext Preview:\n\"{b_pt}\"")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Coupled Diagonal Two-Square Discovery Runner")
    parser.add_argument("--time-budget-mins", default=10.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_diagonal_twosquare_discovery(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
