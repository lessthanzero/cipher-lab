"""High-throughput Monte Carlo null surrogate batch worker for Fedora PC (x86_64).

Executes parallel permutation testing (N=50,000-100,000 iterations) across the 4 core
Indus script discrimination hypotheses:
  H1: Positional Slot-Filler Rigidity
  H2: Sign Repetition Deficit
  H3: Conditional Block Entropy under Hostile Nulls
  H4: Unicity & Combinatorial Space Bounds
"""

from __future__ import annotations

import argparse
import collections
import json
import math
import random
import sys
import time
from pathlib import Path
from typing import Any, Counter, Dict, List, Sequence, Tuple

base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

import numpy as np


def fast_shannon_entropy(tokens: Sequence[str]) -> float:
    n = len(tokens)
    if n == 0:
        return 0.0
    counts = collections.Counter(tokens)
    ent = 0.0
    for c in counts.values():
        p = c / n
        ent -= p * math.log2(p)
    return ent


def fast_conditional_entropy(sequences: Sequence[Sequence[str]]) -> tuple[float, float, float]:
    """Compute H0, H1, H2 efficiently."""
    unigrams: Counter[str] = collections.Counter()
    bigrams: Counter[tuple[str, str]] = collections.Counter()
    trigrams: Counter[tuple[str, str, str]] = collections.Counter()

    for seq in sequences:
        for s in seq:
            unigrams[s] += 1
        for i in range(len(seq) - 1):
            bigrams[(seq[i], seq[i + 1])] += 1
        for i in range(len(seq) - 2):
            trigrams[(seq[i], seq[i + 1], seq[i + 2])] += 1

    total_uni = sum(unigrams.values())
    total_bi = sum(bigrams.values())
    total_tri = sum(trigrams.values())

    h0 = 0.0
    for c in unigrams.values():
        p = c / total_uni
        h0 -= p * math.log2(p)

    h1 = 0.0
    for (w1, _w2), bg_c in bigrams.items():
        p_bg = bg_c / total_bi
        p_w1 = unigrams[w1] / total_uni
        if p_w1 > 0:
            h1 -= p_bg * math.log2((bg_c / total_bi) / p_w1)

    h2 = 0.0
    for (w1, w2, _w3), tg_c in trigrams.items():
        p_tg = tg_c / total_tri
        p_bg = bigrams[(w1, w2)] / total_bi
        if p_bg > 0:
            h2 -= p_tg * math.log2((tg_c / total_tri) / p_bg)

    return h0, max(h1, 0.0), max(h2, 0.0)


def fast_repetition_rate(sequences: Sequence[Sequence[str]]) -> float:
    texts_with_rep = 0
    for seq in sequences:
        counts = collections.Counter(seq)
        if any(c > 1 for c in counts.values()):
            texts_with_rep += 1
    return texts_with_rep / max(len(sequences), 1)


def fast_edge_variance(sequences: Sequence[Sequence[str]]) -> float:
    """Measure edge-to-middle entropy variance."""
    pos_tokens: dict[int, list[str]] = collections.defaultdict(list)
    for seq in sequences:
        for p, s in enumerate(seq[:5]):
            pos_tokens[p].append(s)
    
    entropies = [fast_shannon_entropy(pos_tokens[p]) for p in sorted(pos_tokens.keys())]
    if len(entropies) >= 2:
        return float(np.var(entropies))
    return 0.0


