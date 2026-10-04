"""Heavy-throughput Monte Carlo breakthrough solver for Indus Script on Fedora PC.

Executes:
1. Spectral graph decomposition and eigengap analysis across Parpola and Mahadevan catalogs.
2. Objective HMM model selection sweep across K in 2..8 states (BIC/AIC global minimum).
3. N=10,000 permutation null testing on DAG compliance and MDL compression.
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

from projects.indus.corpus import IndusCorpus
from projects.indus.grammar_engine import IndusGrammarEngine
from projects.indus.hmm_induction import HMMTopologySweeper
from projects.indus.spectral_clustering import IndusSpectralClusterer


def run_breakthrough_simulation(
    data_dir: Path,
    n_permutations: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    t_start = time.time()
    corpus = IndusCorpus(data_dir)

    print(f"[*] Step 1: Spectral graph decomposition across Parpola & Mahadevan signaries...")
    clusterer_p = IndusSpectralClusterer(corpus, target_catalog="parpola")
    res_p = clusterer_p.decompose(n_clusters=5, seed=seed)

    clusterer_m = IndusSpectralClusterer(corpus, target_catalog="mahadevan")
    res_m = clusterer_m.decompose(n_clusters=5, seed=seed)

    print(f"    - Parpola: Eigengap at index {res_p.eigengap_index}, DAG feedforward ratio = {res_p.dag_feedforward_ratio}")
    print(f"    - Mahadevan: Eigengap at index {res_m.eigengap_index}, DAG feedforward ratio = {res_m.dag_feedforward_ratio}")

    print(f"[*] Step 2: HMM topology model selection sweep across K=2..8 states...")
    class_seqs = [
        [str(res_p.sign_to_class[s]) for s in seq]
        for seq in corpus.get_sequences("parpola")
    ]
    sweeper = HMMTopologySweeper(class_seqs)
    sweep_res = sweeper.sweep(k_values=[2, 3, 4, 5, 6, 7, 8], n_restarts=8, seed=seed)
    print(f"    - Best BIC K: {sweep_res.best_bic_k} (BIC = {sweep_res.min_bic})")
    print(f"    - Best AIC K: {sweep_res.best_aic_k}")

    print(f"[*] Step 3: Grammar engine evaluation & MDL complexity calculation...")
    grammar_engine = IndusGrammarEngine(corpus, target_catalog="parpola", n_classes=5, n_states=sweep_res.best_bic_k, seed=seed)
    grammar_rep = grammar_engine.evaluate_corpus()
    print(f"    - DAG feed-forward compliance rate: {grammar_rep.dag_compliance_rate * 100:.2f}%")
    print(f"    - MDL Compression Ratio: {grammar_rep.compression_ratio_percent:.2f}%")

    print(f"[*] Step 4: Monte Carlo permutation sieve on DAG compliance (N={n_permutations} iterations)...")
    rng = random.Random(seed)
    obs_compliance = grammar_rep.dag_compliance_rate

    raw_inscriptions = corpus.inscriptions
    all_tokens = [s for ins in raw_inscriptions for s in ins.signs]
    unique_signs = sorted(list(set(all_tokens)))

    null_freq_compliance = np.empty(n_permutations, dtype=np.float64)
    null_unif_compliance = np.empty(n_permutations, dtype=np.float64)

    # Pre-calculate token classes
    sign_to_c = grammar_engine.sign_to_class

    for i in range(n_permutations):
        # Null 2: Frequency-preserving within-sequence shuffle
        compliant_freq = 0
        for ins in raw_inscriptions:
            s_list = list(ins.signs)
            rng.shuffle(s_list)
            c_seq = [sign_to_c[s] for s in s_list]
            _, states = grammar_engine.viterbi_decode(c_seq)
            is_dag = True
            for t in range(len(states) - 1):
                if states[t + 1] < states[t]:
                    is_dag = False
                    break
            if is_dag:
                compliant_freq += 1
        null_freq_compliance[i] = compliant_freq / len(raw_inscriptions)

        # Null 1: Uniform random signs
        compliant_unif = 0
        for ins in raw_inscriptions:
            s_list = [rng.choice(unique_signs) for _ in range(len(ins.signs))]
            c_seq = [sign_to_c[s] for s in s_list]
            _, states = grammar_engine.viterbi_decode(c_seq)
            is_dag = True
            for t in range(len(states) - 1):
                if states[t + 1] < states[t]:
                    is_dag = False
                    break
            if is_dag:
                compliant_unif += 1
        null_unif_compliance[i] = compliant_unif / len(raw_inscriptions)

    def compute_stats(obs: float, null_arr: np.ndarray, alt: str = "greater") -> dict[str, Any]:
        mean_val = float(np.mean(null_arr))
        std_val = float(np.std(null_arr, ddof=1)) if len(null_arr) > 1 else 1e-6
        std_val = std_val if std_val > 0 else 1e-6
        z = (obs - mean_val) / std_val
        n = len(null_arr)
        if alt == "greater":
            p = float(np.sum(null_arr >= obs) + 1) / (n + 1)
        elif alt == "less":
            p = float(np.sum(null_arr <= obs) + 1) / (n + 1)
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
            "is_significant": bool(p < 0.001),
        }

    stat_freq = compute_stats(obs_compliance, null_freq_compliance, alt="greater")
    stat_unif = compute_stats(obs_compliance, null_unif_compliance, alt="greater")

    elapsed = time.time() - t_start

    return {
        "n_permutations": n_permutations,
        "elapsed_seconds": round(elapsed, 2),
        "spectral_analysis": {
            "parpola_eigenvalues": res_p.eigenvalues[:8],
            "parpola_eigengap_index": res_p.eigengap_index,
            "parpola_dag_feedforward_ratio": res_p.dag_feedforward_ratio,
            "mahadevan_eigenvalues": res_m.eigenvalues[:8],
            "mahadevan_eigengap_index": res_m.eigengap_index,
            "mahadevan_dag_feedforward_ratio": res_m.dag_feedforward_ratio,
            "classes": [
                {
                    "class_id": c.class_id,
                    "name": c.name,
                    "description": c.description,
                    "mean_position": c.mean_position,
                    "initial_ratio": c.initial_ratio,
                    "terminal_ratio": c.terminal_ratio,
                    "member_count": len(c.member_signs),
                    "top_signs": list(c.top_signs[:6]),
                }
                for c in res_p.classes
            ],
            "class_transition_matrix": res_p.class_transition_matrix,
        },
        "hmm_topology_sweep": {
            "best_bic_k": sweep_res.best_bic_k,
            "best_aic_k": sweep_res.best_aic_k,
            "min_bic": sweep_res.min_bic,
            "evaluations": [
                {
                    "k_states": ev.k_states,
                    "log_likelihood": ev.log_likelihood,
                    "bic": ev.bic,
                    "aic": ev.aic,
                    "held_out_log_loss": ev.held_out_log_loss,
                    "n_parameters": ev.n_parameters,
                }
                for ev in sweep_res.evaluations
            ],
        },
        "grammar_evaluation": {
            "dag_compliance_rate": grammar_rep.dag_compliance_rate,
            "raw_corpus_bits": grammar_rep.raw_corpus_bits,
            "unigram_corpus_bits": grammar_rep.unigram_corpus_bits,
            "grammar_mdl_bits": grammar_rep.grammar_mdl_bits,
            "compression_ratio_percent": grammar_rep.compression_ratio_percent,
            "state_descriptions": grammar_rep.state_descriptions,
        },
        "permutation_sieve": {
            "dag_compliance_vs_frequency_shuffle": stat_freq,
            "dag_compliance_vs_uniform_shuffle": stat_unif,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Indus Script Heavy Breakthrough Worker on Fedora PC")
    parser.add_argument("--data-dir", type=str, default="data/indus")
    parser.add_argument("--permutations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="data/derived/indus_grammar_breakthrough_results.json")
    args = parser.parse_args()

    data_p = Path(args.data_dir)
    out_p = Path(args.out)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Starting Indus Breakthrough Simulation: N={args.permutations} permutations, seed={args.seed}...")
    res = run_breakthrough_simulation(data_p, n_permutations=args.permutations, seed=args.seed)

    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)

    print(f"\n[✓] Breakthrough simulation complete in {res['elapsed_seconds']}s. Saved to {out_p}")
    print(f"    - Optimal Latent States: K = {res['hmm_topology_sweep']['best_bic_k']} (BIC = {res['hmm_topology_sweep']['min_bic']})")
    print(f"    - DAG Syntax Compliance: {res['grammar_evaluation']['dag_compliance_rate'] * 100:.2f}%")
    print(f"    - Compliance vs Frequency Shuffle: Z = {res['permutation_sieve']['dag_compliance_vs_frequency_shuffle']['z_score']}, p = {res['permutation_sieve']['dag_compliance_vs_frequency_shuffle']['p_value']}")
    print(f"    - Compliance vs Uniform Shuffle:   Z = {res['permutation_sieve']['dag_compliance_vs_uniform_shuffle']['z_score']}, p = {res['permutation_sieve']['dag_compliance_vs_uniform_shuffle']['p_value']}")
    print(f"    - MDL Compression Ratio:           {res['grammar_evaluation']['compression_ratio_percent']:.2f}%")


if __name__ == "__main__":
    main()
