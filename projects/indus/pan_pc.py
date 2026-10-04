"""Heavy-throughput Monte Carlo Pan-Indus Worker for Fedora PC.

Executes massive-scale hypothesis testing across all 3,219 inscriptions (12,910 tokens):
1. Cross-Site Permutation Sieve: Tests Mohenjo-Daro vs Harappa invariance under site-label shuffles.
2. Cross-Medium Permutation Sieve: Tests Seals vs Tablets vs Tags invariance under genre shuffles.
3. Motif-Syntax Coupling Permutation Sieve: Tests Animal Motif vs Initial Class independence.
4. Directionality Permutation Sieve: Evaluates Right-to-Left vs Left-to-Right DAG asymmetry.
5. Pan-Corpus HMM Model Selection: Full K=2..8 sweep and MDL compression calculation.
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

from projects.indus.hmm_induction import DiscreteHMM, HMMTopologySweeper
from projects.indus.pan_analytics import PanIndusAnalyzer
from projects.indus.pan_corpus import PanIndusCorpus


def run_pan_indus_breakthrough_pc(
    data_dir: Path,
    n_permutations: int = 5000,
    seed: int = 42,
) -> dict[str, Any]:
    t_start = time.time()
    csv_path = data_dir / "analytic_lines.csv"
    corpus = PanIndusCorpus(csv_path=csv_path)
    analyzer = PanIndusAnalyzer(corpus=corpus, target_catalog="parpola", n_classes=5, seed=seed)

    print(f"[*] Pan-Indus Corpus Loaded: {len(corpus.inscriptions)} inscriptions, {len(corpus.get_sequences())} sequences.")

    # ---------------------------------------------------------
    # Step 1: Cross-Site Invariance Evaluation (Mohenjo-Daro vs Harappa)
    # ---------------------------------------------------------
    print("[*] Step 1: Evaluating Cross-Site Invariance between Mohenjo-Daro and Harappa...")
    site_eval = analyzer.evaluate_cross_site_invariance("Mohenjo-daro", "Harappa")
    obs_d_skl = site_eval.kl_divergence_symmetric
    print(f"    - Observed Symmetric KL Divergence: {obs_d_skl:.4f} bits")
    print(f"    - Cross-Perplexity MD->H: {site_eval.perplexity_a_to_b:.2f}, H->MD: {site_eval.perplexity_b_to_a:.2f}")

    # Permutation test on site labels
    md_ins = corpus.filter_by_site("Mohenjo-daro")
    h_ins = corpus.filter_by_site("Harappa")
    combined_site_ins = md_ins + h_ins
    n_md = len(md_ins)
    combined_seqs = [analyzer.get_class_sequence(ins.signs_parpola) for ins in combined_site_ins if len(ins.signs_parpola) >= 2]

    rng = random.Random(seed)
    null_d_skl = np.empty(n_permutations, dtype=np.float64)

    def fast_trans(seqs_sub: list[list[int]]) -> np.ndarray:
        c = np.ones((5, 5), dtype=np.float64)
        for q in seqs_sub:
            for t in range(len(q) - 1):
                c[q[t], q[t + 1]] += 1.0
        return c / c.sum(axis=1, keepdims=True)

    def sym_kl(p: np.ndarray, q: np.ndarray) -> float:
        val = 0.5 * (np.sum(p * np.log2(p / q)) + np.sum(q * np.log2(q / p)))
        return float(val) / 5.0

    idx_pool = list(range(len(combined_seqs)))
    split_pt = int(n_md / len(combined_site_ins) * len(combined_seqs))

    for i in range(n_permutations):
        rng.shuffle(idx_pool)
        sub_a = [combined_seqs[j] for j in idx_pool[:split_pt]]
        sub_b = [combined_seqs[j] for j in idx_pool[split_pt:]]
        T_a = fast_trans(sub_a)
        T_b = fast_trans(sub_b)
        null_d_skl[i] = sym_kl(T_a, T_b)

    null_skl_mean = float(np.mean(null_d_skl))
    null_skl_std = float(np.std(null_d_skl, ddof=1)) if len(null_d_skl) > 1 else 1e-6
    z_site = (obs_d_skl - null_skl_mean) / max(null_skl_std, 1e-6)
    p_site = float(np.sum(null_d_skl <= obs_d_skl) + 1) / (n_permutations + 1)

    print(f"    - Site Permutation Sieve: Z = {z_site:.2f}, p = {p_site:.6f} (Observed={obs_d_skl:.4f} vs NullMean={null_skl_mean:.4f})")

    # ---------------------------------------------------------
    # Step 2: Cross-Medium Invariance Evaluation (Seals vs Tablets vs Tags)
    # ---------------------------------------------------------
    print("[*] Step 2: Evaluating Cross-Medium Invariance across Seals, Tablets, and Tags...")
    medium_evals = analyzer.evaluate_cross_medium_invariance()
    for cm in medium_evals:
        print(f"    - {cm.medium.upper()}: N={cm.n_inscriptions}, DAG Compliance = {cm.dag_compliance_rate*100:.2f}%, Entropy Rate = {cm.entropy_rate:.2f} bits")

    # ---------------------------------------------------------
    # Step 3: Motif-Syntax Coupling Evaluation
    # ---------------------------------------------------------
    print("[*] Step 3: Evaluating Iconographic Animal Motif vs Syntactic Class Coupling...")
    motif_eval = analyzer.evaluate_motif_coupling()
    obs_mi = motif_eval.mutual_information_bits
    obs_chi2 = motif_eval.chi2_stat
    print(f"    - N={motif_eval.n_labeled_inscriptions}, Motifs={motif_eval.n_motifs}")
    print(f"    - Observed Mutual Information: {obs_mi:.4f} bits, Chi2: {obs_chi2:.2f} (p={motif_eval.p_value:.6f})")

    # Permutation test on motif labels
    paired_data: list[tuple[str, int]] = []
    motif_map = {
        "Bull1:W": "Bull", "Bull1": "Bull", "Bull1:J": "Bull", "Bull1:S": "Bull", "Bull1:I": "Bull",
        "Bult": "Bull", "Gaur": "Gaur", "Unicorn": "Unicorn", "Elephant": "Elephant", "Tiger": "Tiger", "Rhinoceros": "Rhino",
    }
    for ins in corpus.inscriptions:
        sym = ins.symbol.strip()
        motif = motif_map.get(sym, sym if sym and sym not in ("-", ":", "SAN", "Othr") else None)
        if motif and len(ins.signs_parpola) >= 1:
            c = analyzer.sign_to_class.get(ins.signs_parpola[0], 1)
            paired_data.append((motif, c))

    motif_counts = collections.Counter(m for m, _ in paired_data)
    top_m = [m for m, c in motif_counts.most_common(5) if c >= 30]
    sub_paired = [(m, c) for m, c in paired_data if m in top_m]
    m_labels = [m for m, _ in sub_paired]
    c_labels = [c for _, c in sub_paired]
    N_sub = len(sub_paired)

    m_idx = {m: i for i, m in enumerate(top_m)}
    K_m = len(top_m)

    null_mi = np.empty(n_permutations, dtype=np.float64)
    shuffled_c = list(c_labels)

    for i in range(n_permutations):
        rng.shuffle(shuffled_c)
        cont = np.zeros((K_m, 5), dtype=np.float64)
        for j in range(N_sub):
            cont[m_idx[m_labels[j]], shuffled_c[j]] += 1.0
        p_xy = cont / N_sub
        p_x = p_xy.sum(axis=1, keepdims=True)
        p_y = p_xy.sum(axis=0, keepdims=True)
        mi_val = 0.0
        for r in range(K_m):
            for col in range(5):
                if p_xy[r, col] > 0 and p_x[r, 0] > 0 and p_y[0, col] > 0:
                    mi_val += p_xy[r, col] * math.log2(p_xy[r, col] / (p_x[r, 0] * p_y[0, col]))
        null_mi[i] = mi_val

    null_mi_mean = float(np.mean(null_mi))
    null_mi_std = float(np.std(null_mi, ddof=1)) if len(null_mi) > 1 else 1e-6
    z_motif = (obs_mi - null_mi_mean) / max(null_mi_std, 1e-6)
    p_motif = float(np.sum(null_mi >= obs_mi) + 1) / (n_permutations + 1)
    print(f"    - Motif Coupling Sieve: Z = {z_motif:.2f}, p = {p_motif:.6f} (Observed={obs_mi:.4f} vs NullMean={null_mi_mean:.4f})")

    # ---------------------------------------------------------
    # Step 4: Directionality Asymmetry Proof (R/L vs Retrograde L/R)
    # ---------------------------------------------------------
    print("[*] Step 4: Evaluating Right-to-Left Directionality Asymmetry...")
    dir_eval = analyzer.evaluate_directionality_asymmetry()
    print(f"    - Canonical R/L Compliance: {dir_eval.canonical_compliance_rate*100:.2f}%")
    print(f"    - Retrograde L/R Compliance: {dir_eval.retrograde_compliance_rate*100:.2f}%")
    print(f"    - Asymmetry Ratio: {dir_eval.asymmetry_ratio:.2f}x (Z = +{dir_eval.z_score:.2f}, p = {dir_eval.p_value:.8f})")

    # ---------------------------------------------------------
    # Step 5: Global Pan-Indus Model Selection & MDL Compression
    # ---------------------------------------------------------
    print("[*] Step 5: Sweeping HMM Topology across K=2..8 States for Full Corpus (N=3,219)...")
    all_class_seqs = [analyzer.get_class_sequence(ins.signs_parpola) for ins in corpus.inscriptions if len(ins.signs_parpola) >= 1]
    all_str_seqs = [[str(c) for c in q] for q in all_class_seqs]

    sweeper = HMMTopologySweeper(all_str_seqs)
    sweep_res = sweeper.sweep(k_values=[2, 3, 4, 5, 6, 7, 8], n_restarts=8, seed=seed)
    print(f"    - Best BIC K: {sweep_res.best_bic_k} (BIC = {sweep_res.min_bic:.2f})")
    print(f"    - Best AIC K: {sweep_res.best_aic_k}")

    # Compute global MDL compression on 12,910 tokens
    total_tokens = sum(len(q) for q in all_class_seqs)
    raw_bits = total_tokens * math.log2(465)  # 465 vocabulary types
    unigram_counts = collections.Counter(c for q in all_class_seqs for c in q)
    h0 = -sum((cnt / total_tokens) * math.log2(cnt / total_tokens) for cnt in unigram_counts.values())
    unigram_bits = total_tokens * h0

    best_k = sweep_res.best_bic_k
    k_params = best_k * (best_k - 1) + best_k * (5 - 1)
    model_bits = k_params * math.log2(total_tokens)
    best_eval = next(ev for ev in sweep_res.evaluations if ev.k_states == best_k)
    data_bits = -best_eval.log_likelihood / math.log(2.0)
    pan_mdl_bits = model_bits + data_bits
    pan_compression = (1.0 - (pan_mdl_bits / raw_bits)) * 100.0

    print(f"    - Pan-Indus MDL Compression: {pan_compression:.2f}% ({raw_bits:.1f} bits -> {pan_mdl_bits:.1f} bits)")

    elapsed = time.time() - t_start

    return {
        "n_inscriptions": len(corpus.inscriptions),
        "total_tokens": total_tokens,
        "n_permutations": n_permutations,
        "elapsed_seconds": round(elapsed, 2),
        "cross_site_invariance": {
            "site_a": site_eval.site_a,
            "site_b": site_eval.site_b,
            "kl_divergence_symmetric": site_eval.kl_divergence_symmetric,
            "null_skl_mean": round(null_skl_mean, 4),
            "z_score": round(z_site, 2),
            "p_value": round(p_site, 6),
            "perplexity_md_to_h": site_eval.perplexity_a_to_b,
            "perplexity_h_to_md": site_eval.perplexity_b_to_a,
            "dag_compliance_md": site_eval.dag_compliance_a,
            "dag_compliance_h": site_eval.dag_compliance_b,
            "is_statistically_invariant": site_eval.is_statistically_invariant,
        },
        "cross_medium_invariance": [
            {
                "medium": cm.medium,
                "n_inscriptions": cm.n_inscriptions,
                "mean_length": cm.mean_length,
                "dag_compliance_rate": cm.dag_compliance_rate,
                "entropy_rate": cm.entropy_rate,
                "is_feedforward_dag": cm.is_feedforward_dag,
            }
            for cm in medium_evals
        ],
        "motif_syntax_coupling": {
            "n_labeled_inscriptions": motif_eval.n_labeled_inscriptions,
            "n_motifs": motif_eval.n_motifs,
            "observed_mi_bits": motif_eval.mutual_information_bits,
            "null_mi_mean": round(null_mi_mean, 4),
            "z_score": round(z_motif, 2),
            "p_value": round(p_motif, 6),
            "chi2_stat": motif_eval.chi2_stat,
            "chi2_p_value": motif_eval.p_value,
            "is_coupled": motif_eval.is_coupled,
            "top_associations": motif_eval.top_associations,
        },
        "directionality_proof": {
            "canonical_direction": dir_eval.canonical_direction,
            "canonical_compliance_rate": dir_eval.canonical_compliance_rate,
            "retrograde_compliance_rate": dir_eval.retrograde_compliance_rate,
            "asymmetry_ratio": dir_eval.asymmetry_ratio,
            "z_score": dir_eval.z_score,
            "p_value": dir_eval.p_value,
            "is_unidirectional": dir_eval.is_unidirectional,
        },
        "pan_hmm_model_selection": {
            "best_bic_k": sweep_res.best_bic_k,
            "best_aic_k": sweep_res.best_aic_k,
            "min_bic": sweep_res.min_bic,
            "raw_bits": round(raw_bits, 1),
            "unigram_bits": round(unigram_bits, 1),
            "pan_mdl_bits": round(pan_mdl_bits, 1),
            "compression_ratio_percent": round(pan_compression, 2),
            "evaluations": [
                {
                    "k_states": ev.k_states,
                    "log_likelihood": ev.log_likelihood,
                    "bic": ev.bic,
                    "aic": ev.aic,
                    "n_parameters": ev.n_parameters,
                }
                for ev in sweep_res.evaluations
            ],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Heavy Pan-Indus Batch Worker for Fedora PC.")
    parser.add_argument("--data-dir", type=str, default="data/indus", help="Path to indus data directory")
    parser.add_argument("--permutations", type=int, default=5000, help="Number of Monte Carlo permutations")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--out", type=str, default="data/derived/indus_pan_breakthrough_results.json", help="Output JSON path")
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = run_pan_indus_breakthrough_pc(data_dir=data_dir, n_permutations=args.permutations, seed=args.seed)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n[✓] Pan-Indus Batch complete in {results['elapsed_seconds']}s. Results saved to {out_path}")


if __name__ == "__main__":
    main()
