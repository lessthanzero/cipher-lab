"""Forensic Biographical & Cartographic Discovery Runner for D'Agapeyeff Cipher.

Attacks the cipher specifically through the lenses of:
1. Cartographic grid reading (Cartesian bottom-up, Easting-first, diagonal transpose, spirals)
2. Kerckhoffs 1883 double-transposition defects (erroneous SCHUVALOF ranking vs corrected)
3. Row 0 clerical correction ('04' at position 97 -> {64, 74, 84, 94, 75})
4. Column 14 null margin stripping (182 pairs)
5. Book-derived keywords from Codes and Ciphers and Maps (OUP 1942)
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from typing import List

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)

from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_grid import (
    CARTOGRAPHIC_OPERATORS,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.clerical_repair import (
    get_all_row0_variants,
    strip_column_14_margin,
)
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.joint_annealer import make_polybius_alphabet
from projects.dagapeyeff.kerckhoffs_defect import (
    BOOK_KEYWORDS,
    apply_double_kerckhoffs_transposition,
    get_historical_shuvalof_ranks,
)

ROW_MAP = {"6": 0, "7": 1, "8": 2, "9": 3, "0": 4}
COL_MAP = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4}


def decode_pairs_fast(pairs: List[str], alphabet: str) -> str:
    """Ultra-fast decode from pre-mapped pair cell indices."""
    out = []
    for p in pairs:
        if len(p) == 2:
            r = ROW_MAP.get(p[0], 0)
            c = COL_MAP.get(p[1], 0)
            out.append(alphabet[r * 5 + c])
        else:
            out.append("?")
    return "".join(out)


def run_forensic_biographical_sweep(
    data_dir: Path,
    time_budget_mins: float = 5.0,
    seed: int = 42,
) -> None:
    """Execute systematic forensic sweep over authorial and typographical defect hypotheses."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    rng = random.Random(seed)
    
    pairs_raw = get_digit_pairs()
    scorer = QuadgramScorer(language="english")
    ledger = EpistemicLedger(ledger_dir=data_dir)
    
    print("=" * 80)
    print("D'AGAPEYEFF FORENSIC BIOGRAPHICAL & CARTOGRAPHIC DISCOVERY SWEEP")
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s)")
    print("Hypotheses: Cartographic Grids, Kerckhoffs Inversion, Shuvalof Defect, Row 0 Anomaly")
    print("=" * 80)

    # 1. Sweep 1: Row 0 / Column 14 Repair Variants
    print("\n[+] STAGE 1: Evaluating Row 0 Clerical Repair Matrix & Column 14 Stripping...")
    row0_variants = get_all_row0_variants(pairs_raw)
    
    best_candidate_pt = ""
    best_candidate_score = -9999.0
    best_hypothesis = ""

    for variant_name, pairs_var in row0_variants.items():
        if (time.time() - start_time) >= time_budget_secs:
            break

        # Test against top book keywords
        for kw_name in ["SCHUVALOF_BOOK_TEXT", "DAGAPEYEFF", "ORDNANCE_SURVEY", "RETRIANGULATION"]:
            kw = BOOK_KEYWORDS[kw_name]
            alpha = make_polybius_alphabet(kw)
            pt_direct = decode_pairs_fast(pairs_var, alpha)
            q_tot = scorer.score_total(pt_direct)

            trial_id = f"row0_{variant_name}_{kw_name}_{int(time.time()*1000)%1000000}"
            ledger.record_trial(
                trial_id=trial_id,
                artifact_id="dagapeyeff_1939",
                hypothesis_name=f"H_row0_{variant_name}_{kw_name}",
                key_class="clerical_row0_repair",
                payload_len=len(pt_direct),
                unicity_distance=25.0,
                passed_unicity=True,
                raw_fitness=q_tot,
                empirical_p_value=0.5,
                negative_twin_fitness=0.0,
                falsification_status="ACTIVE_SEARCH",
                abstention_reason=None,
            )

            if q_tot > best_candidate_score:
                best_candidate_score = q_tot
                best_candidate_pt = pt_direct
                best_hypothesis = f"H_row0_{variant_name}_{kw_name}"

    print(f"[*] Stage 1 Complete. Top repair candidate: {best_hypothesis} (Q={best_candidate_score:.1f})")

    # 2. Sweep 2: Cartographic Grid Operators (Easting-First, Cartesian Bottom-Up, Diagonal)
    print("\n[+] STAGE 2: Evaluating Cartographic Grid Transformations...")
    for op_name, op_func in CARTOGRAPHIC_OPERATORS.items():
        if (time.time() - start_time) >= time_budget_secs:
            break

        # Apply grid operator to raw pairs and 182-pair stripped
        for base_label, base_pairs in [("196_full", pairs_raw), ("182_stripped", strip_column_14_margin(pairs_raw))]:
            w = 14 if base_label == "196_full" else 13
            transformed_pairs = op_func(base_pairs, w) if op_name != "diagonal_transpose" or w == 14 else base_pairs

            for kw_name in ["ORDNANCE_SURVEY", "SCHUVALOF_BOOK_TEXT", "BENCHMARK", "CASSINI", "DAGAPEYEFF"]:
                kw = BOOK_KEYWORDS[kw_name]
                alpha = make_polybius_alphabet(kw)
                pt = decode_pairs_fast(transformed_pairs, alpha)
                q_tot = scorer.score_total(pt)

                trial_id = f"carto_{op_name}_{base_label}_{kw_name}_{int(time.time()*1000)%1000000}"
                ledger.record_trial(
                    trial_id=trial_id,
                    artifact_id="dagapeyeff_1939",
                    hypothesis_name=f"H_carto_{op_name}_{base_label}_{kw_name}",
                    key_class=f"cartographic_grid_{op_name}",
                    payload_len=len(pt),
                    unicity_distance=25.0,
                    passed_unicity=True,
                    raw_fitness=q_tot,
                    empirical_p_value=0.5,
                    negative_twin_fitness=0.0,
                    falsification_status="ACTIVE_SEARCH",
                    abstention_reason=None,
                )

                if q_tot > best_candidate_score:
                    best_candidate_score = q_tot
                    best_candidate_pt = pt
                    best_hypothesis = f"H_carto_{op_name}_{base_label}_{kw_name}"

    print(f"[*] Stage 2 Complete. Top cartographic candidate: {best_hypothesis} (Q={best_candidate_score:.1f})")

    # 3. Sweep 3: Kerckhoffs Double Transposition Inversion & Shuvalof Defects
    print("\n[+] STAGE 3: Testing Kerckhoffs Defect Inversions & Shuvalof Ordering...")
    shuvalof_ranks = get_historical_shuvalof_ranks()

    for rank_label, rank_order in shuvalof_ranks.items():
        if (time.time() - start_time) >= time_budget_secs:
            break

        for direction_mode in ["kerckhoffs_decryption", "standard_encryption"]:
            for target_w in [14, 13]:
                base_pairs = pairs_raw if target_w == 14 else strip_column_14_margin(pairs_raw)
                expanded_key = (rank_order * 2)[:target_w]
                indexed_key = sorted(list(enumerate(expanded_key)), key=lambda x: (x[1], x[0]))
                perm = [0] * target_w
                for r, (orig_i, _) in enumerate(indexed_key):
                    perm[orig_i] = r

                transposed = apply_double_kerckhoffs_transposition(base_pairs, perm, mode=direction_mode)

                for kw_name in ["SCHUVALOF_BOOK_TEXT", "REUNION_TOMORROW", "ORDNANCE_SURVEY"]:
                    kw = BOOK_KEYWORDS[kw_name]
                    alpha = make_polybius_alphabet(kw)
                    pt = decode_pairs_fast(transposed, alpha)
                    q_tot = scorer.score_total(pt)

                    trial_id = f"kerckhoffs_{rank_label[:10]}_{direction_mode[:8]}_w{target_w}_{kw_name}_{int(time.time()*1000)%1000000}"
                    ledger.record_trial(
                        trial_id=trial_id,
                        artifact_id="dagapeyeff_1939",
                        hypothesis_name=f"H_kerckhoffs_{rank_label}_{direction_mode}_w{target_w}_{kw_name}",
                        key_class="kerckhoffs_defect_inversion",
                        payload_len=len(pt),
                        unicity_distance=35.0,
                        passed_unicity=True,
                        raw_fitness=q_tot,
                        empirical_p_value=0.5,
                        negative_twin_fitness=0.0,
                        falsification_status="ACTIVE_SEARCH",
                        abstention_reason=None,
                    )

                    if q_tot > best_candidate_score:
                        best_candidate_score = q_tot
                        best_candidate_pt = pt
                        best_hypothesis = f"H_kerckhoffs_{rank_label}_{direction_mode}_w{target_w}_{kw_name}"

    # 4. Sweep 4: High-Speed Annealing on Top Forensic Structures
    print("\n[+] STAGE 4: High-Speed Annealing on Top Forensic Geometry...")
    diag_196 = read_diagonal_matrix_transpose(pairs_raw, width=14)
    diag_182 = diag_196[:182]
    
    current_alpha = make_polybius_alphabet("ORDNANCESURVEY")
    best_sa_pt = decode_pairs_fast(diag_182, current_alpha)
    best_sa_q = scorer.score_total(best_sa_pt)

    t_sa_start = time.time()
    steps = 0
    temp = 20.0
    cooling = 0.99995

    while (time.time() - start_time) < (time_budget_secs - 3.0) and temp > 0.05:
        steps += 1
        a_list = list(current_alpha)
        i, j = rng.sample(range(25), 2)
        a_list[i], a_list[j] = a_list[j], a_list[i]
        cand_alpha = "".join(a_list)

        cand_pt = decode_pairs_fast(diag_182, cand_alpha)
        cand_q = scorer.score_total(cand_pt)

        delta = cand_q - best_sa_q
        if delta > 0 or random.random() < pow(2.71828, delta / temp):
            best_sa_q = cand_q
            best_sa_pt = cand_pt
            current_alpha = cand_alpha
            if cand_q > best_candidate_score:
                best_candidate_score = cand_q
                best_candidate_pt = cand_pt
                best_hypothesis = "H_sa_diagonal_pelling_182"

        temp *= cooling

    elapsed_sa = max(0.001, time.time() - t_sa_start)
    print(f"[*] Annealing Complete ({steps} steps, {steps/elapsed_sa:.0f} decodes/s). Best SA Q={best_sa_q:.1f}")

    # Summary and Ledger Checkpointing
    summary = ledger.get_summary_statistics("dagapeyeff_1939")
    comp = evaluate_against_competition(
        best_candidate_score,
        calculate_chi_squared(best_candidate_pt),
        calculate_index_of_coincidence(best_candidate_pt),
        len(best_candidate_pt),
    )

    print("\n" + "=" * 80)
    print("FORENSIC BIOGRAPHICAL & CARTOGRAPHIC SWEEP COMPLETE")
    print(f"Total Trials Recorded in Ledger: {summary['total_trials_denominator']}")
    print(f"Bonferroni Critical Threshold: {summary['bonferroni_critical_p']:.8f}")
    print(f"Top Candidate: {best_hypothesis}")
    print(f"Score Q: {best_candidate_score:.1f} (Marland Record: {comp['marland_record_q']}, Delta: {comp['delta_q']:+.1f})")
    print(f"Chi-Squared: {comp['candidate_chi_sq']:.1f} | IoC: {comp['candidate_ioc']:.4f}")
    print(f"Competition Status: {comp['competition_status']}")
    print(f"Plaintext Sample: \"{best_candidate_pt[:60]}...\"")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="D'Agapeyeff Forensic Biographical & Cartographic Runner")
    parser.add_argument("--time-budget-mins", default=5.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_forensic_biographical_sweep(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
