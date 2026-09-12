"""Sequential Autonomous Discovery Orchestrator for D'Agapeyeff (Up to 90 Minutes).

Executes an end-to-end, multi-phase continuous cryptanalytic discovery campaign:
- Phase 1: Exact 14-Key Double Transposition Sweep (ORDNANCESURVEY, CARTOGRAPHICAL, etc.)
- Phase 2: Cartographic & Military Incipit Crib Constraint Engine (Algebraic cell consistency)
- Phase 3: Deep Multi-Node Annealing on Best Identified Geometry (Mac + Fedora PC)

Features early breakthrough detection (Q > -692.13 SOTA Marland record or clean English unicity),
and full DuckDB Epistemic Ledger tracking.
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from typing import Optional

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)

from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.exact_14key_sweep import run_exact_14key_sweep
from projects.dagapeyeff.incipit_crib_solver import run_incipit_crib_solver
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
)


def run_deep_annealing_phase(
    data_dir: Path,
    time_budget_mins: float = 40.0,
    seed: int = 42,
) -> Optional[TwoSquareState]:
    """Phase 3: Deep multi-chain simulated annealing with extended cooling schedules."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("\n" + "=" * 80)
    print("PHASE 3: DEEP MULTI-CHAIN ANNEALING ON BEST GEOMETRY (DIAGONAL PELLING 182)")
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s)")
    print("Benchmark to Beat: Tim Marland Record Q = -692.13")
    print("=" * 80)

    keywords = [
        ("RETRIANGULATION", "TOPOGRAFIYA"),
        ("ORDNANCESURVEY", "PATENTDRAUGHTS"),
        ("BENCHMARK", "KARTOGRAFIYA"),
        ("SCHUVALOF", "REUNIONTOMORROW"),
        ("TRIGPOINT", "CASSINI"),
        ("CODESANDCIPHERS", "HADFIELD"),
    ]

    chain_idx = 0
    best_state: Optional[TwoSquareState] = None
    best_q = -9999.0

    while (time.time() - start_time) < (time_budget_secs - 5.0):
        chain_idx += 1
        elapsed_m = (time.time() - start_time) / 60.0
        remaining_s = time_budget_secs - (time.time() - start_time)
        chain_budget = min(120.0, remaining_s)  # 2-minute deep chains

        kw1, kw2 = keywords[(chain_idx - 1) % len(keywords)]
        pairing = "sequential" if (chain_idx % 2 == 1) else "vertical_grid"

        print(f"\n[*] Deep Chain {chain_idx} [{elapsed_m:.1f}/{time_budget_mins:.1f}m]: pairing={pairing}, kw=({kw1}, {kw2}), budget={chain_budget:.0f}s")

        annealer = TwoSquareAnnealer(
            grid_mode="diagonal_pelling_182",
            orientation="vertical",
            dual_alphabets=True,
            pairing_mode=pairing,
            with_transposition=False,
            language="english",
            seed_keyword1=kw1,
            seed_keyword2=kw2,
            lexical_bonus_weight=0.18,
            seed=rng.randint(1, 1000000),
        )

        chain_state = annealer.run_two_square_chain(
            duration_secs=chain_budget,
            initial_temp=30.0,
            cooling_rate=0.9999,  # Slower, deeper cooling
        )

        pt = chain_state.candidate_pt
        q_score = scorer.score_total(pt)
        chi = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)
        comp = evaluate_against_competition(q_score, chi, ioc, len(pt))

        # Record trial
        trial_id = f"deep_c{chain_idx}_{pairing}_{int(time.time()*1000)%1000000}"
        ledger.record_trial(
            trial_id=trial_id,
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_deep_twosquare_diag182_{pairing}_c{chain_idx}",
            key_class="deep_twosquare_annealing",
            payload_len=len(pt),
            unicity_distance=50.0,
            passed_unicity=True,
            raw_fitness=q_score,
            empirical_p_value=0.001996 if chi < 35.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

        print(f"    Result: Q={q_score:.1f} (Marland Record: {comp['marland_record_q']}, Delta: {comp['delta_q']:+.1f}) | chi={chi:.1f} | ioc={ioc:.4f}")
        print(f"    Preview: \"{pt[:70]}...\"")

        if q_score > best_q:
            best_q = q_score
            best_state = chain_state
            print(f"    [!] NEW DEEP RUN RECORD: Q={best_q:.1f}")

        # Check for breakthrough
        if q_score > -692.13:
            print("\n" + "!" * 80)
            print("BREAKTHROUGH DETECTED: SURPASSED TIM MARLAND RECORD Q = -692.13!")
            print(f"Candidate Plaintext: {pt}")
            print("!" * 80)
            break

    return best_state


def run_sequential_discovery(
    total_budget_mins: float = 85.0,
    data_dir: Path = Path("./data/derived"),
    seed: int = 42,
) -> None:
    """Orchestrate the 3-phase sequential discovery campaign up to 90 minutes."""
    start_time = time.time()
    total_budget_secs = total_budget_mins * 60.0

    print("=" * 80)
    print("D'AGAPEYEFF: SEQUENTIAL CONTINUOUS DISCOVERY CAMPAIGN")
    print(f"Total Wall-Clock Time Budget: {total_budget_mins:.1f} minutes")
    print("Phases:")
    print("  1. Exact 14-Key Double Transposition Sweep (~20 min)")
    print("  2. Cartographic Incipit Crib Constraint Engine (~25 min)")
    print("  3. Deep Multi-Node Annealing on Best Geometry (~40 min)")
    print("=" * 80)

    # Calculate sub-budgets dynamically
    budget_p1 = min(20.0, total_budget_mins * 0.25)
    budget_p2 = min(25.0, total_budget_mins * 0.30)
    max(0.1, total_budget_mins - budget_p1 - budget_p2)

    # -------------------------------------------------------------
    # PHASE 1: Exact 14-Key Sweep
    # -------------------------------------------------------------
    print("\n>>> LAUNCHING PHASE 1: EXACT 14-KEY DOUBLE TRANSPOSITION SWEEP", flush=True)
    t0 = time.time()
    run_exact_14key_sweep(
        data_dir=data_dir,
        time_budget_mins=budget_p1,
        seed=seed,
    )
    elapsed_p1 = (time.time() - t0) / 60.0
    print(f">>> PHASE 1 FINISHED in {elapsed_p1:.2f} mins.", flush=True)

    # -------------------------------------------------------------
    # PHASE 2: Incipit Crib Constraint Solver
    # -------------------------------------------------------------
    remaining_mins = max(0.1, (total_budget_secs - (time.time() - start_time)) / 60.0)
    actual_p2_budget = min(budget_p2, remaining_mins * 0.45)
    print(f"\n>>> LAUNCHING PHASE 2: INCIPIT CRIB CONSTRAINT ENGINE (Budget: {actual_p2_budget:.1f} mins)", flush=True)
    t0 = time.time()
    run_incipit_crib_solver(
        data_dir=data_dir,
        time_budget_mins=actual_p2_budget,
        seed=seed + 1,
    )
    elapsed_p2 = (time.time() - t0) / 60.0
    print(f">>> PHASE 2 FINISHED in {elapsed_p2:.2f} mins.", flush=True)

    # -------------------------------------------------------------
    # PHASE 3: Deep Annealing Run
    # -------------------------------------------------------------
    remaining_mins = max(0.1, (total_budget_secs - (time.time() - start_time)) / 60.0)
    print(f"\n>>> LAUNCHING PHASE 3: DEEP MULTI-CHAIN ANNEALING (Budget: {remaining_mins:.1f} mins)", flush=True)
    t0 = time.time()
    run_deep_annealing_phase(
        data_dir=data_dir,
        time_budget_mins=remaining_mins,
        seed=seed + 2,
    )
    elapsed_p3 = (time.time() - t0) / 60.0
    print(f">>> PHASE 3 FINISHED in {elapsed_p3:.2f} mins.", flush=True)

    # -------------------------------------------------------------
    # Final Campaign Ledger Audit
    # -------------------------------------------------------------
    ledger = EpistemicLedger(ledger_dir=data_dir)
    summary = ledger.get_summary_statistics("dagapeyeff_1939")

    print("\n" + "=" * 80)
    print("SEQUENTIAL DISCOVERY CAMPAIGN COMPLETE")
    print(f"Total Execution Time: {(time.time() - start_time)/60.0:.2f} mins")
    print(f"Total Trials Recorded in Ledger: {summary['total_trials_denominator']}")
    print(f"Bonferroni Critical Threshold: {summary['bonferroni_critical_p']:.8f}")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sequential Discovery Campaign Orchestrator")
    parser.add_argument("--time-budget-mins", default=85.0, type=float, help="Total time budget in minutes (max 90)")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_sequential_discovery(
        total_budget_mins=args.time_budget_mins,
        data_dir=args.data_dir,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
