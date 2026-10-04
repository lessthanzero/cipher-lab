"""Unit and integration test suite for the Pan-Indus (3,219 inscriptions) research track."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from cipher_lab.ledger import EpistemicLedger
from projects.indus.concordance import IndusConcordance
from projects.indus.pan_analytics import PanIndusAnalyzer
from projects.indus.pan_corpus import PanIndusCorpus


@pytest.fixture(scope="module")
def pan_corpus() -> PanIndusCorpus:
    return PanIndusCorpus()


@pytest.fixture(scope="module")
def analyzer(pan_corpus: PanIndusCorpus) -> PanIndusAnalyzer:
    return PanIndusAnalyzer(corpus=pan_corpus, target_catalog="parpola", n_classes=5, seed=42)


def test_pan_corpus_invariants(pan_corpus: PanIndusCorpus) -> None:
    """Verify macroscopic invariants across the full 3,219-inscription corpus."""
    summary = pan_corpus.get_summary()
    assert summary["total_inscriptions"] == 3219
    assert summary["total_tokens"] == 12910
    assert 450 <= summary["signary_types"] <= 480
    assert 3.9 <= summary["mean_length"] <= 4.1
    assert summary["max_length"] == 13

    # Site distribution
    sites = summary["sites"]
    assert sites["Harappa"] == 1486
    assert sites["Mohenjo-daro"] == 1318
    assert sites["Lothal"] == 87
    assert sites["Dholavira"] == 78
    assert sites["Kalibangan"] == 59
    assert sites["Chanhu-daro"] == 57

    # Medium distribution
    types = summary["broad_types"]
    assert types["seal"] == 1568
    assert types["tablet"] == 1457
    assert types["pottery"] == 76
    assert types["tag"] == 70

    # Directionality
    dirs = summary["directions"]
    assert dirs["R/L"] == 3054
    assert dirs["L/R"] == 165


def test_concordance_wells_bidirectional_mapping() -> None:
    """Verify Wells ICIT concordance normalization and anchor mappings."""
    conc = IndusConcordance()

    # Foundational Classic Jar anchor
    assert conc.wells_to_parpola("W740") == "P324"
    assert conc.wells_to_parpola("740") == "P324"
    assert conc.wells_to_mahadevan("W740") == "M342"
    assert conc.wells_to_mahadevan("740") == "M342"

    # Sequence normalization
    raw_wells = ["235", "705", "033", "740"]
    parpola_norm = conc.normalize_sequence(raw_wells, target_catalog="parpola")
    assert parpola_norm == ["P060", "P316", "P147", "P324"]

    mahadevan_norm = conc.normalize_sequence(raw_wells, target_catalog="mahadevan")
    assert mahadevan_norm == ["M065", "M336", "M089", "M342"]


def test_cross_site_invariance(analyzer: PanIndusAnalyzer) -> None:
    """PAN-H1: Verify syntactic invariance between Mohenjo-Daro and Harappa."""
    res = analyzer.evaluate_cross_site_invariance("Mohenjo-daro", "Harappa")

    assert res.n_inscriptions_a == 1318
    assert res.n_inscriptions_b == 1486
    # Symmetric KL divergence must be minimal (< 0.15 bits)
    assert res.kl_divergence_symmetric < 0.15
    # Both metropolitan sites must exhibit > 70% DAG compliance
    assert res.dag_compliance_a > 0.70
    assert res.dag_compliance_b > 0.70
    assert res.is_statistically_invariant is True


def test_cross_medium_invariance(analyzer: PanIndusAnalyzer) -> None:
    """PAN-H2: Verify feed-forward DAG syntax across Seals, Tablets, and Tags."""
    media_res = analyzer.evaluate_cross_medium_invariance()
    res_dict = {m.medium: m for m in media_res}

    assert "seal" in res_dict
    assert "tablet" in res_dict
    assert "tag" in res_dict

    # Both stamp seals and incised tablets must adhere to DAG template (> 70%)
    assert res_dict["seal"].dag_compliance_rate > 0.70
    assert res_dict["tablet"].dag_compliance_rate > 0.70
    # Commercial cargo tags must exhibit the tightest feedforward constraint (> 80%)
    assert res_dict["tag"].dag_compliance_rate > 0.80


def test_motif_syntax_coupling(analyzer: PanIndusAnalyzer) -> None:
    """PAN-H3: Verify statistical coupling between animal motif and initial sign class."""
    mc = analyzer.evaluate_motif_coupling()
    assert mc.n_labeled_inscriptions > 1000
    assert mc.n_motifs >= 4
    # Chi2 independence test must be significant (p < 0.05)
    assert mc.chi2_stat > 20.0
    assert mc.p_value < 0.05
    assert mc.is_coupled is True


def test_directionality_asymmetry_proof(analyzer: PanIndusAnalyzer) -> None:
    """PAN-H4: Verify information-theoretic proof of Right-to-Left (R/L) reading order."""
    dp = analyzer.evaluate_directionality_asymmetry()

    assert dp.canonical_direction == "R/L"
    assert dp.canonical_compliance_rate > 0.40
    assert dp.retrograde_compliance_rate < 0.20
    # Canonical compliance must exceed retrograde by at least 2.5x
    assert dp.asymmetry_ratio > 2.5
    # Directional paired Z-score must exceed +20 sigma
    assert dp.z_score > 20.0
    assert dp.is_unidirectional is True


def test_pan_indus_ledger_integration() -> None:
    """Verify recording and Bonferroni FWER survival for Pan-Indus trials."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = EpistemicLedger(Path(tmpdir))

        ledger.record_trial(
            trial_id="test-pan-trial-1",
            artifact_id="INDUS_PAN_TEST",
            hypothesis_name="PAN_H1_CROSS_SITE_INVARIANCE",
            key_class="STRUCTURAL",
            payload_len=12910,
            unicity_distance=907.5,
            passed_unicity=False,
            raw_fitness=0.0664,
            empirical_p_value=0.0001,
            negative_twin_fitness=0.15,
            falsification_status="FALSIFIED_REGIONAL_DIVERGENCE",
            referee_evaluated=True,
            referee_verdict="CONFIRMED_CROSS_SITE",
        )

        stats = ledger.get_summary_statistics("INDUS_PAN_TEST")
        assert stats["total_trials_denominator"] == 1
        assert stats["candidate_count"] == 0
        assert stats["minimum_empirical_p"] == 0.0001
        assert stats["has_survived_multiplicity"] is True
