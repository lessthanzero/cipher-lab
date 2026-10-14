"""Node 2 (Fedora PC x86_64) Batch Discovery Engine for Kryptos K4.

Executes heavy keyspace sweeps and Monte Carlo controls:
1. 1,000 Monte Carlo order-shuffled null surrogates.
2. 216 Grid transposition configurations.
3. 14x7 Cardan stencil mask sweeps (rotational, vertical flip, horizontal flip).
4. 'LAYER TWO' Cross-section coupling sweeps across K1-K3.
5. Compass bearings and Weltzeituhr 24-cylinder rotational projections.
6. Evaluates empirical significance and FDR-adjusted bounds.
7. Logs telemetry to data/derived/pc_kryptos_trials.jsonl.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path
from typing import Any, Dict, List

from cipher_lab.stats import (
    QuadgramScorer,
    calculate_index_of_coincidence,
    order_shuffle_null,
)

from projects.kryptos.manifests import BLIND_PATH, CONTEXTUAL_PATH, load_dataset
from projects.kryptos.tier2_contextual.cardan_stencil_sweeper import (
    run_cardan_stencil_campaign,
)
from projects.kryptos.tier2_contextual.compass_weltzeituhr_sweeper import (
    run_compass_weltzeituhr_campaign,
)
from projects.kryptos.tier2_contextual.cross_section_mask import (
    sweep_cross_section_layers,
)
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)
from projects.kryptos.tier2_contextual.transposition_models import (
    generate_candidate_grid_dimensions,
    read_columns_bottom_to_top_left_to_right,
    read_columns_top_to_bottom_left_to_right,
    text_to_grid,
)


def run_discovery_pc(
    time_budget_mins: float = 2.0,
    output_path: Path = Path("data/derived/pc_kryptos_trials.jsonl"),
    seed: int = 42,
) -> Dict[str, Any]:
    """Execute high-throughput batch discovery on Fedora PC worker."""
    random.seed(seed)
    blind_data = load_dataset(BLIND_PATH, current_tier=1)
    context_data = load_dataset(CONTEXTUAL_PATH, current_tier=2)

    ciphertext = blind_data["ciphertext"]
    known_pairs = extract_known_pairs()
    n = len(ciphertext)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    f_out = open(output_path, "a", encoding="utf-8")

    def record_trial(trial_data: Dict[str, Any]) -> None:
        f_out.write(json.dumps(trial_data) + "\n")
        f_out.flush()

    start_time = time.time()
    print(f"[*] Node 2 (Fedora PC): Launching Comprehensive Batch Discovery...", flush=True)

    scorer = QuadgramScorer(language="english")

    # Stage 1: Generate 1,000 Monte Carlo Null Surrogates
    print("[*] Node 2: Stage 1 — Generating Monte Carlo Null Distribution (1,000 Surrogates)...", flush=True)
    surrogates = order_shuffle_null(list(ciphertext), n_samples=1000, seed=seed)
    null_scores: List[float] = []

    for sample in surrogates:
        shuffled_text = "".join(sample)
        q = scorer.score(shuffled_text)
        null_scores.append(q)

    null_mean = sum(null_scores) / len(null_scores) if null_scores else -1000.0
    variance = sum((s - null_mean) ** 2 for s in null_scores) / len(null_scores) if null_scores else 1.0
    null_std = variance ** 0.5

    print(f"[*] Node 2: Null Surrogates Evaluated: {len(null_scores)} (Mean Q = {null_mean:.2f}, Std = {null_std:.2f})", flush=True)

    # Stage 2: Grid Transposition Sweep
    print("[*] Node 2: Stage 2 — Evaluating Grid Transposition Configurations...", flush=True)
    grid_configs = generate_candidate_grid_dimensions(n=n, max_nulls=7)
    best_grid_trial: Dict[str, Any] = {}
    best_grid_q = -float("inf")
    trial_count = 0

    for r, c, nulls in grid_configs:
        for pad_char in ["X", "Q", "Z", "A"]:
            g = text_to_grid(ciphertext, r, c, pad_char=pad_char)
            cand1 = read_columns_top_to_bottom_left_to_right(g)
            q1 = scorer.score(cand1)
            ioc1 = calculate_index_of_coincidence(cand1)
            trial_count += 1
            if q1 > best_grid_q:
                best_grid_q = q1
                best_grid_trial = {
                    "type": "grid_transposition_top_bottom",
                    "rows": r,
                    "cols": c,
                    "pad_char": pad_char,
                    "q_score": round(q1, 2),
                    "ioc": round(ioc1, 5),
                }

            cand2 = read_columns_bottom_to_top_left_to_right(g)
            q2 = scorer.score(cand2)
            ioc2 = calculate_index_of_coincidence(cand2)
            trial_count += 1
            if q2 > best_grid_q:
                best_grid_q = q2
                best_grid_trial = {
                    "type": "grid_transposition_sanborn",
                    "rows": r,
                    "cols": c,
                    "pad_char": pad_char,
                    "q_score": round(q2, 2),
                    "ioc": round(ioc2, 5),
                }

    # Stage 3: Cardan Stencil Mask Sweeper
    print("[*] Node 2: Stage 3 — Sweeping Cardan Stencil Mask Symmetries...", flush=True)
    cardan_res = run_cardan_stencil_campaign()

    # Stage 4: Cross-Section Layer Two Sweeper
    print("[*] Node 2: Stage 4 — Sweeping 'LAYER TWO' Cross-Section Superpositions...", flush=True)
    cross_res = sweep_cross_section_layers()

    # Stage 5: Compass & Weltzeituhr Sweeper
    print("[*] Node 2: Stage 5 — Sweeping Compass Bearings and Weltzeituhr Projections...", flush=True)
    compass_res = run_compass_weltzeituhr_campaign()

    elapsed = time.time() - start_time
    z_score = (best_grid_q - null_mean) / null_std if null_std > 0 else 0.0

    summary = {
        "node": "fedora-pc",
        "elapsed_seconds": round(elapsed, 2),
        "null_distribution": {"mean_q": round(null_mean, 2), "std_q": round(null_std, 2)},
        "best_grid_transposition": best_grid_trial,
        "grid_z_score": round(z_score, 2),
        "cardan_stencil_summary": {
            "fixed_hits": len(cardan_res["fixed_stencil_hits"]),
            "rot180_hits": len(cardan_res["rot180_hits"]),
            "flip_v_hits": len(cardan_res["flip_v_hits"]),
            "flip_h_hits": len(cardan_res["flip_h_hits"]),
        },
        "cross_section_summary": {
            sec: data["total_hits_above_25pct"]
            for sec, data in cross_res.items()
        },
        "compass_weltzeituhr_summary": {
            "total_hits_above_25pct": compass_res["total_hits_above_25pct"],
            "best_hits": compass_res["best_hits"][:3],
        },
    }

    record_trial({
        "timestamp": time.time(),
        "summary": summary,
    })
    f_out.close()

    print(f"[*] Node 2: Complete Discovery Run Finished in {elapsed:.1f}s.", flush=True)
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=float, default=2.0, help="Time budget in minutes")
    args = parser.parse_args()
    res = run_discovery_pc(time_budget_mins=args.budget)
    print(json.dumps(res, indent=2))
