"""Autonomous Competitive Discovery Loop Runner for D'Agapeyeff Cipher.

Directly competes against benchmarks established at https://dagapeyeffresearch.com.
Supports strict time budgeting, Darwin RAM/CPU guardrails, and Fedora PC worker offloading.
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from cipher_lab.loop import CipherDiscoveryLoop
from cipher_lab.stats import QuadgramScorer

from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.corpus import (
    get_digit_pairs,
    get_payload_digits,
    get_stripped_14x13_pairs,
)
from projects.dagapeyeff.kerckhoffs import KerckhoffsEngine


def run_competitive_discovery(
    data_dir: Path,
    time_budget_mins: float = 2.0,
    iterations_per_module: int = 50,
    seed: int = 42,
) -> None:
    """Run an autonomous, time-budgeted competitive discovery sweep."""
    time_budget_secs = time_budget_mins * 60.0
    engine = KerckhoffsEngine()
    rng = random.Random(seed)
    
    pairs_196 = get_digit_pairs()
    pairs_182 = get_stripped_14x13_pairs()

    loop = CipherDiscoveryLoop(
        artifact_id="dagapeyeff_1939",
        ciphertext=get_payload_digits(),
        alphabet_size=25,
        key_space_bits=84.0,
        historical_context="1939 British cartographer challenge cipher from Codes and Ciphers. 196 pairs, 14x14 grid, reversed Kerckhoffs.",
        data_dir=data_dir,
        time_budget_secs=time_budget_secs,
    )

    print("=" * 80)
    print("D'AGAPEYEFF AUTONOMOUS COMPETITIVE DISCOVERY RUNNER")
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s) | Remote Worker: {loop.remote_worker.is_reachable()}")
    print("=" * 80)

    # 1. Baseline H0: Direct Polybius decoding (All 196 positions)
    pt_direct = engine.decode_pair_stream(pairs_196)
    eval_h0 = loop.evaluate_candidate(
        hypothesis_name="H0_direct_polybius",
        key_class="monoalphabetic_polybius",
        key_desc="Standard Polybius 5x5 reading of all 196 pairs",
        candidate_pt=pt_direct,
    )
    total_q_h0 = loop.scorer.score_total(pt_direct)
    comp_h0 = evaluate_against_competition(
        total_q_h0,
        eval_h0.metadata.get("chi_squared", 999.0),
        eval_h0.index_of_coincidence,
        len(pt_direct),
    )
    print(f"[*] H0 Direct: norm_score={eval_h0.quadgram_score:.2f}, total_Q={total_q_h0:.1f} (Marland Record={comp_h0['marland_record_q']}), chi_sq={comp_h0['candidate_chi_sq']:.1f}, status={comp_h0['competition_status']}")

    # 2. Module A: Reversed Kerckhoffs Double-Transposition Permutation Sweep
    print("\n[+] MODULE A: Reversed Kerckhoffs Double-Transposition Permutation Sweep...")
    base_14 = list(range(14))
    for i in range(iterations_per_module):
        if loop.is_time_exhausted():
            print("[!] Wall-clock time budget reached during Module A. Checkpointing and exiting.")
            break
        
        row_key = base_14[:]
        col_key = base_14[:]
        rng.shuffle(row_key)
        rng.shuffle(col_key)

        transposed_pairs = engine.apply_reversed_kerckhoffs_double_transposition(
            pairs_196, row_key, col_key, width=14
        )
        pt = engine.decode_pair_stream(transposed_pairs)
        
        eval_res = loop.evaluate_candidate(
            hypothesis_name=f"H_kerckhoffs_dtrans_{i}",
            key_class="reversed_kerckhoffs",
            key_desc=f"Row key {row_key[:4]}..., Col key {col_key[:4]}...",
            candidate_pt=pt,
        )

        if eval_res.is_statistically_viable or eval_res.quadgram_score > -5.0:
            total_q = loop.scorer.score_total(pt)
            comp = evaluate_against_competition(
                total_q,
                eval_res.metadata.get("chi_squared", 999.0),
                eval_res.index_of_coincidence,
                len(pt),
            )
            print(f"  --> Iteration {i}: norm_score={eval_res.quadgram_score:.2f}, total_Q={total_q:.1f}, status={comp['competition_status']}")

    # 3. Module B: 14th-Column Null Removal ($14 \times 13 = 182$ pairs)
    print("\n[+] MODULE B: 14th-Column Null Removal ($14 \\times 13 = 182$ pairs)...")
    base_13 = list(range(13))
    for i in range(iterations_per_module):
        if loop.is_time_exhausted():
            print("[!] Wall-clock time budget reached during Module B. Checkpointing and exiting.")
            break

        col_order = base_13[:]
        rng.shuffle(col_order)
        transposed_182 = engine.apply_single_pair_transposition(pairs_182, width=13, col_order=col_order)
        pt_182 = engine.decode_pair_stream(transposed_182)

        eval_res = loop.evaluate_candidate(
            hypothesis_name=f"H_col14_stripped_k13_{i}",
            key_class="null_removed_transposition",
            key_desc=f"14th-col removed, 13-col perm {col_order[:4]}...",
            candidate_pt=pt_182,
        )

    # 4. Module C: Coupled Position 97 Correction ($04 \\to 75$) + Kerckhoffs
    print("\n[+] MODULE C: Position 97 Correction ($04 \\to 75$) + Kerckhoffs Sweeps...")
    corrected_pairs = engine.apply_position_97_correction(pairs_196, replacement="75")
    for i in range(iterations_per_module):
        if loop.is_time_exhausted():
            print("[!] Wall-clock time budget reached during Module C. Checkpointing and exiting.")
            break

        row_key = base_14[:]
        col_key = base_14[:]
        rng.shuffle(row_key)
        rng.shuffle(col_key)

        transposed_pairs = engine.apply_reversed_kerckhoffs_double_transposition(
            corrected_pairs, row_key, col_key, width=14
        )
        pt = engine.decode_pair_stream(transposed_pairs)

        loop.evaluate_candidate(
            hypothesis_name=f"H_pos97_kerckhoffs_{i}",
            key_class="error_corrected_kerckhoffs",
            key_desc=f"Pos 97=75, Row key {row_key[:4]}..., Col key {col_key[:4]}...",
            candidate_pt=pt,
        )

    # 5. Module D: Russian Nihilist Keywords & Transliterated Polybius Squares
    print("\n[+] MODULE D: Russian Nihilist Keywords & Slavic Transliteration Sweeps...")
    russian_keywords = [
        "SCHUVALOF", "SCHUVALOV", "AGAPEYEFF", "AGAPYEV", "ROSSIYA",
        "KARTOGRAFIYA", "MOSKVA", "LENINGRAD", "PETROGRAD", "NIHILIST",
    ]
    
    def make_keyword_alpha(kw: str) -> str:
        seen = set()
        out = ""
        for c in kw.upper().replace("J", "I"):
            if c.isalpha() and c not in seen:
                seen.add(c)
                out += c
        for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
            if c not in seen:
                seen.add(c)
                out += c
        return out[:25]

    ru_scorer = QuadgramScorer(language="russian_translit")

    for kw in russian_keywords:
        if loop.is_time_exhausted():
            print("[!] Wall-clock time budget reached during Module D. Checkpointing and exiting.")
            break

        alpha = make_keyword_alpha(kw)
        kw_engine = KerckhoffsEngine(key_alphabet=alpha)
        
        # Test direct reading with Russian keyword square
        pt_kw = kw_engine.decode_pair_stream(pairs_196)
        ru_score_kw = ru_scorer.score(pt_kw)
        loop.evaluate_candidate(
            hypothesis_name=f"H_russian_kw_{kw}",
            key_class="russian_nihilist_keyword",
            key_desc=f"Polybius square with Russian keyword '{kw}' (ru_score={ru_score_kw:.2f})",
            candidate_pt=pt_kw,
        )

        # Test reversed Kerckhoffs transposition with Russian keyword square
        for j in range(min(5, iterations_per_module)):
            if loop.is_time_exhausted():
                break
            r_key = base_14[:]
            c_key = base_14[:]
            rng.shuffle(r_key)
            rng.shuffle(c_key)
            trans_pairs = kw_engine.apply_reversed_kerckhoffs_double_transposition(
                pairs_196, r_key, c_key, width=14
            )
            pt_trans = kw_engine.decode_pair_stream(trans_pairs)
            loop.evaluate_candidate(
                hypothesis_name=f"H_ru_{kw}_kerckhoffs_{j}",
                key_class="russian_kerckhoffs",
                key_desc=f"KW '{kw}', Row key {r_key[:4]}..., Col key {c_key[:4]}...",
                candidate_pt=pt_trans,
            )

    # 6. Module E: Continuous Evolutionary Search (until time budget exhausted)
    print("\n[+] MODULE E: Continuous Multi-Hypothesis Evolutionary Search...")
    iter_count = 0
    while not loop.is_time_exhausted():
        iter_count += 1
        # Randomly choose strategy: full 196, 182-stripped, or pos97 corrected
        mode = rng.choice(["kerckhoffs_14", "col14_stripped", "pos97_corrected"])
        kw = rng.choice(russian_keywords + ["STANDARD"])
        alpha = make_keyword_alpha(kw) if kw != "STANDARD" else "ABCDEFGHIKLMNOPQRSTUVWXYZ"
        active_engine = KerckhoffsEngine(key_alphabet=alpha)

        if mode == "kerckhoffs_14":
            r_key = base_14[:]
            c_key = base_14[:]
            rng.shuffle(r_key)
            rng.shuffle(c_key)
            t_pairs = active_engine.apply_reversed_kerckhoffs_double_transposition(pairs_196, r_key, c_key, 14)
            pt = active_engine.decode_pair_stream(t_pairs)
        elif mode == "col14_stripped":
            c_key = base_13[:]
            rng.shuffle(c_key)
            t_pairs = active_engine.apply_single_pair_transposition(pairs_182, 13, c_key)
            pt = active_engine.decode_pair_stream(t_pairs)
        else:
            r_key = base_14[:]
            c_key = base_14[:]
            rng.shuffle(r_key)
            rng.shuffle(c_key)
            c_pairs = active_engine.apply_position_97_correction(pairs_196, "75")
            t_pairs = active_engine.apply_reversed_kerckhoffs_double_transposition(c_pairs, r_key, c_key, 14)
            pt = active_engine.decode_pair_stream(t_pairs)

        loop.evaluate_candidate(
            hypothesis_name=f"H_evo_{mode}_{iter_count}",
            key_class=f"evolutionary_{mode}",
            key_desc=f"Evo mode {mode}, KW '{kw}'",
            candidate_pt=pt,
        )

        if iter_count % 20 == 0:
            elapsed_m = (time.time() - loop.start_time) / 60.0
            print(f"  [*] Evolutionary search active: {iter_count} trials in module E ({elapsed_m:.2f} / {time_budget_mins:.1f} mins elapsed)...")

    # Final Checkpointing & Statistics
    loop.save_checkpoint()
    summary = loop.ledger.get_summary_statistics("dagapeyeff_1939")
    print("\n" + "=" * 80)
    print("COMPETITIVE RUN COMPLETE - SUMMARY")
    print(f"Total Trials Recorded (Denominator): {summary['total_trials_denominator']}")
    print(f"Multiplicity-Adjusted Critical Threshold (Bonferroni): {summary['bonferroni_critical_p']:.6f}")
    if loop.best_candidate:
        total_q_best = loop.best_candidate.quadgram_score * (196 - 3)
        best_comp = evaluate_against_competition(
            total_q_best,
            loop.best_candidate.metadata.get("chi_squared", 999.0),
            loop.best_candidate.index_of_coincidence,
            196,
        )
        print(f"Best Candidate: {loop.best_candidate.hypothesis_name}")
        print(f"Best Normalized Score: {loop.best_candidate.quadgram_score:.2f} | Total Q (196-char): {total_q_best:.1f} (Marland Record: {best_comp['marland_record_q']})")
        print(f"Competition Status: {best_comp['competition_status']}")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="D'Agapeyeff Autonomous Competitive Discovery Runner")
    parser.add_argument("--time-budget-mins", default=1.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--iterations", default=25, type=int, help="Iterations per module")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    args = parser.parse_args()

    run_competitive_discovery(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        iterations_per_module=args.iterations,
    )


if __name__ == "__main__":
    main()
