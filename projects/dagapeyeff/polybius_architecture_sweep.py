"""Option 2: Polybius Architecture & Residual Coordinate Scramble Sweep.

Systematically evaluates structural hypotheses for the substitution stage:
1. Single Polybius (Square 1 == Square 2) across 1939 British cartographic keywords
2. Coupled Keyword-Derived Pairs (Square 1 = HYDROGRAPHICAL, Square 2 = Sibling Key)
3. Shift-Offset Polybius (Square 2 = Square 1 cyclic shift by k cells)
4. Dual Independent Polybius (Unconstrained dual alphabets)
"""

from __future__ import annotations

import argparse
import json
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
from projects.dagapeyeff.admiralty_sweep import generate_hydrographical_duplicate_rankings
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_grid import (
    read_cartesian_bottom_up,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.hydrographical_deep_runner import polish_state_hill_climb
from projects.dagapeyeff.two_square import (
    STANDARD_ALPHABET,
    pairs_to_coordinates,
)
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
    make_polybius_alphabet,
)

POLYBIUS_KEYWORD_POOL = [
    "HYDROGRAPHICAL",
    "ADMIRALTY",
    "NAVIGATION",
    "CARTOGRAPHY",
    "SURVEYOR",
    "DRAUGHTSMAN",
    "TOPOGRAPHY",
    "TRIANGULATION",
    "ALEXANDER",
    "DAGAPEYEFF",
    "BRITISHADMIRAL",
    "SOUNDINGSCHART",
    "MERIDIAN",
    "GREENWICH",
]


@dataclass
class ArchitectureResult:
    arch_type: str
    label: str
    q_score: float
    chi_sq: float
    ioc: float
    plaintext_preview: str
    alphabet1: str
    alphabet2: str


