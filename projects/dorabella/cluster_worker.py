"""Cluster Worker for Dorabella Cipher: Batch Monte Carlo Null Surrogates & Annealing.

Designed for high-throughput execution across multi-node compute clusters
(Apple Silicon macOS + Fedora Linux x86_64 worker 'pc').
Generates 1,000 to 10,000 order-shuffled surrogate cryptograms preserving exact
token marginal frequencies to establish the empirical null distribution Q_null.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from cipher_lab.stats import QuadgramScorer

from projects.dorabella.annealer import DorabellaAnnealer
from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.hypotheses import scramble_tokens


def run_surrogate_monte_carlo(
    num_surrogates: int = 100,
    anneal_duration_secs: float = 0.5,
    seed: int = 42,
    output_path: Path | None = None,
) -> Dict[str, Any]:
    """Generate empirical null score distribution across order-shuffled surrogates."""
    scorer = QuadgramScorer(language="english")
    null_scores: List[float] = []

    start_time = time.time()
    print(f"[*] Cluster Worker: Starting Monte Carlo null simulation ({num_surrogates} surrogates)...", flush=True)

    for i in range(num_surrogates):
        surr_seed = seed + i * 17
        scrambled = scramble_tokens(DORABELLA_TOKENS, seed=surr_seed)
        annealer = DorabellaAnnealer(scorer=scorer, tokens=scrambled)
        res = annealer.anneal(duration_secs=anneal_duration_secs, seed=surr_seed)
        null_scores.append(res.q_score)

        if (i + 1) % max(1, num_surrogates // 5) == 0:
            print(f"    [{i+1}/{num_surrogates}] Mean Q_null: {np.mean(null_scores):.2f} | Max: {np.max(null_scores):.2f}", flush=True)

    elapsed = time.time() - start_time
    arr = np.array(null_scores)
    summary = {
        "num_surrogates": num_surrogates,
        "elapsed_seconds": elapsed,
        "q_null_mean": float(np.mean(arr)),
        "q_null_std": float(np.std(arr)),
        "q_null_min": float(np.min(arr)),
        "q_null_max": float(np.max(arr)),
        "q_null_p95": float(np.percentile(arr, 95)),
        "q_null_p99": float(np.percentile(arr, 99)),
    }

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump({"summary": summary, "scores": null_scores}, f, indent=2)

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Dorabella Cluster Monte Carlo Worker")
    parser.add_argument("--surrogates", type=int, default=50, help="Number of null surrogates")
    parser.add_argument("--duration", type=float, default=0.5, help="Anneal duration per surrogate (seconds)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--output", type=str, default="data/derived/dorabella_null_surrogates.json")
    args = parser.parse_args()

    summary = run_surrogate_monte_carlo(
        num_surrogates=args.surrogates,
        anneal_duration_secs=args.duration,
        seed=args.seed,
        output_path=Path(args.output),
    )
    print("\n[+] Monte Carlo Null Simulation Complete:", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
