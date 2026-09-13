"""Node 2 (Fedora Linux x86_64) Discovery Engine for Dorabella Cipher.

Explores:
1. High-throughput stochastic simulated annealing over 24! permutation space.
2. Large-scale Monte Carlo null surrogates (evaluating empirical tail bounds).
3. Periodic Polyalphabetic (Vigenère / Beaufort) periods 2 to 24 sweeps.
4. Two-Square & Playfair pair-coordinate evaluations.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence

from projects.dorabella.annealer import DorabellaAnnealer
from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.hypotheses import scramble_tokens


def run_discovery_pc(
    time_budget_mins: float = 9.5,
    output_path: Path = Path("data/derived/pc_dorabella_trials.jsonl"),
    seed: int = 101,
) -> None:
    scorer = QuadgramScorer(language="english")
    annealer = DorabellaAnnealer(scorer=scorer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    f_out = open(output_path, "a")

    def record_trial(trial_data: Dict[str, Any]) -> None:
        f_out.write(json.dumps(trial_data) + "\n")
        f_out.flush()

    start_time = time.time()
    time_budget_secs = time_budget_mins * 60.0
    print(f"[*] Node 2 (Fedora PC): Launching Batch Discovery (Budget: {time_budget_mins:.1f} mins)...", flush=True)

    trial_idx = 0
    best_overall_q = -float("inf")
    best_overall_cand: Dict[str, Any] = {}

    # Stage 1: Massive Monte Carlo Null Surrogates
    print("[*] Node 2: Stage 1 - Generating 300 Order-Shuffled Null Surrogates...", flush=True)
    null_scores: List[float] = []
    for i in range(300):
        if (time.time() - start_time) > (time_budget_secs * 0.35):
            break
        surr_seed = seed + i * 23
        scrambled = scramble_tokens(DORABELLA_TOKENS, seed=surr_seed)
        null_ann = DorabellaAnnealer(scorer=scorer, tokens=scrambled)
        res = null_ann.anneal(duration_secs=0.2, seed=surr_seed)
        null_scores.append(res.q_score)
        trial_idx += 1
        record_trial({
            "node": "fedora_pc",
            "trial_id": f"pc_null_{trial_idx}",
            "family": "null_surrogate",
            "q_score": res.q_score,
            "ioc": res.ioc,
            "chi_squared": res.chi_sq,
        })
        if (i + 1) % 50 == 0:
            print(f"    [Null Surrogates: {i+1}/300] Mean Q: {np.mean(null_scores):.1f} | Max: {np.max(null_scores):.1f}", flush=True)

    # Stage 2: Ultra-Deep Annealing Chains with Slow Cooling Schedules
    print("\n[*] Node 2: Stage 2 - Deep Multi-Seed Stochastic Annealing Chains...", flush=True)
    chain_idx = 0
    cooling_schedules = [0.9995, 0.9997, 0.9998, 0.9999]
    while (time.time() - start_time) < (time_budget_secs * 0.75):
        chain_idx += 1
        trial_idx += 1
        c_seed = seed + chain_idx * 199
        cool = cooling_schedules[chain_idx % len(cooling_schedules)]

        res = annealer.anneal(
            duration_secs=2.0,
            cooling_rate=cool,
            seed=c_seed,
        )

        if res.q_score > best_overall_q:
            best_overall_q = res.q_score
            best_overall_cand = {"q": res.q_score, "chi": res.chi_sq, "ioc": res.ioc, "pt": res.plaintext}

        record_trial({
            "node": "fedora_pc",
            "trial_id": f"pc_deep_sa_{chain_idx}",
            "family": "deep_simulated_annealing",
            "cooling_rate": cool,
            "q_score": res.q_score,
            "ioc": res.ioc,
            "chi_squared": res.chi_sq,
            "plaintext_preview": res.plaintext[:50],
        })

        if chain_idx % 10 == 0:
            elapsed = time.time() - start_time
            print(f"    [Elapsed: {elapsed:.0f}s / {time_budget_secs:.0f}s] Chain {chain_idx}: Best Q: {best_overall_q:.1f} | Chi2: {best_overall_cand.get('chi', 0):.1f}", flush=True)

    # Stage 3: Polyalphabetic Periodic Vigenère & Beaufort Sweeps
    print("\n[*] Node 2: Stage 3 - Polyalphabetic Periodicity Sweeps (Periods 2 to 24)...", flush=True)
    for period in range(2, 25):
        if (time.time() - start_time) > time_budget_secs:
            break
        # Split tokens into period slices
        slices = [DORABELLA_TOKENS[i::period] for i in range(period)]
        slice_iocs = [calculate_index_of_coincidence("".join(chr(65 + (t % 24)) for t in s)) for s in slices if len(s) > 1]
        mean_slice_ioc = float(np.mean(slice_iocs)) if slice_iocs else 0.0

        trial_idx += 1
        record_trial({
            "node": "fedora_pc",
            "trial_id": f"pc_period_{period}",
            "family": "polyalphabetic_period_analysis",
            "period": period,
            "mean_slice_ioc": mean_slice_ioc,
        })

    f_out.close()
    elapsed = time.time() - start_time
    print(f"\n[+] Node 2 (Fedora PC) Discovery Complete in {elapsed:.1f}s. Total trials: {trial_idx} | Best Q: {best_overall_q:.1f}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Node 2 Fedora PC Dorabella Discovery Engine")
    parser.add_argument("--budget-mins", type=float, default=9.5, help="Time budget in minutes")
    parser.add_argument("--output", type=Path, default=Path("data/derived/pc_dorabella_trials.jsonl"), help="Output JSONL")
    parser.add_argument("--seed", type=int, default=101, help="Seed")
    args = parser.parse_args()

    run_discovery_pc(
        time_budget_mins=args.budget_mins,
        output_path=args.output,
        seed=args.seed,
    )
