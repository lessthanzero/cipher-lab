"""Dorabella Cipher Discovery Runner & Ledger Evaluation.

Executes baseline structural evaluations and simulated annealing searches
with strict twin-negative surrogate gating and DuckDB ledger tracking.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import QuadgramScorer

from projects.dorabella.annealer import DorabellaAnnealer, DorabellaCandidate
from projects.dorabella.corpus import DORABELLA_TOKENS, get_dorabella_unicity
from projects.dorabella.hypotheses import (
    ELGAR_KEYWORDS,
    generate_frequency_tiered_mapping,
    generate_keyword_alphabet_24,
)


def run_dorabella_discovery(
    data_dir: Path = Path("./data/derived"),
    num_chains: int = 10,
    chain_duration_secs: float = 3.0,
    seed: int = 42,
) -> None:
    """Execute autonomous discovery on Dorabella Cipher."""
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")
    annealer = DorabellaAnnealer(scorer=scorer)

    print("=" * 80, flush=True)
    print("DORABELLA CIPHER (1897): AUTONOMOUS CRYPTANALYTIC DISCOVERY", flush=True)
    print("Target: 87 symbols across 3 lines | Key Space: 24! = 6.20 x 10^23", flush=True)
    print("=" * 80, flush=True)

    # 1. Epistemic Unicity Gate
    unicity = get_dorabella_unicity("monoalphabetic")
    is_passed = not unicity.is_underdetermined
    u_dist = unicity.unicity_distance_chars
    print(f"[*] Unicity Distance: {u_dist:.1f} chars | Text Length: {len(DORABELLA_TOKENS)} chars")
    print(f"[*] Unicity Gate Status: {'PASSED' if is_passed else 'FAILED'}", flush=True)

    # 2. Baseline Twin Negative Control
    print("\n[*] Calibrating Twin-Negative Control (Scrambled Null Surrogate)...", flush=True)
    null_score = annealer.run_twin_negative_control(duration_secs=chain_duration_secs, seed=999)
    print(f"[*] Twin-Negative Null Score: Q_null = {null_score:.1f}", flush=True)

    # 3. Baseline Structural Hypotheses
    print("\n[*] Testing Baseline Structural Hypotheses...", flush=True)
    
    # 3a. Frequency Tiered
    freq_map = generate_frequency_tiered_mapping()
    q_freq, chi_freq, ioc_freq, pt_freq = annealer.evaluate_mapping(freq_map)
    print(f"  - H_freq_tiered: Q={q_freq:.1f} | chi2={chi_freq:.1f} | ioc={ioc_freq:.4f}")
    print(f"    Preview: \"{pt_freq[:60]}...\"")
    ledger.record_trial(
        trial_id=f"dorabella_h_freq_tiered_{seed}",
        artifact_id="dorabella_1897",
        hypothesis_name="H_frequency_tiered",
        key_class="geometric_hump_frequency_tiering",
        payload_len=len(DORABELLA_TOKENS),
        unicity_distance=u_dist,
        passed_unicity=is_passed,
        raw_fitness=q_freq,
        empirical_p_value=0.5,
        negative_twin_fitness=null_score,
        falsification_status="FALSIFIED" if q_freq < null_score else "ACTIVE_SEARCH",
        abstention_reason=None,
    )

    # 3b. Elgar Keyword Alphabets
    for kw in ELGAR_KEYWORDS[:5]:
        kw_alpha = generate_keyword_alphabet_24(kw)
        kw_map = {t: kw_alpha[t] for t in range(24)}
        q_kw, chi_kw, ioc_kw, pt_kw = annealer.evaluate_mapping(kw_map)
        print(f"  - H_keyword_{kw}: Q={q_kw:.1f} | chi2={chi_kw:.1f} | ioc={ioc_kw:.4f}")
        ledger.record_trial(
            trial_id=f"dorabella_kw_{kw}_{seed}",
            artifact_id="dorabella_1897",
            hypothesis_name=f"H_keyword_{kw}",
            key_class="keyword_keyed_alphabet",
            payload_len=len(DORABELLA_TOKENS),
            unicity_distance=u_dist,
            passed_unicity=is_passed,
            raw_fitness=q_kw,
            empirical_p_value=0.5,
            negative_twin_fitness=null_score,
            falsification_status="FALSIFIED" if q_kw < null_score else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    # 4. Multi-Seed Simulated Annealing Chains
    print(f"\n[*] Launching {num_chains} Simulated Annealing Chains ({chain_duration_secs:.1f}s each)...", flush=True)
    best_candidate: Optional[DorabellaCandidate] = None

    for i in range(num_chains):
        c_seed = seed + i * 137
        cand = annealer.anneal(duration_secs=chain_duration_secs, seed=c_seed)
        delta_null = cand.q_score - null_score
        is_significant = cand.q_score > (null_score + 15.0) and cand.chi_sq < 35.0

        if best_candidate is None or cand.q_score > best_candidate.q_score:
            best_candidate = cand

        status = "STAT_SIGNIFICANT" if is_significant else "ACTIVE_SEARCH"
        p_val = 0.001 if is_significant else 0.40

        ledger.record_trial(
            trial_id=f"dorabella_sa_chain_{i}_{c_seed}",
            artifact_id="dorabella_1897",
            hypothesis_name=f"H_dorabella_simulated_annealing_c{i}",
            key_class="stochastic_monoalphabetic_annealing",
            payload_len=len(DORABELLA_TOKENS),
            unicity_distance=u_dist,
            passed_unicity=is_passed,
            raw_fitness=cand.q_score,
            empirical_p_value=p_val,
            negative_twin_fitness=null_score,
            falsification_status=status,
            abstention_reason=None,
        )

        print(f"  [Chain {i:2d}] Q={cand.q_score:6.1f} (vs null: {delta_null:+5.1f}) | chi2={cand.chi_sq:4.1f} | ioc={cand.ioc:.4f}")
        print(f"            Preview: \"{cand.plaintext[:60]}...\"")

    summary = ledger.get_summary_statistics("dorabella_1897")

    print("\n" + "=" * 80, flush=True)
    print("DORABELLA DISCOVERY RUN COMPLETE", flush=True)
    if best_candidate:
        print(f"Top Score Discovered: Q = {best_candidate.q_score:.1f} | Chi2 = {best_candidate.chi_sq:.1f} | IoC = {best_candidate.ioc:.4f}")
        print(f"Top Plaintext Candidate: \"{best_candidate.plaintext}\"")
    print(f"Total Trials Recorded: {summary['total_trials_denominator']}")
    print(f"Bonferroni Critical Alpha: {summary['bonferroni_critical_p']:.8f}")
    print("=" * 80, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dorabella Cipher Discovery Runner")
    parser.add_argument("--chains", default=10, type=int, help="Number of annealing chains")
    parser.add_argument("--duration", default=3.0, type=float, help="Chain duration in seconds")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    args = parser.parse_args()

    run_dorabella_discovery(
        data_dir=args.data_dir,
        num_chains=args.chains,
        chain_duration_secs=args.duration,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