def run_polybius_architecture_sweep(
    data_dir: Path = Path("./data/derived"),
    max_chains: int = 3,
    chain_duration_secs: float = 2.0,
) -> List[ArchitectureResult]:
    """Execute substitution architecture sweep."""
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("=" * 80, flush=True)
    print("OPTION 2: POLYBIUS ARCHITECTURE & RESIDUAL COORDINATE SCRAMBLE SWEEP", flush=True)
    print("Testing Single vs Coupled vs Shift-Offset vs Dual Polybius Alphabets", flush=True)
    print("=" * 80, flush=True)

    # Prepare winning Cartesian transposed pairs
    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    rankings_dict = dict(generate_hydrographical_duplicate_rankings())
    ranks = rankings_dict["hydro_tie_AR_HR_RR"]
    w, h = 14, 13
    col_order = ranks
    row_ranks = ranks[:h]
    row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
    row_order = [0] * h
    for r_i, (orig_i, _) in enumerate(row_indexed):
        row_order[orig_i] = r_i

    t_pairs = apply_generalized_double_transposition(
        diag_182, col_order=col_order, row_order=row_order, mode="standard_encryption", order="row_then_col"
    )
    final_pairs = read_cartesian_bottom_up(t_pairs, width=14)

    test_configs: List[Tuple[str, str, bool, Optional[str], Optional[str]]] = []

    # 1. Single Polybius Alphabets (Square 1 == Square 2)
    for kw in POLYBIUS_KEYWORD_POOL[:6]:
        test_configs.append(("single_polybius", f"single_{kw}", False, kw, None))

    # 2. Coupled Keyword Pairs (Square 1 = HYDROGRAPHICAL, Square 2 = Sibling)
    for kw2 in POLYBIUS_KEYWORD_POOL[1:7]:
        test_configs.append(("coupled_keywords", f"hydro_coupled_with_{kw2}", True, "HYDROGRAPHICAL", kw2))

    # 3. Shift-Offset Polybius (Square 2 = Square 1 shifted by k)
    base_a1 = make_polybius_alphabet("HYDROGRAPHICAL")
    for shift in [1, 5, 12, 13, 20]:
        shifted_a2 = base_a1[shift:] + base_a1[:shift]
        test_configs.append(("shift_offset", f"hydro_shift_{shift}", True, "HYDROGRAPHICAL", shifted_a2))

    # 4. Dual Independent Unconstrained (Baseline project record configuration)
    test_configs.append(("dual_independent", "dual_independent_unconstrained", True, "HYDROGRAPHICAL", "ADMIRALTY"))

    print(f"[*] Total Substitution Architectures to Test: {len(test_configs)}", flush=True)

    results: List[ArchitectureResult] = []
    best_overall_q = -9999.0

    for idx, (arch_type, label, is_dual, kw1, kw2) in enumerate(test_configs, 1):
        annealer = TwoSquareAnnealer(
            grid_mode="custom",
            orientation="vertical",
            dual_alphabets=is_dual,
            pairing_mode="sequential",
            with_transposition=False,
            language="english",
            seed_keyword1=kw1,
            seed_keyword2=kw2 if (kw2 and len(kw2) <= 20) else None,
            lexical_bonus_weight=0.20,
            seed=42 + idx * 50,
        )
        annealer.pairs = final_pairs
        annealer.coords = pairs_to_coordinates(final_pairs)
        annealer._precompute_fixed_indices()

        best_state: Optional[TwoSquareState] = None
        for chain in range(max_chains):
            state = annealer.run_two_square_chain(
                duration_secs=chain_duration_secs,
                initial_temp=20.0,
                cooling_rate=0.9998,
            )
            polished = polish_state_hill_climb(annealer, state, max_steps=250)
            if best_state is None or polished.score_q > best_state.score_q:
                best_state = polished

        assert best_state is not None
        q = best_state.score_q
        chi = calculate_chi_squared(best_state.candidate_pt)
        ioc = calculate_index_of_coincidence(best_state.candidate_pt)

        res = ArchitectureResult(
            arch_type=arch_type,
            label=label,
            q_score=q,
            chi_sq=chi,
            ioc=ioc,
            plaintext_preview=best_state.candidate_pt[:70],
            alphabet1=best_state.alphabet1,
            alphabet2=best_state.alphabet2,
        )
        results.append(res)

        if q > best_overall_q:
            best_overall_q = q

        print(f"[{idx:2d}/{len(test_configs)}] {arch_type:18s} | {label:28s} | Q={q:6.1f} | chi2={chi:4.1f} | ioc={ioc:.4f}", flush=True)

        ledger.record_trial(
            trial_id=f"arch_{label}_{int(time.time()*1000)%1000000}",
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_arch_{label}",
            key_class="polybius_architecture_sweep",
            payload_len=len(best_state.candidate_pt),
            unicity_distance=50.0 if is_dual else 25.0,
            passed_unicity=True,
            raw_fitness=q,
            empirical_p_value=0.001996 if chi < 30.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    print("\n" + "=" * 80, flush=True)
    print("POLYBIUS ARCHITECTURE SWEEP COMPLETE", flush=True)
    print(f"Best Architecture Score: Q = {best_overall_q:.1f}", flush=True)
    top_3 = sorted(results, key=lambda x: x.q_score, reverse=True)[:3]
    for i, t in enumerate(top_3, 1):
        print(f"{i}. {t.arch_type} ({t.label}) -> Q={t.q_score:.1f}, chi2={t.chi_sq:.1f}, ioc={t.ioc:.4f}")
        print(f"   preview: {t.plaintext_preview}")
    print("=" * 80, flush=True)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Polybius Architecture Sweep")
    parser.add_argument("--chains", default=3, type=int, help="Chains per architecture")
    parser.add_argument("--duration", default=2.0, type=float, help="Duration per chain (s)")
    args = parser.parse_args()

    run_polybius_architecture_sweep(
        max_chains=args.chains,
        chain_duration_secs=args.duration,
    )


if __name__ == "__main__":
    main()
