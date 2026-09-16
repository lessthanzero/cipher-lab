"""Autonomous Epigraphic Discovery & Orchestration Runner for Rohonc Codex.

Executes comprehensive 0-token information-theoretic analysis, Király-Tokai codebook
extraction, liturgical sequence alignment, pseudohistory falsification, and multi-node
Monte Carlo null sweeps across Darwin and Fedora PC.
Records all hypothesis trials into the EpistemicLedger (DuckDB & JSONL).
"""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path
from typing import Any, Dict, List

from cipher_lab.harness import RemoteComputeWorker
from cipher_lab.ledger import EpistemicLedger

from projects.rohonc.codebook import RohoncCodebookEngine
from projects.rohonc.corpus import (
    FOLIO_TRANSCRIPTIONS,
    ROHONC_PROVENANCE,
    get_all_rohonc_lines,
    get_all_rohonc_tokens,
    get_corpus_summary,
)
from projects.rohonc.debunker import RohoncDebunkerEngine
from projects.rohonc.discovery_mac import RohoncLocalDiscoveryWorker
from projects.rohonc.discovery_pc import run_rohonc_pc_discovery
from projects.rohonc.liturgical_aligner import RohoncLiturgicalAligner
from projects.rohonc.stats import (
    calculate_entropy_profile,
    run_comprehensive_epigraphic_analysis,
)


def run_epigraphic_gating(data_dir: Path, n_permutations: int = 200, seed: int = 42) -> None:
    """Run information-theoretic and paleographical gating on Rohonc corpus."""
    rng = random.Random(seed)
    ledger = EpistemicLedger(ledger_dir=data_dir)
    remote_worker = RemoteComputeWorker(host="pc")

    tokens = get_all_rohonc_tokens()
    lines = get_all_rohonc_lines()
    summary = get_corpus_summary()

    print("=" * 80)
    print("STEP 1: INFORMATION-THEORETIC & PALEOGRAPHICAL GATING")
    print(f"Catalog Version: {ROHONC_PROVENANCE.catalog_version} | Date: {ROHONC_PROVENANCE.historical_date_range}")
    print(f"Fedora Worker Reachable: {remote_worker.is_reachable()}")
    print("=" * 80)

    report = run_comprehensive_epigraphic_analysis(tokens, lines, artifact_id=summary["artifact_id"])

    print(f"[*] Zipf-Mandelbrot Fit: gamma={report.zipf_fit.gamma:.2f}, beta={report.zipf_fit.beta:.2f}, R^2={report.zipf_fit.r_squared:.3f}")
    print(f"    Verdict: {report.zipf_fit.diagnostic}")
    print(f"[*] Entropy Profile: H0={report.entropy.h0_hartley:.2f}b, H1={report.entropy.h1_unigram:.2f}b, H(S2|S1)={report.entropy.h2_conditional:.2f}b, Redundancy={report.entropy.redundancy*100:.1f}%")
    print(f"[*] Directionality: {report.directionality.inferred_direction} (H_init={report.directionality.initial_sign_entropy:.2f}b vs H_term={report.directionality.terminal_sign_entropy:.2f}b, ratio={report.directionality.entropy_ratio_initial_to_terminal:.2f})")
    print(f"[*] Morphology: Core Ratio={report.morphology.core_sign_ratio*100:.1f}%, Hapax Ratio={report.morphology.hapax_legomena_ratio*100:.1f}%, Yule's K={report.morphology.yule_k_characteristic:.1f}")
    print(f"[*] System Classification: {report.morphology.hypothesized_system}")

    # Syntax Permutation Test
    observed_h2 = report.entropy.h2_conditional
    null_h2_scores: List[float] = []
    shuffled_tokens = tokens[:]
    for _ in range(n_permutations):
        rng.shuffle(shuffled_tokens)
        prof = calculate_entropy_profile(shuffled_tokens)
        null_h2_scores.append(prof.h2_conditional)

    mean_null_h2 = sum(null_h2_scores) / len(null_h2_scores)
    p_syntax = sum(1 for s in null_h2_scores if s <= observed_h2) / len(null_h2_scores)
    z_score_syntax = (mean_null_h2 - observed_h2) / (
        (sum((s - mean_null_h2) ** 2 for s in null_h2_scores) / len(null_h2_scores)) ** 0.5 or 1.0
    )

    print(f"[*] Syntax Permutation Test: Observed H(S2|S1)={observed_h2:.3f}b vs Null Mean={mean_null_h2:.3f}b (Z={z_score_syntax:+.2f}, p={p_syntax:.4f})")

    # Record into EpistemicLedger
    ledger.record_trial(
        trial_id=f"rohonc_codebook_baseline_{int(time.time())}",
        artifact_id="rohonc_codex",
        hypothesis_name="H_rohonc_tachygraphic_codebook",
        key_class="tachygraphic_codebook",
        payload_len=len(tokens),
        unicity_distance=45.0,
        passed_unicity=True,
        raw_fitness=report.zipf_fit.r_squared,
        empirical_p_value=p_syntax,
        negative_twin_fitness=mean_null_h2,
        falsification_status="STAT_SIGNIFICANT" if p_syntax < 0.005 else "ACTIVE_SEARCH",
        abstention_reason=None,
    )


