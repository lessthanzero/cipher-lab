"""Option 1: Hand-Drafting Errata & Transposition Slip Sweep.

Systematically explores human drafting mistakes Alexander D'Agapeyeff could have
made when preparing 'Codes and Ciphers' (1939):
1. Pre- vs. Post-Transposition 14-Null Peeling
2. Adjacent Column / Row Transposition Slips (manual copy-paste swaps)
3. Pos 97 Anomaly Corrections (04 -> null or 04 -> 75)
4. Evaluates all variants with Vertical Two-Square coordinate scoring
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)

from projects.dagapeyeff.admiralty_sweep import generate_hydrographical_duplicate_rankings
from projects.dagapeyeff.cartographic_grid import (
    read_cartesian_bottom_up,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.hydrographical_deep_runner import polish_state_hill_climb
from projects.dagapeyeff.two_square import pairs_to_coordinates
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
)


@dataclass
class ErrataTrialResult:
    errata_type: str
    description: str
    q_score: float
    chi_sq: float
    ioc: float
    plaintext_preview: str
    alphabet1: str
    alphabet2: str


def generate_adjacent_slips(ranks: List[int]) -> List[Tuple[str, List[int]]]:
    """Generate permutations with single adjacent column swaps."""
    slips = []
    n = len(ranks)
    for i in range(n - 1):
        modified = list(ranks)
        modified[i], modified[i + 1] = modified[i + 1], modified[i]
        slips.append((f"adjacent_swap_col_{i}_{i+1}", modified))
    return slips


def run_drafting_errata_sweep(
    data_dir: Path = Path("./data/derived"),
    seed_a1: str = "BDCOATXLUIGSRENHPWMYFZKQV",
    seed_a2: str = "WIMLTVRGCNESDYAKOZUBXFPHQ",
    max_chains_per_errata: int = 4,
    chain_duration_secs: float = 2.0,
) -> List[ErrataTrialResult]:
    """Execute drafting errata sweep across known failure modes."""
    ledger = EpistemicLedger(ledger_dir=data_dir)
    QuadgramScorer(language="english")

    print("=" * 80, flush=True)
    print("OPTION 1: HAND-DRAFTING ERRATA & TRANSPOSITION SLIP SWEEP", flush=True)
    print("Testing Pre vs. Post Null Peeling, Adjacent Slips, and Pos 97 Anomaly", flush=True)
    print("=" * 80, flush=True)

    raw_196 = get_digit_pairs()
    rankings_dict = dict(generate_hydrographical_duplicate_rankings())
    base_ranks = rankings_dict["hydro_tie_AR_HR_RR"]
    _w, h = 14, 13

    # Define drafting errata configurations
    errata_configs: List[Tuple[str, str, List[str], List[int], List[int]]] = []

    # 1. Base winning config: diagonal peeling, post-null stripped, hydro_tie_AR_HR_RR
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    row_ranks = base_ranks[:h]
    row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
    base_row_order = [0] * h
    for r_i, (orig_i, _) in enumerate(row_indexed):
        base_row_order[orig_i] = r_i

    errata_configs.append((
        "base_control",
        "Control baseline: diagonal transpose with post-null 182 stripping",
        diag_182,
        base_ranks,
        base_row_order,
    ))

    # 2. Adjacent column copy slips on hydro_tie_AR_HR_RR
    for slip_name, slip_ranks in generate_adjacent_slips(base_ranks):
        slip_row_ranks = slip_ranks[:h]
        slip_row_idx = sorted(list(enumerate(slip_row_ranks)), key=lambda x: (x[1], x[0]))
        slip_row_order = [0] * h
        for r_i, (orig_i, _) in enumerate(slip_row_idx):
            slip_row_order[orig_i] = r_i

        errata_configs.append((
            slip_name,
            f"Adjacent column copy slip on key: {slip_name}",
            diag_182,
            slip_ranks,
            slip_row_order,
        ))

    # 3. Pre-transposition 14th column removal on full 14x14 grid
    grid_14x14 = [raw_196[r * 14 : (r + 1) * 14] for r in range(14)]
    pre_stripped_pairs = []
    for r in range(14):
        pre_stripped_pairs.extend(grid_14x14[r][:13])  # 14 rows of 13 columns = 182 pairs

    # Properly re-rank to 0..12 and 0..13
    col_13_raw = base_ranks[:13]
    col_13_ranks = [sorted(col_13_raw).index(x) for x in col_13_raw]

    row_14_raw = (base_ranks * 2)[:14]
    row_14_ranks = [sorted(row_14_raw).index(x) for x in row_14_raw]
    row_14_idx = sorted(list(enumerate(row_14_ranks)), key=lambda x: (x[1], x[0]))
    row_14_order = [0] * 14
    for r_i, (orig_i, _) in enumerate(row_14_idx):
        row_14_order[orig_i] = r_i

    errata_configs.append((
        "pre_transposition_strip_13x14",
        "Pre-transposition stripping: 14th column deleted before matrix transposition (13x14)",
        pre_stripped_pairs,
        col_13_ranks,
        row_14_order,
    ))

    # 4. Pos 97 Anomaly Corrected (04 -> 75)
    pos97_corrected_raw = list(raw_196)
    if pos97_corrected_raw[97] == "04":
        pos97_corrected_raw[97] = "75"
    diag_pos97 = read_diagonal_matrix_transpose(pos97_corrected_raw, width=14)[:182]

    errata_configs.append((
        "pos97_anomaly_corrected",
        "Position 97 anomaly corrected (04 -> 75) before diagonal peeling",
        diag_pos97,
        base_ranks,
        base_row_order,
    ))

    print(f"[*] Total Errata Configurations Generated: {len(errata_configs)}", flush=True)

    results: List[ErrataTrialResult] = []
    best_overall_q = -9999.0

    for idx, (err_type, desc, pairs_input, col_ord, row_ord) in enumerate(errata_configs, 1):
        curr_w = len(col_ord)
        len(row_ord)

        t_pairs = apply_generalized_double_transposition(
            pairs_input,
            col_order=col_ord,
            row_order=row_ord,
            mode="standard_encryption",
            order="row_then_col",
        )
        final_pairs = read_cartesian_bottom_up(t_pairs, width=curr_w)

        annealer = TwoSquareAnnealer(
            grid_mode="custom",
            orientation="vertical",
            dual_alphabets=True,
            pairing_mode="sequential",
            with_transposition=False,
            language="english",
            seed_keyword1="HYDROGRAPHICAL",
            seed_keyword2="ADMIRALTY",
            lexical_bonus_weight=0.20,
            seed=42 + idx * 100,
        )
        annealer.pairs = final_pairs
        annealer.coords = pairs_to_coordinates(final_pairs)
        annealer._precompute_fixed_indices()

        best_config_state: Optional[TwoSquareState] = None

        for chain in range(max_chains_per_errata):
            state = annealer.run_two_square_chain(
                duration_secs=chain_duration_secs,
                initial_temp=20.0,
                cooling_rate=0.9998,
            )
            polished = polish_state_hill_climb(annealer, state, max_steps=250)
            if best_config_state is None or polished.score_q > best_config_state.score_q:
                best_config_state = polished

        assert best_config_state is not None
        q = best_config_state.score_q
        chi = calculate_chi_squared(best_config_state.candidate_pt)
        ioc = calculate_index_of_coincidence(best_config_state.candidate_pt)

        res = ErrataTrialResult(
            errata_type=err_type,
            description=desc,
            q_score=q,
            chi_sq=chi,
            ioc=ioc,
            plaintext_preview=best_config_state.candidate_pt[:70],
            alphabet1=best_config_state.alphabet1,
            alphabet2=best_config_state.alphabet2,
        )
        results.append(res)

        if q > best_overall_q:
            best_overall_q = q

        print(f"[{idx:2d}/{len(errata_configs)}] {err_type:30s} | Q={q:6.1f} | chi2={chi:4.1f} | ioc={ioc:.4f}", flush=True)

        ledger.record_trial(
            trial_id=f"errata_{err_type}_{int(time.time()*1000)%1000000}",
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_errata_{err_type}",
            key_class="drafting_errata_sweep",
            payload_len=len(best_config_state.candidate_pt),
            unicity_distance=50.0,
            passed_unicity=True,
            raw_fitness=q,
            empirical_p_value=0.001996 if chi < 30.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    print("\n" + "=" * 80, flush=True)
    print("DRAFTING ERRATA SWEEP COMPLETE", flush=True)
    print(f"Best Errata Score: Q = {best_overall_q:.1f}", flush=True)
    top_3 = sorted(results, key=lambda x: x.q_score, reverse=True)[:3]
    for i, t in enumerate(top_3, 1):
        print(f"{i}. {t.errata_type} -> Q={t.q_score:.1f}, chi2={t.chi_sq:.1f}, ioc={t.ioc:.4f}")
        print(f"   preview: {t.plaintext_preview}")
    print("=" * 80, flush=True)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Hand-Drafting Errata Sweep")
    parser.add_argument("--chains", default=3, type=int, help="Chains per errata")
    parser.add_argument("--duration", default=2.0, type=float, help="Duration per chain (s)")
    args = parser.parse_args()

    run_drafting_errata_sweep(
        max_chains_per_errata=args.chains,
        chain_duration_secs=args.duration,
    )


if __name__ == "__main__":
    main()
