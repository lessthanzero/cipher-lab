"""Node 1 (macOS Apple Silicon) Discovery Engine for Dorabella Cipher.

Explores:
1. Holistic keyword columnar transpositions + simulated annealing.
2. 3x8 and 8x3 Polybius coordinate checkerboards (row-major, col-major, compass rotations).
3. Periodic polyalphabetic (Vigenère/Beaufort) period sweeps.
4. Musical contour and Solfège voice-leading evaluations.
5. Double-blind local models refereeing with negative-control foils.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict

from cipher_lab.harness import ModelRefereeHarness
from cipher_lab.stats import QuadgramScorer, calculate_chi_squared, calculate_index_of_coincidence

from projects.dorabella.annealer import DorabellaAnnealer
from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.holistic import HolisticDorabellaContext
from projects.dorabella.hypotheses import ALPHABET_24, scramble_tokens
from projects.dorabella.musical_cipher import MusicalCipherEvaluator
from projects.dorabella.symbols import decode_tokens
from projects.dorabella.transposition_solver import DorabellaTranspositionSolver


def run_discovery_mac(
    time_budget_mins: float = 9.5,
    output_path: Path = Path("data/derived/mac_dorabella_trials.jsonl"),
    seed: int = 42,
    run_llm: bool = True,
) -> None:
    scorer = QuadgramScorer(language="english")
    holistic = HolisticDorabellaContext()
    trans_solver = DorabellaTranspositionSolver()
    keywords = list(set(holistic.get_lexicon_cribs() + [
        "MALVERN", "GREATMALVERN", "WOLVERHAMPTON", "SEVERN", "HASFIELD", "BIRCHWOOD",
        "WORCESTER", "POWICK", "FORLI", "DAN", "BULLDOG", "RIVERWYE", "KITE",
        "ARK", "SULPHURETTED", "STAMMER", "CURLEW", "BLACKBIRD", "EDWARDELGAR",
        "DORAPENNY", "DORABELLA", "CARICE", "ALICE", "JUBILEE", "IMPERIAL",
        "RECTORY", "VARIATIONS", "ENIGMA", "SOLOMON", "MELANESIA", "TALISMAN", "MISSION"
    ]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    f_out = open(output_path, "a")

    def record_trial(trial_data: Dict[str, Any]) -> None:
        f_out.write(json.dumps(trial_data) + "\n")
        f_out.flush()

    start_time = time.time()
    time_budget_secs = time_budget_mins * 60.0
    print(f"[*] Node 1 (macOS): Launching Free-Roam Discovery (Budget: {time_budget_mins:.1f} mins)...", flush=True)

    trial_idx = 0
    best_overall_q = -float("inf")
    best_overall_cand: Dict[str, Any] = {}

    # Stage 1: Exhaustive 3x8 and 8x3 Coordinate Checkerboard Sweeps
    print("[*] Node 1: Stage 1 - Sweeping 3x8 & 8x3 Coordinate Checkerboards...", flush=True)
    for kw in keywords:
        if (time.time() - start_time) > time_budget_secs:
            break
        # Build 24-letter keyed alphabet
        clean = ""
        for c in kw.upper().replace("J", "I").replace("Z", "S"):
            if c in ALPHABET_24 and c not in clean:
                clean += c
        for c in ALPHABET_24:
            if c not in clean:
                clean += c

        for grid_shape in [(3, 8), (8, 3)]:
            rows, cols = grid_shape
            for fill_order in ["row_major", "col_major"]:
                for hump_order in [(0, 1, 2), (2, 1, 0), (1, 0, 2)]:
                    for col_dir in [1, -1]:
                        for col_offset in range(cols):
                            trial_idx += 1
                            pt_chars = []
                            for t in DORABELLA_TOKENS:
                                h = t // 8
                                ori = t % 8
                                r = hump_order[h] % rows
                                c = (col_dir * ori + col_offset) % cols
                                cell_idx = (r * cols + c) if fill_order == "row_major" else (c * rows + r)
                                pt_chars.append(clean[cell_idx % 24])

                            text = "".join(pt_chars)
                            q = scorer.score_total(text)
                            ioc = calculate_index_of_coincidence(text)
                            chi = calculate_chi_squared(text)

                            if q > best_overall_q:
                                best_overall_q = q
                                best_overall_cand = {"type": "checkerboard", "kw": kw, "q": q, "pt": text}

                            record_trial({
                                "node": "darwin_m1",
                                "trial_id": f"mac_chk_{trial_idx}",
                                "family": "coordinate_checkerboard",
                                "keyword": kw,
                                "grid_shape": f"{rows}x{cols}",
                                "fill_order": fill_order,
                                "q_score": q,
                                "ioc": ioc,
                                "chi_squared": chi,
                                "plaintext_preview": text[:50],
                            })

    print(f"[*] Node 1: Completed Stage 1. Trials: {trial_idx} | Best Q so far: {best_overall_q:.1f}", flush=True)

    # Stage 2: Keyword Columnar Transpositions + Simulated Annealing Restarts
    print("[*] Node 1: Stage 2 - Keyword Columnar Transposition + Annealing Restarts...", flush=True)
    chain_idx = 0
    while (time.time() - start_time) < (time_budget_secs * 0.75):
        kw = keywords[chain_idx % len(keywords)]
        chain_idx += 1
        trial_idx += 1

        # Transpose tokens under keyword
        t_tokens = trans_solver.columnar_keyword_transposition(kw)
        t_annealer = DorabellaAnnealer(scorer=scorer, tokens=t_tokens)
        res = t_annealer.anneal(duration_secs=1.5, seed=seed + trial_idx)

        if res.q_score > best_overall_q:
            best_overall_q = res.q_score
            best_overall_cand = {"type": "transposed_anneal", "kw": kw, "q": res.q_score, "pt": res.plaintext}

        record_trial({
            "node": "darwin_m1",
            "trial_id": f"mac_trans_sa_{trial_idx}",
            "family": "transposed_simulated_annealing",
            "keyword": kw,
            "q_score": res.q_score,
            "ioc": res.ioc,
            "chi_squared": res.chi_sq,
            "plaintext_preview": res.plaintext[:50],
        })

        if chain_idx % 10 == 0:
            elapsed = time.time() - start_time
            print(f"    [Elapsed: {elapsed:.0f}s / {time_budget_secs:.0f}s] Chain {chain_idx}: Kw='{kw}' | Best Q: {best_overall_q:.1f}", flush=True)

    # Stage 3: Musical Cipher Scale & Contour Sweeps
    print("[*] Node 1: Stage 3 - Musical Interval & Tonal Contour Search...", flush=True)
    music_eval = MusicalCipherEvaluator()
    for root in range(8):
        score = music_eval.score_melodic_fluency(root)
        trial_idx += 1
        record_trial({
            "node": "darwin_m1",
            "trial_id": f"mac_music_{root}",
            "family": "musical_diatonic_contour",
            "root_offset": root,
            "melodic_score": score,
        })

    # Stage 4: Local Model Referee Pass on Best Overall Candidate
    if run_llm and best_overall_cand:
        print("\n[*] Node 1: Stage 4 - Local Model Referee Pass (Double-Blind Foils)...", flush=True)
        try:
            referee = ModelRefereeHarness()
            decoy_map = {t: ALPHABET_24[t % 24] for t in range(24)}
            decoy_1 = decode_tokens(scramble_tokens(DORABELLA_TOKENS, seed=777), decoy_map)
            decoy_2 = decode_tokens(scramble_tokens(DORABELLA_TOKENS, seed=888), decoy_map)

            ref_res = referee.evaluate_with_blinded_foils(
                candidate_plaintext=best_overall_cand["pt"],
                decoy_plaintexts=[decoy_1, decoy_2],
                artifact_context="Edward Elgar's 1897 encrypted note to Dora Penny at Wolverhampton Rectory.",
                preferred_model="phi4-mini:latest",
            )
            print(f"    - Blind Referee Result: Option [{ref_res.get('selected_option', 'NONE')}] | Score: {ref_res.get('linguistic_coherence_score', 0.0):.2f}")
            record_trial({
                "node": "darwin_m1",
                "trial_id": "mac_llm_referee",
                "family": "model_referee",
                "candidate_q": best_overall_cand["q"],
                "referee_result": ref_res,
            })
        except Exception as e:
            print(f"    [!] LLM Referee warning: {e}")

    f_out.close()
    elapsed = time.time() - start_time
    print(f"\n[+] Node 1 (macOS) Discovery Complete in {elapsed:.1f}s. Total trials: {trial_idx} | Best Q: {best_overall_q:.1f}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Node 1 macOS Dorabella Discovery Engine")
    parser.add_argument("--budget-mins", type=float, default=9.5, help="Time budget in minutes")
    parser.add_argument("--output", type=Path, default=Path("data/derived/mac_dorabella_trials.jsonl"), help="Output JSONL")
    parser.add_argument("--seed", type=int, default=42, help="Seed")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM referee")
    args = parser.parse_args()

    run_discovery_mac(
        time_budget_mins=args.budget_mins,
        output_path=args.output,
        seed=args.seed,
        run_llm=not args.no_llm,
    )