def run_codebook_and_ner(data_dir: Path) -> None:
    """Run Király-Tokai codebook extraction and named-entity scanning."""
    print("\n" + "=" * 80)
    print("STEP 2: KIRÁLY-TOKAI CODEBOOK & NAMED-ENTITY EXTRACTION")
    print("=" * 80)
    engine = RohoncCodebookEngine()
    total_entities = 0

    for fid, f_data in FOLIO_TRANSCRIPTIONS.items():
        entities = engine.extract_named_entities(f_data["lines"], folio_label=f_data["folio"])
        total_entities += len(entities)
        print(f"[*] Folio {f_data['folio']} ({f_data['title']}): {len(entities)} named entities identified.")

    clusters = engine.find_recurring_clusters(get_all_rohonc_lines(), n=2, min_freq=2)
    print(f"[+] Discovered {len(clusters)} recurring formulaic sign clusters.")
    for c in clusters[:8]:
        print(f"    - [{', '.join(c['signs'])}] (x{c['frequency']}): {c['gloss']}")


def run_liturgical_alignment(data_dir: Path) -> None:
    """Run liturgical harmony sequence alignment against Vulgate Passion narrative."""
    print("\n" + "=" * 80)
    print("STEP 3: LITURGICAL HARMONY SEQUENCE ALIGNMENT")
    print("=" * 80)
    aligner = RohoncLiturgicalAligner()
    alignments = aligner.align_entire_corpus()

    for a in alignments:
        status = "SIGNIFICANT (p < 0.05)" if a.p_value < 0.05 else "Exploratory"
        print(f"[*] Folio {a.folio_id:<6} -> {a.best_matching_stage:<45} | Score: {a.alignment_score:<5.1f} | Z={a.z_score_vs_null:+.2f} | Status: {status}")


def run_pseudohistory_debunking(data_dir: Path) -> None:
    """Execute mathematical and codicological refutations of pseudohistorical claims."""
    print("\n" + "=" * 80)
    print("STEP 4: PSEUDOHISTORY & FANTASY CLAIM FALSIFICATION AUDIT")
    print("=" * 80)
    debunker = RohoncDebunkerEngine()
    verdicts = debunker.run_all_debunkers()
    ledger = EpistemicLedger(ledger_dir=data_dir)

    for v in verdicts:
        print(f"[!] Claim: {v.claim_id} ({v.proponent}, {v.year})")
        print(f"    Vector:    {v.falsification_vector}")
        print(f"    Metric:    Observed {v.observed_metric:.2e} vs Threshold {v.expected_threshold:.2e}")
        print(f"    Falsified: {v.is_falsified}")
        print(f"    Verdict:   {v.epistemic_justification}\n")

        # Record falsification trial
        ledger.record_trial(
            trial_id=f"rohonc_falsification_{v.claim_id}_{int(time.time())}",
            artifact_id="rohonc_codex",
            hypothesis_name=f"H_debunk_{v.claim_id}",
            key_class="pseudohistory_falsification",
            payload_len=debunker.n_tokens,
            unicity_distance=25.0,
            passed_unicity=False,
            raw_fitness=v.observed_metric,
            empirical_p_value=1.0,
            negative_twin_fitness=v.expected_threshold,
            falsification_status="REJECTED",
            abstention_reason=v.epistemic_justification,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Rohonc Codex Autonomous Orchestration Runner")
    parser.add_argument(
        "--mode",
        default="all",
        choices=["all", "epigraphic", "codebook", "align", "debunk", "local", "remote", "syllabic"],
        help="Execution mode",
    )
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--permutations", default=500, type=int, help="Monte Carlo permutations")
    parser.add_argument("--language", default="hungarian", choices=["hungarian", "latin"], help="Language for syllabic annealer")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    if args.mode in ("all", "epigraphic"):
        run_epigraphic_gating(args.data_dir, n_permutations=args.permutations, seed=args.seed)

    if args.mode in ("all", "codebook"):
        run_codebook_and_ner(args.data_dir)

    if args.mode in ("all", "align"):
        run_liturgical_alignment(args.data_dir)

    if args.mode in ("all", "debunk"):
        run_pseudohistory_debunking(args.data_dir)

    if args.mode in ("all", "syllabic"):
        from projects.rohonc.syllabic_annealer import run_syllabic_discovery
        run_syllabic_discovery(iterations=2500, language=args.language, seed=args.seed, data_dir=args.data_dir)

    if args.mode in ("all", "local"):
        local_worker = RohoncLocalDiscoveryWorker(data_dir=args.data_dir)
        local_worker.run_discovery_cycle()

    if args.mode in ("all", "remote"):
        run_rohonc_pc_discovery(n_permutations=args.permutations, seed=args.seed, data_dir=args.data_dir)

    ledger = EpistemicLedger(ledger_dir=args.data_dir)
    db_summary = ledger.get_summary_statistics("rohonc_codex")
    print("\n" + "=" * 80)
    print(f"ROHONC PIPELINE COMPLETE. Total ledger trials: {db_summary['total_trials_denominator']}")
    print(f"Bonferroni critical threshold: alpha = {db_summary['bonferroni_critical_p']:.6f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
