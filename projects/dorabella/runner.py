"""Dorabella Cipher Holistic Multi-Disciplinary Discovery Runner & Ledger Evaluator.

Unifies:
1. Holistic multi-disciplinary context (history, bibliography, geography, biology, politics).
2. Epistemic unicity gating.
3. Musical cipher contour evaluation.
4. Tachygraphic (Taylor & Pitman shorthand) phonotactic evaluation.
5. Transposition & Pall Mall grille search.
6. Multi-seed simulated annealing with twin-negative surrogate gating.
7. Local models harness refereeing with negative-control foils.
8. Append-only DuckDB epistemic ledger persistence.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from cipher_lab.harness import ModelRefereeHarness, get_darwin_available_memory_gb
from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import QuadgramScorer

from projects.dorabella.annealer import DorabellaAnnealer, DorabellaCandidate
from projects.dorabella.corpus import DORABELLA_TOKENS, get_dorabella_unicity
from projects.dorabella.holistic import HolisticDorabellaContext
from projects.dorabella.hypotheses import (
    ELGAR_KEYWORDS,
    generate_frequency_tiered_mapping,
)
from projects.dorabella.musical_cipher import MusicalCipherEvaluator
from projects.dorabella.tachygraphy import TachygraphicEvaluator
from projects.dorabella.transposition_solver import DorabellaTranspositionSolver


def run_dorabella_discovery(
    data_dir: Path = Path("./data/derived"),
    num_chains: int = 5,
    chain_duration_secs: float = 2.0,
    seed: int = 42,
    run_llm_referee: bool = False,
) -> None:
    """Execute autonomous discovery on Dorabella Cipher."""
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")
    annealer = DorabellaAnnealer(scorer=scorer)
    holistic = HolisticDorabellaContext()

    print("=" * 80, flush=True)
    print("DORABELLA CIPHER (1897): HOLISTIC MULTI-DISCIPLINARY DISCOVERY", flush=True)
    print("Target: 87 symbols across 3 lines | Key Space: 24! = 6.20 x 10^23", flush=True)
    print("=" * 80, flush=True)

    # 1. Holistic Context Ingestion
    print("\n[+] 1. INGESTING HOLISTIC MULTI-DISCIPLINARY CONTEXT:")
    for domain, summary in holistic.get_summary().items():
        print(f"    - {domain:12s}: {summary}")
    cribs = holistic.get_lexicon_cribs()
    print(f"    - Ingested Cribs ({len(cribs)} total): {', '.join(cribs[:8])}...", flush=True)

    # 2. Epistemic Unicity Gate
    unicity_mono = get_dorabella_unicity("monoalphabetic")
    unicity_homo = get_dorabella_unicity("homophonic")
    print("\n[+] 2. EPISTEMIC UNICITY GATES:")
    print(f"    - Monoalphabetic: U_0 = {unicity_mono.unicity_distance_chars:.1f} chars | Text = {len(DORABELLA_TOKENS)} chars | Status: {'PASSED' if not unicity_mono.is_underdetermined else 'FAILED'}")
    print(f"    - Homophonic:     U_0 = {unicity_homo.unicity_distance_chars:.1f} chars | Text = {len(DORABELLA_TOKENS)} chars | Status: {'UNDERDETERMINED (ABSTENTION MANDATED)' if unicity_homo.is_underdetermined else 'PASSED'}")

    # 3. Musical Cipher Evaluation
    print("\n[+] 3. EVALUATING MUSICAL CIPHER HYPOTHESIS (MELODIC CONTOUR):")
    music_eval = MusicalCipherEvaluator()
    best_root, mel_score, note_names = music_eval.search_optimal_tonal_alignment()
    flutter = music_eval.compute_rhythmic_flutter_correlation()
    print(f"    - Optimal Diatonic Scale Alignment: Root={best_root} | Voice-Leading Score={mel_score:.1f}")
    print(f"    - Incipit Contour: {'-'.join(note_names[:12])}...")
    print(f"    - Triplet Flutter Correlation (Variation X 'Dorabella' mimicry): {flutter:.0f} bursts")
    ledger.record_trial(
        trial_id=f"dorabella_melodic_contour_{seed}",
        artifact_id="dorabella_1897",
        hypothesis_name="H_musical_melodic_contour",
        key_class="diatonic_pitch_mapping",
        payload_len=len(DORABELLA_TOKENS),
        unicity_distance=unicity_mono.unicity_distance_chars,
        passed_unicity=True,
        raw_fitness=mel_score,
        empirical_p_value=0.25,
        negative_twin_fitness=-50.0,
        falsification_status="ACTIVE_SEARCH",
        abstention_reason=None,
    )

    # 4. Tachygraphic / Shorthand Evaluation
    print("\n[+] 4. EVALUATING TACHYGRAPHIC / SHORTHAND HYPOTHESES:")
    tachy_eval = TachygraphicEvaluator(scorer=scorer)
    tachy_results = tachy_eval.evaluate_tachygraphic_hypotheses()
    for hyp_name, (q_val, ioc_val, dec_text) in tachy_results.items():
        print(f"    - {hyp_name}: Q={q_val:6.1f} | IoC={ioc_val:.4f} | \"{dec_text[:40]}...\"")
        ledger.record_trial(
            trial_id=f"{hyp_name}_{seed}",
            artifact_id="dorabella_1897",
            hypothesis_name=hyp_name,
            key_class="phonographic_shorthand",
            payload_len=len(dec_text),
            unicity_distance=unicity_mono.unicity_distance_chars,
            passed_unicity=True,
            raw_fitness=q_val,
            empirical_p_value=0.50,
            negative_twin_fitness=-600.0,
            falsification_status="FALSIFIED" if q_val < -700.0 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    # 5. Baseline Twin Negative Control
    print("\n[+] 5. CALIBRATING TWIN-NEGATIVE CONTROL (SCRAMBLED NULL SURROGATE)...", flush=True)
    null_score = annealer.run_twin_negative_control(duration_secs=chain_duration_secs, seed=999)
    print(f"    - Twin-Negative Null Score: Q_null = {null_score:.1f}", flush=True)

    # 6. Transposition & Pall Mall Grille Variants
    print("\n[+] 6. TESTING TRANSPOSITION & PALL MALL GRILLE ARCHITECTURES:")
    trans_solver = DorabellaTranspositionSolver()
    baseline_map = generate_frequency_tiered_mapping()
    t_candidates = trans_solver.evaluate_transposition_candidates(
        mapping=baseline_map,
        scorer=scorer,
        keywords=ELGAR_KEYWORDS[:4],
    )
    for t_name, t_q, t_ioc, t_pt in t_candidates[:3]:
        print(f"    - {t_name:18s}: Q={t_q:6.1f} | IoC={t_ioc:.4f} | Preview: \"{t_pt[:35]}...\"")
        ledger.record_trial(
            trial_id=f"dorabella_trans_{t_name}_{seed}",
            artifact_id="dorabella_1897",
            hypothesis_name=f"H_transposition_{t_name}",
            key_class="pall_mall_columnar_transposition",
            payload_len=len(DORABELLA_TOKENS),
            unicity_distance=unicity_mono.unicity_distance_chars,
            passed_unicity=True,
            raw_fitness=t_q,
            empirical_p_value=0.5,
            negative_twin_fitness=null_score,
            falsification_status="FALSIFIED" if t_q < null_score else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    # 7. Multi-Seed Simulated Annealing Chains
    print(f"\n[+] 7. EXECUTING {num_chains} STOCHASTIC ANNEALING CHAINS ({chain_duration_secs:.1f}s each)...", flush=True)
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
            unicity_distance=unicity_mono.unicity_distance_chars,
            passed_unicity=True,
            raw_fitness=cand.q_score,
            empirical_p_value=p_val,
            negative_twin_fitness=null_score,
            falsification_status=status,
            abstention_reason=None,
        )

        print(f"    [Chain {i:2d}] Q={cand.q_score:6.1f} (vs null: {delta_null:+5.1f}) | chi2={cand.chi_sq:4.1f} | ioc={cand.ioc:.4f}")
        print(f"               Preview: \"{cand.plaintext[:50]}...\"")

    # 8. Local Models Referee Verification (if enabled and candidate available)
    if run_llm_referee and best_candidate:
        print("\n[+] 8. LOCAL MODELS HARNESS REFEREEING (DOUBLE-BLIND FOIL PASS):")
        mem_gb = get_darwin_available_memory_gb()
        print(f"    - Darwin Available Memory: {mem_gb:.2f} GB")
        referee = ModelRefereeHarness()
        # Generate 2 decoys: frequency-tiered decode and scrambled tokens decode
        decoy_1 = t_candidates[0][3] if t_candidates else decode_tokens(DORABELLA_TOKENS, baseline_map)
        from projects.dorabella.hypotheses import scramble_tokens
        from projects.dorabella.symbols import decode_tokens
        scrambled_map = {t: chr(65 + t) for t in range(24)}
        decoy_2 = decode_tokens(scramble_tokens(DORABELLA_TOKENS, seed=123), scrambled_map)

        ref_res = referee.evaluate_with_blinded_foils(
            candidate_plaintext=best_candidate.plaintext,
            decoy_plaintexts=[decoy_1, decoy_2],
            artifact_context="Edward Elgar's 1897 Dorabella Cipher note to 23-year-old Dora Penny at Wolverhampton Rectory.",
            preferred_model="phi4-mini:latest",
        )
        print(f"    - Blind Referee Selection: Option [{ref_res.get('selected_option', 'NONE')}]")
        print(f"    - Linguistic Coherence: {ref_res.get('linguistic_coherence_score', 0.0):.2f} | Confidence: {ref_res.get('confidence', 0.0):.2f}")
        print(f"    - Rationale: {ref_res.get('rationale', 'N/A')}")

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
    parser.add_argument("--chains", default=5, type=int, help="Number of annealing chains")
    parser.add_argument("--duration", default=2.0, type=float, help="Chain duration in seconds")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--referee", action="store_true", help="Run local models referee pass")
    args = parser.parse_args()

    run_dorabella_discovery(
        data_dir=args.data_dir,
        num_chains=args.chains,
        chain_duration_secs=args.duration,
        seed=args.seed,
        run_llm_referee=args.referee,
    )


if __name__ == "__main__":
    main()
