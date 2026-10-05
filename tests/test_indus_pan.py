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


def test_compound_clause_grammar(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """PAN-H6: Verify compound multi-clause regular grammar resolves the non-compliance gap."""
    from projects.indus.compound_grammar import CompoundGrammarEngine

    engine = CompoundGrammarEngine(analyzer=analyzer, corpus=pan_corpus)
    report, parses = engine.evaluate_corpus()

    assert report.total_inscriptions == 3043
    # 1-clause baseline is ~44%
    assert 0.40 <= report.one_clause_rate <= 0.48
    # <=2 clauses must explain >= 84% of inscriptions
    assert report.two_clause_rate >= 0.84
    # <=3 clauses must explain >= 95% of inscriptions
    assert report.three_clause_rate >= 0.95
    # Unexplained rate must drop below 5%
    assert report.unexplained_rate <= 0.05
    # Clausal boundary resets must be overwhelmingly preceded by Class 4 (Terminal Jar Sink)
    assert report.terminal_boundary_reset_ratio >= 0.60

    # Test single parse dynamic programming segmentation
    p_mono = engine.parse_inscription([0, 1, 2, 4], ["P001", "P060", "P147", "P324"])
    assert p_mono.n_clauses == 1
    assert p_mono.is_compliant is True

    p_compound = engine.parse_inscription([0, 1, 4, 1, 4], ["P001", "P060", "P324", "P060", "P324"])
    assert p_compound.n_clauses == 2
    assert p_compound.clause_boundaries == (3,)
    assert p_compound.boundary_transitions == ((4, 1),)

    p_three = engine.parse_inscription([1, 4, 1, 4, 2, 4], ["P060", "P324", "P060", "P324", "P147", "P324"])
    assert p_three.n_clauses == 3
    assert p_three.clause_boundaries == (2, 4)


def test_ligature_morphology_algebra(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """PAN-H7: Verify graphemic morphology and ligature decomposition algebra."""
    from projects.indus.ligature_algebra import LigatureDecomposer, LigatureMorphologyAnalyzer

    decomposer = LigatureDecomposer()
    r, m, _ = decomposer.decompose("P324")
    assert r == "JAR"

    r_fish, m_fish, _ = decomposer.decompose("P048")
    assert r_fish == "FISH"

    morph = LigatureMorphologyAnalyzer(corpus=pan_corpus, analyzer=analyzer)
    report = morph.evaluate_morphology()

    assert report.n_analyzed_tokens > 12000
    assert report.h_class_total > 2.0
    # Modifier alone must reduce syntactic uncertainty (MI > 0.10 bits)
    assert report.mi_modifier > 0.10
    # Joint root + modifier must provide >= 0.50 bits of syntactic constraint
    assert report.mi_joint > 0.50
    # Positive synergistic information between root and modifier
    assert report.synergy_delta_i > 0.0
    # Chi-squared test must reject independence (p < 1e-10)
    assert report.chi2_stat > 1000.0
    assert report.chi2_p_value < 1e-10


def test_dholavira_signboard_structural_fit(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """PAN-H8: Verify Dholavira Citadel Gateway Signboard decomposes into 4 monotonic formulaic clauses."""
    from projects.indus.dholavira_signboard import DholaviraSignboardAnalyzer

    s_analyzer = DholaviraSignboardAnalyzer(corpus=pan_corpus, analyzer=analyzer)
    report = s_analyzer.analyze_signboard()

    assert report.length == 10
    assert report.is_four_clause_compliant is True
    assert len(report.segments) == 4
    assert report.delimiter_sign == "P378"
    assert report.delimiter_frequency == 4
    assert report.delimiter_positions == (0, 3, 7, 8)
    assert report.boundary_transitions == ((2, 0), (4, 1), (4, 0))

    # All four clausal segments must be strictly monotonic non-decreasing
    assert all(seg.is_dag_monotonic for seg in report.segments)
    assert report.segments[0].classes == (0, 1, 2)
    assert report.segments[1].classes == (0, 4)
    assert report.segments[2].classes == (1, 4)
    assert report.segments[3].classes == (0, 0, 4)


def test_ancient_comparative_typology(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """PAN-H9: Verify mathematical typological separation: Indus aligns with administrative accounts."""
    from projects.indus.comparative_typology import AncientTypologyComparator

    comp = AncientTypologyComparator(corpus=pan_corpus, analyzer=analyzer)
    report = comp.run_comparative_benchmark()

    assert "Indus_Cargo_Tags" in report.metrics
    assert "Minoan_Linear_A" in report.metrics
    assert "Proto_Elamite_Accounts" in report.metrics

    # Commercial tags must display rigid feedforward syntax (> 85% DAG compliance, < 15% cyclicity)
    m_tags = report.metrics["Indus_Cargo_Tags"]
    assert m_tags.forward_dag_compliance > 0.85
    assert m_tags.backward_cyclicity < 0.15

    # Typological vector distance must place Indus closer to Proto-Elamite accounts than spoken language
    assert report.is_closer_to_administrative_than_phonetic is True
    assert report.indus_vs_proto_elamite_similarity < 0.25


def test_indus_structural_reader(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """Verify end-to-end structural parser and administrative glossing engine."""
    from projects.indus.reader import IndusReader

    reader = IndusReader(corpus=pan_corpus, analyzer=analyzer)

    # Test Dholavira Signboard 144.1
    res_dh = reader.read_artifact("144.1")
    assert res_dh is not None
    assert res_dh.length == 9
    assert res_dh.n_clauses == 4
    assert res_dh.is_fully_compliant is True
    assert "WHEEL" in res_dh.clauses[0].gloss_text

    # Test Allahdino Cargo Tag 5.1
    res_tag = reader.read_artifact("5.1")
    assert res_tag is not None
    assert res_tag.n_clauses == 1
    assert res_tag.is_fully_compliant is True
    assert "TERMINAL VERIFICATION SINK" in res_tag.clauses[0].gloss_text


def test_meluhha_international_trade_audit(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """PAN-H10: Verify Meluhha international trade audit across Near-Eastern sites."""
    from projects.indus.international_trade import MeluhhaTradeAuditor

    auditor = MeluhhaTradeAuditor(corpus=pan_corpus, analyzer=analyzer)
    report, audits = auditor.audit_international_corpus()

    assert report.total_foreign_inscriptions >= 15
    # Over 80% of expatriate inscriptions maintain Harappan scribal grammar
    assert report.compliance_rate >= 0.80
    # Left-to-Right writing direction is elevated by >2.5x due to cuneiform influence
    assert report.lr_elevation_ratio > 2.5
    # Creolized anomalies (Ur, Susa, Janabiyah) are systematically isolated
    assert len(report.creolized_anomalies) >= 2


def test_numerical_stroke_metrology(pan_corpus: PanIndusCorpus, analyzer: PanIndusAnalyzer) -> None:
    """PAN-H11: Verify Indus numerical stroke system and commodity binding algebra."""
    from projects.indus.numerical_system import IndusNumericalAnalyzer

    num_analyzer = IndusNumericalAnalyzer(corpus=pan_corpus, analyzer=analyzer)
    report, patterns = num_analyzer.analyze_numerals()

    assert report.total_numeral_tokens > 2000
    assert report.numeral_token_percentage > 15.0
    # Numeral -> successor mutual information must exceed 1.0 bit
    assert report.numeral_noun_mutual_information > 1.0
    # Tall numerals (P145, P147, P150) must bind to container measure U (P310)
    u_patterns = [p for p in patterns if p.target_sign == "P310"]
    assert len(u_patterns) >= 3
    assert sum(p.co_occurrence_count for p in u_patterns) > 250





