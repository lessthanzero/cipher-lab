"""Autonomous Competitive Discovery Loop Runner for D'Agapeyeff Cipher.

Directly competes against benchmarks established at https://dagapeyeffresearch.com.
Integrates OpenAI GPT-6 Astra hypothesis seeding, joint simulated annealing,
Darwin RAM/CPU guardrails, and Fedora PC worker offloading.
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from cipher_lab.loop import CipherDiscoveryLoop
from cipher_lab.stats import QuadgramScorer
from projects.dagapeyeff.astra_advisor import (
    query_astra_advisor,
    query_astra_cartographic_nihilist,
)
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_corpus import (
    DIAGNOSTIC_ROOTS,
    NIHILIST_INDICATOR_TERMS,
    ORDNANCE_SURVEY_TERMS,
    calculate_cartographic_lexical_bonus,
)
from projects.dagapeyeff.corpus import (
    get_digit_pairs,
    get_payload_digits,
    get_stripped_14x13_pairs,
)
from projects.dagapeyeff.joint_annealer import JointDagapeyeffAnnealer, make_polybius_alphabet
from projects.dagapeyeff.kerckhoffs import KerckhoffsEngine
from projects.dagapeyeff.two_square_annealer import TwoSquareAnnealer
from projects.dagapeyeff.desync_attack import DesyncAnnealer


def run_competitive_discovery(
    data_dir: Path,
    time_budget_mins: float = 30.0,
    iterations_per_module: int = 50,
    enable_joint_annealing: bool = True,
    attack_mode: str = "two_square",
    model_name: str = "gpt-6-astra",
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
    print(f"Time Budget: {time_budget_mins:.2f} mins ({time_budget_secs:.0f}s) | Model: {model_name}")
    print(f"Fedora Worker Reachable: {loop.remote_worker.is_reachable()}")
    print("=" * 80)

    # 0. Engage OpenAI GPT-6 Astra for Hypothesis Seeding
    print("\n[+] STEP 0: Engaging OpenAI GPT-6 Astra Advisor for Cartographic & Nihilist Seeding...")
    astra_seeds = query_astra_cartographic_nihilist(model=model_name, timeout_secs=60.0)
    print(f"[*] Astra Analysis: {astra_seeds.get('nihilist_analysis', astra_seeds.get('hypotheses_summary'))}")
    
    keywords_pool = astra_seeds.get("seed_polybius_keywords", [
        "NIHILIST", "NIHIL", "SCHUVALOF", "SCHUWALOW", "ORDNANCESURVEY",
        "RETRIANGULATION", "CASSINI", "TRIGPOINT", "BENCHMARK",
        "KARTOGRAFIYA", "TOPOGRAFIYA", "AGAPEYEFF", "ROSSIYA",
    ])
    print(f"[*] Seeded Keywords ({len(keywords_pool)}): {', '.join(keywords_pool[:8])}...")
    if astra_seeds.get("candidate_cribs"):
        print(f"[*] Candidate Cribs: {', '.join(astra_seeds.get('candidate_cribs')[:5])}...")

    # Reset start_time so advisor network latency does not consume search budget
    loop.start_time = time.time()

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
    print(f"\n[*] H0 Direct: norm_score={eval_h0.quadgram_score:.2f}, total_Q={total_q_h0:.1f} (Marland Record={comp_h0['marland_record_q']}), chi_sq={comp_h0['candidate_chi_sq']:.1f}, status={comp_h0['competition_status']}")

    if attack_mode != "two_square":
        # 2. Module A: Reversed Kerckhoffs Double-Transposition Permutation Sweep
        print("\n[+] MODULE A: Reversed Kerckhoffs Double-Transposition Permutation Sweep...")
        base_14 = list(range(14))
        for i in range(iterations_per_module):
            if loop.is_time_exhausted():
                print("[!] Wall-clock time budget reached during Module A.")
                break
            
            row_key = base_14[:]
            col_key = base_14[:]
            rng.shuffle(row_key)
            rng.shuffle(col_key)

            transposed_pairs = engine.apply_reversed_kerckhoffs_double_transposition(
                pairs_196, row_key, col_key, width=14
            )
            pt = engine.decode_pair_stream(transposed_pairs)
            
            loop.evaluate_candidate(
                hypothesis_name=f"H_kerckhoffs_dtrans_{i}",
                key_class="reversed_kerckhoffs",
                key_desc=f"Row key {row_key[:4]}..., Col key {col_key[:4]}...",
                candidate_pt=pt,
            )

        # 3. Module B: 14th-Column Null Removal ($14 \times 13 = 182$ pairs)
        print("\n[+] MODULE B: 14th-Column Null Removal ($14 \\times 13 = 182$ pairs)...")
        base_13 = list(range(13))
        for i in range(iterations_per_module):
            if loop.is_time_exhausted():
                break

            col_order = base_13[:]
            rng.shuffle(col_order)
            transposed_182 = engine.apply_single_pair_transposition(pairs_182, width=13, col_order=col_order)
            pt_182 = engine.decode_pair_stream(transposed_182)

            loop.evaluate_candidate(
                hypothesis_name=f"H_col14_stripped_k13_{i}",
                key_class="null_removed_transposition",
                key_desc=f"14th-col removed, 13-col perm {col_order[:4]}...",
                candidate_pt=pt_182,
            )

        # 4. Module C: Position 97 Correction ($04 \\to 75$) + Kerckhoffs
        print("\n[+] MODULE C: Position 97 Correction ($04 \\to 75$) + Kerckhoffs Sweeps...")
        corrected_pairs = engine.apply_position_97_correction(pairs_196, replacement="75")
        for i in range(iterations_per_module):
            if loop.is_time_exhausted():
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
        ru_scorer = QuadgramScorer(language="russian_translit")

        for kw in keywords_pool[:12]:
            if loop.is_time_exhausted():
                break

            alpha = make_polybius_alphabet(kw)
            kw_engine = KerckhoffsEngine(key_alphabet=alpha)
            
            # Test direct reading with keyword square
            pt_kw = kw_engine.decode_pair_stream(pairs_196)
            ru_score_kw = ru_scorer.score(pt_kw)
            loop.evaluate_candidate(
                hypothesis_name=f"H_nihilist_kw_{kw}",
                key_class="russian_nihilist_keyword",
                key_desc=f"Polybius square with keyword '{kw}' (ru_score={ru_score_kw:.2f})",
                candidate_pt=pt_kw,
            )

    # 6. Module E: High-Throughput Cartographic Guided Annealing with Nihilist Additive Keys
    if enable_joint_annealing:
        print("\n[+] MODULE E: Exhaustive Annealing with Nihilist Additive Keys (~16k trials/s)...")
        print("    Testing Secondary Additive Keys: [PRE-TRANSPOSITION vs POST-TRANSPOSITION vs NONE]")
        print("    Targeting 14x13 Grid (182 pairs) with Ordnance Survey & Nihilist Additive Periods")
        
        # Grid modes (70% 14x13_stripped)
        modes = [
            "14x13_stripped", "14x13_stripped", "14x13_stripped",
            "pos97_corrected", "14x14", "14x13_stripped",
        ]
        # Two-Square parameter rotations
        two_sq_orientations = ["vertical", "vertical", "horizontal"]
        two_sq_dual = [True, True, False]
        two_sq_pairings = ["sequential", "vertical_grid"]
        two_sq_trans = [False, False, True]

        # Rotating additive orders
        additive_orders = ["post_transposition", "pre_transposition", "post_transposition", "none"]
        additive_keywords = [
            "SCHUVALOF", "NIHILIST", "AGAPEYEFF", "MOSKVA",
            "ORDNANCE", "RUSSIAN", "PETROGRAD", "CASSINI", None,
        ]
        additive_periods = [5, 7, 8, 9, 10, 13, 14]
        
        languages = ["english", "english", "russian_translit"]
        chain_idx = 0

        while not loop.is_time_exhausted():
            chain_idx += 1
            mode = modes[(chain_idx - 1) % len(modes)]
            lang = languages[(chain_idx - 1) % len(languages)]
            seed_kw = rng.choice(keywords_pool)
            seed_kw2 = rng.choice(keywords_pool)

            remaining_s = loop.time_budget_secs - (time.time() - loop.start_time)
            if remaining_s <= 5:
                break
            
            chain_duration = min(75.0, remaining_s)
            elapsed_m = (time.time() - loop.start_time) / 60.0

            if attack_mode in ("two_square", "hybrid") and (attack_mode == "two_square" or chain_idx % 2 == 1):
                # Execute Two-Square Chain
                orient = two_sq_orientations[(chain_idx - 1) % len(two_sq_orientations)]
                is_dual = two_sq_dual[(chain_idx - 1) % len(two_sq_dual)]
                pairing = two_sq_pairings[(chain_idx - 1) % len(two_sq_pairings)]
                trans = two_sq_trans[(chain_idx - 1) % len(two_sq_trans)]

                two_sq_desc = f"{orient}_dual{is_dual}_pair{pairing}_trans{trans}"
                print(f"\n  [*] Two-Square Chain {chain_idx} [{elapsed_m:.2f}/{time_budget_mins:.1f}m]: {orient} (dual={is_dual}, pairing={pairing}, trans={trans}), grid={mode}, kw=({seed_kw}, {seed_kw2}), budget={chain_duration:.0f}s")

                annealer_ts = TwoSquareAnnealer(
                    grid_mode=mode,
                    orientation=orient,
                    dual_alphabets=is_dual,
                    pairing_mode=pairing,
                    with_transposition=trans,
                    language=lang,
                    seed_keyword1=seed_kw,
                    seed_keyword2=seed_kw2,
                    lexical_bonus_weight=0.15,
                    seed=rng.randint(1, 100000),
                )

                best_chain_state = annealer_ts.run_two_square_chain(
                    duration_secs=chain_duration,
                    initial_temp=20.0,
                    cooling_rate=0.9998,
                    loop=loop,
                )

                matched_terms = [t for t in ORDNANCE_SURVEY_TERMS + NIHILIST_INDICATOR_TERMS if t in best_chain_state.candidate_pt]

                eval_res = loop.evaluate_candidate(
                    hypothesis_name=f"H_two_square_{orient}_{mode}_{lang}_c{chain_idx}",
                    key_class=f"two_square_{orient}_{mode}",
                    key_desc=f"Two-Square {orient} (dual={is_dual}, pair={pairing}, trans={trans}), Annealed {lang} (Q={best_chain_state.score_q:.1f}), Alpha1={best_chain_state.alphabet1[:8]}...",
                    candidate_pt=best_chain_state.candidate_pt,
                )

                total_q = loop.scorer.score_total(best_chain_state.candidate_pt)
                comp = evaluate_against_competition(
                    total_q,
                    eval_res.metadata.get("chi_squared", 999.0),
                    eval_res.index_of_coincidence,
                    len(best_chain_state.candidate_pt),
                )
                print(f"      Two-Square Result: Q={total_q:.1f} (Marland Record: {comp['marland_record_q']}, Delta: {comp['delta_q']:+.1f}), chi_sq={comp['candidate_chi_sq']:.1f}, status={comp['competition_status']}")
                if matched_terms:
                    print(f"      [!] Emergent Cartographic / Nihilist Matches: {matched_terms}")
            elif attack_mode == "desync":
                # Execute Desynchronization Slip / Traverse Chain
                desync_types = ["boustrophedon", "dropped_slip", "diagonal", "split_pos97", "inserted_slip"]
                att_type = desync_types[(chain_idx - 1) % len(desync_types)]
                print(f"\n  [*] Desync Slip Chain {chain_idx} [{elapsed_m:.2f}/{time_budget_mins:.1f}m]: type={att_type}, grid={mode}, lang={lang}, seed_kw={seed_kw}, budget={chain_duration:.0f}s")

                annealer_desync = DesyncAnnealer(
                    attack_type=att_type,
                    grid_mode=mode,
                    language=lang,
                    seed_keyword=seed_kw,
                    lexical_bonus_weight=0.15,
                    seed=rng.randint(1, 100000),
                )

                best_chain_state = annealer_desync.run_desync_chain(
                    duration_secs=chain_duration,
                    initial_temp=20.0,
                    cooling_rate=0.9998,
                    loop=loop,
                )

                matched_terms = [t for t in ORDNANCE_SURVEY_TERMS + NIHILIST_INDICATOR_TERMS if t in best_chain_state.candidate_pt]

                eval_res = loop.evaluate_candidate(
                    hypothesis_name=f"H_desync_{att_type}_{mode}_{lang}_c{chain_idx}",
                    key_class=f"desync_{att_type}_{mode}",
                    key_desc=f"Desync {att_type} (param={best_chain_state.slip_parameter}), Annealed {lang} (Q={best_chain_state.score_q:.1f}), Alpha={best_chain_state.alphabet[:8]}...",
                    candidate_pt=best_chain_state.candidate_pt,
                )

                total_q = loop.scorer.score_total(best_chain_state.candidate_pt)
                comp = evaluate_against_competition(
                    total_q,
                    eval_res.metadata.get("chi_squared", 999.0),
                    eval_res.index_of_coincidence,
                    len(best_chain_state.candidate_pt),
                )
                print(f"      Desync Result: Q={total_q:.1f} (Marland Record: {comp['marland_record_q']}, Delta: {comp['delta_q']:+.1f}), chi_sq={comp['candidate_chi_sq']:.1f}, status={comp['competition_status']}")
                if matched_terms:
                    print(f"      [!] Emergent Cartographic / Nihilist Matches: {matched_terms}")
                print(f"      Plaintext Preview: \"{best_chain_state.candidate_pt[:60]}...\"")

            else:
                # Execute Joint Transposition / Additive Chain
                add_order = additive_orders[(chain_idx - 1) % len(additive_orders)]
                add_kw = additive_keywords[(chain_idx - 1) % len(additive_keywords)]
                add_period = 0 if add_order == "none" else (len(add_kw) if add_kw else rng.choice(additive_periods))
                add_desc = f"{add_order} (kw={add_kw}, L={add_period})" if add_order != "none" else "none"
                print(f"\n  [*] Joint Additive Chain {chain_idx} [{elapsed_m:.2f}/{time_budget_mins:.1f}m]: mode={mode}, lang={lang}, seed_kw={seed_kw}, additive={add_desc}, budget={chain_duration:.0f}s")
                
                annealer = JointDagapeyeffAnnealer(
                    grid_mode=mode,
                    language=lang,
                    seed_keyword=seed_kw,
                    lexical_bonus_weight=0.15,
                    additive_order=add_order,
                    additive_key_period=add_period,
                    initial_additive_keyword=add_kw,
                    seed=rng.randint(1, 100000),
                )
                
                best_chain_state = annealer.run_annealing_chain(
                    duration_secs=chain_duration,
                    initial_temp=25.0,
                    cooling_rate=0.9997,
                    loop=loop,
                )

                matched_terms = [t for t in ORDNANCE_SURVEY_TERMS + NIHILIST_INDICATOR_TERMS if t in best_chain_state.candidate_pt]

                eval_res = loop.evaluate_candidate(
                    hypothesis_name=f"H_additive_{add_order}_{mode}_{lang}_c{chain_idx}",
                    key_class=f"additive_{add_order}_{mode}",
                    key_desc=f"Additive {add_desc}, Annealed {lang} (Q={best_chain_state.score_q:.1f}), Alpha={best_chain_state.alphabet[:8]}...",
                    candidate_pt=best_chain_state.candidate_pt,
                )
                
                total_q = loop.scorer.score_total(best_chain_state.candidate_pt)
                comp = evaluate_against_competition(
                    total_q,
                    eval_res.metadata.get("chi_squared", 999.0),
                    eval_res.index_of_coincidence,
                    len(best_chain_state.candidate_pt),
                )
                print(f"      Chain Result: Q={total_q:.1f} (Marland Record: {comp['marland_record_q']}), chi_sq={comp['candidate_chi_sq']:.1f}, status={comp['competition_status']}")
                if matched_terms:
                    print(f"      [!] Emergent Cartographic / Nihilist Matches: {matched_terms}")
                print(f"      Plaintext Preview: \"{best_chain_state.candidate_pt[:60]}...\"")

    # Final Checkpointing & Statistics
    loop.save_checkpoint()
    summary = loop.ledger.get_summary_statistics("dagapeyeff_1939")
    print("\n" + "=" * 80)
    print("CONTINUOUS DISCOVERY RUN COMPLETE - SUMMARY")
    print(f"Total Trials Recorded in Ledger: {summary['total_trials_denominator']}")
    print(f"Bonferroni Adjusted Threshold: {summary['bonferroni_critical_p']:.8f}")
    if loop.best_candidate:
        total_q_best = loop.best_candidate.quadgram_score * (196 - 3)
        best_comp = evaluate_against_competition(
            total_q_best,
            loop.best_candidate.metadata.get("chi_squared", 999.0),
            loop.best_candidate.index_of_coincidence,
            196,
        )
        print(f"Best Candidate: {loop.best_candidate.hypothesis_name}")
        print(f"Best Q-Score (196-char): {total_q_best:.1f} (Marland Record: {best_comp['marland_record_q']})")
        print(f"Competition Status: {best_comp['competition_status']}")
        print(f"Plaintext Sample: \"{loop.best_candidate.plaintext_preview}\"")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="D'Agapeyeff Autonomous Competitive Discovery Runner")
    parser.add_argument("--time-budget-mins", default=60.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--iterations", default=25, type=int, help="Iterations per module")
    parser.add_argument("--enable-joint-annealing", action="store_true", default=True, help="Enable joint simulated annealing")
    parser.add_argument("--attack-mode", default="two_square", choices=["two_square", "joint_additive", "hybrid", "desync"], help="Attack mode")
    parser.add_argument("--model", default="gpt-6-astra", type=str, help="LLM referee and advisor model")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    args = parser.parse_args()

    run_competitive_discovery(
        data_dir=args.data_dir,
        time_budget_mins=args.time_budget_mins,
        iterations_per_module=args.iterations,
        enable_joint_annealing=args.enable_joint_annealing,
        attack_mode=args.attack_mode,
        model_name=args.model,
    )


if __name__ == "__main__":
    main()