def run_batch_simulation(
    inscriptions_path: Path,
    n_iterations: int = 50000,
    seed: int = 42,
) -> dict[str, Any]:
    """Execute high-sample Monte Carlo permutation tests."""
    with open(inscriptions_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sequences = [item["signs"] for item in data]
    all_tokens = [s for seq in sequences for s in seq]
    unique_signs = sorted(list(set(all_tokens)))
    
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    # 1. Observed metrics
    obs_h0, obs_h1, obs_h2 = fast_conditional_entropy(sequences)
    obs_rep = fast_repetition_rate(sequences)
    obs_edge_var = fast_edge_variance(sequences)

    # Pre-aggregate positional columns for Null 3
    by_pos: dict[int, list[str]] = collections.defaultdict(list)
    for seq in sequences:
        for p, sign in enumerate(seq):
            by_pos[p].append(sign)

    # Null metric collectors
    null_freq_h1 = np.empty(n_iterations, dtype=np.float64)
    null_pos_h1 = np.empty(n_iterations, dtype=np.float64)
    null_unigram_rep = np.empty(n_iterations, dtype=np.float64)
    null_unif_edge_var = np.empty(n_iterations, dtype=np.float64)

    # Compute unigram sampling distribution for unconstrained language model
    sign_list = list(unique_signs)
    token_counts = collections.Counter(all_tokens)
    unigram_probs = np.array([token_counts[s] for s in sign_list], dtype=np.float64)
    unigram_probs /= np.sum(unigram_probs)

    t0 = time.time()

    for i in range(n_iterations):
        # Null 2: Frequency-preserving order shuffle
        shuffled_seqs_freq = []
        for seq in sequences:
            s = list(seq)
            rng.shuffle(s)
            shuffled_seqs_freq.append(s)

        _, h1_freq, _ = fast_conditional_entropy(shuffled_seqs_freq)
        null_freq_h1[i] = h1_freq

        # Null for H2: Independent draws from unigram distribution (unconstrained linguistic baseline)
        unigram_draw_seqs = [
            list(np_rng.choice(sign_list, size=len(seq), p=unigram_probs))
            for seq in sequences
        ]
        null_unigram_rep[i] = fast_repetition_rate(unigram_draw_seqs)

        # Null 3: Positional column shuffle
        shuffled_pos: dict[int, list[str]] = {}
        for p in by_pos:
            col = list(by_pos[p])
            rng.shuffle(col)
            shuffled_pos[p] = col

        shuffled_seqs_pos = []
        ptrs: dict[int, int] = collections.defaultdict(int)
        for seq in sequences:
            s_pos = []
            for p in range(len(seq)):
                s_pos.append(shuffled_pos[p][ptrs[p]])
                ptrs[p] += 1
            shuffled_seqs_pos.append(s_pos)

        _, h1_pos, _ = fast_conditional_entropy(shuffled_seqs_pos)
        null_pos_h1[i] = h1_pos

        # Null 1: Uniform draw edge variance
        unif_seqs = [
            [rng.choice(unique_signs) for _ in range(len(seq))]
            for seq in sequences
        ]
        null_unif_edge_var[i] = fast_edge_variance(unif_seqs)

    elapsed = time.time() - t0

    def compute_stats(obs: float, null_arr: np.ndarray, alt: str = "less") -> dict[str, Any]:
        mean_val = float(np.mean(null_arr))
        std_val = float(np.std(null_arr, ddof=1)) if len(null_arr) > 1 else 1e-6
        std_val = std_val if std_val > 0 else 1e-6
        z = (obs - mean_val) / std_val
        n = len(null_arr)
        if alt == "less":
            p = float(np.sum(null_arr <= obs) + 1) / (n + 1)
        elif alt == "greater":
            p = float(np.sum(null_arr >= obs) + 1) / (n + 1)
        else:
            p = float(np.sum(np.abs(null_arr - mean_val) >= np.abs(obs - mean_val)) + 1) / (n + 1)

        ci_low = float(np.percentile(null_arr, 2.5))
        ci_high = float(np.percentile(null_arr, 97.5))
        return {
            "observed": round(obs, 4),
            "null_mean": round(mean_val, 4),
            "null_std": round(std_val, 4),
            "z_score": round(z, 2),
            "p_value": round(p, 6),
            "ci_95": [round(ci_low, 4), round(ci_high, 4)],
            "is_significant_bonferroni": bool(p < (0.05 / 4)),  # Bonferroni threshold across 4 hypotheses
        }

    results = {
        "n_iterations": n_iterations,
        "elapsed_seconds": round(elapsed, 2),
        "iterations_per_second": round(n_iterations / max(elapsed, 0.001), 1),
        "observed_baseline": {
            "h0_bits": round(obs_h0, 3),
            "h1_bits": round(obs_h1, 3),
            "h2_bits": round(obs_h2, 3),
            "repetition_rate": round(obs_rep, 4),
            "edge_entropy_variance": round(obs_edge_var, 4),
        },
        "hypothesis_1_edge_variance_vs_uniform": compute_stats(obs_edge_var, null_unif_edge_var, alt="greater"),
        "hypothesis_2_repetition_rate_vs_unigram_draw": compute_stats(obs_rep, null_unigram_rep, alt="less"),
        "hypothesis_3a_h1_vs_frequency_preserving": compute_stats(obs_h1, null_freq_h1, alt="less"),
        "hypothesis_3b_h1_vs_positional_preserving": compute_stats(obs_h1, null_pos_h1, alt="less"),
    }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Indus Script Monte Carlo Permutation Sieve on Fedora PC")
    parser.add_argument("--inscriptions", type=str, default="data/indus/mohenjodaro_cisi_inscriptions.json")
    parser.add_argument("--iterations", type=int, default=50000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="data/derived/indus_monte_carlo_results.json")
    args = parser.parse_args()

    inscriptions_p = Path(args.inscriptions)
    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting Indus Monte Carlo Sieve: N={args.iterations} iterations, seed={args.seed}...")
    res = run_batch_simulation(inscriptions_p, n_iterations=args.iterations, seed=args.seed)
    
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    print(f"[✓] Complete in {res['elapsed_seconds']}s ({res['iterations_per_second']} iter/s). Saved to {out_p}")
    print(f"    - H1 Edge Variance vs Uniform:      Z={res['hypothesis_1_edge_variance_vs_uniform']['z_score']}, p={res['hypothesis_1_edge_variance_vs_uniform']['p_value']}")
    print(f"    - H2 Repetition vs Unigram Draw:    Z={res['hypothesis_2_repetition_rate_vs_unigram_draw']['z_score']}, p={res['hypothesis_2_repetition_rate_vs_unigram_draw']['p_value']}")
    print(f"    - H3a H1 vs Freq-Preserving:       Z={res['hypothesis_3a_h1_vs_frequency_preserving']['z_score']}, p={res['hypothesis_3a_h1_vs_frequency_preserving']['p_value']}")
    print(f"    - H3b H1 vs Positional-Preserving: Z={res['hypothesis_3b_h1_vs_positional_preserving']['z_score']}, p={res['hypothesis_3b_h1_vs_positional_preserving']['p_value']}")


if __name__ == "__main__":
    main()
