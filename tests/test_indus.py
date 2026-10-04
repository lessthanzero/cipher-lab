"""Comprehensive unit and integration test suite for the Indus Script research track."""

from __future__ import annotations

import collections
import tempfile
from pathlib import Path

import pytest

from cipher_lab.ledger import EpistemicLedger
from projects.indus.concordance import IndusConcordance
from projects.indus.corpus import IndusCorpus
from projects.indus.grammar_engine import IndusGrammarEngine
from projects.indus.hmm_induction import DiscreteHMM, HMMTopologySweeper
from projects.indus.null_models import NullSurrogateGenerator
from projects.indus.spectral_clustering import IndusSpectralClusterer
from projects.indus.stats import (
    calculate_conditional_block_entropy,
    calculate_positional_entropy,
    calculate_repetition_metrics,
    calculate_shannon_entropy,
    calculate_unicity_distance,
)


@pytest.fixture
def corpus() -> IndusCorpus:
    return IndusCorpus()


@pytest.fixture
def concordance(corpus: IndusCorpus) -> IndusConcordance:
    return corpus.concordance


def test_concordance_mappings(concordance: IndusConcordance) -> None:
    """Verify bidirectional mappings and classic sign anchors."""
    summary = concordance.get_summary()
    assert summary["total_parpola_signs"] == 396
    assert summary["mapped_to_mahadevan"] >= 330
    assert summary["mapped_to_wells"] >= 330

    # Test the foundational "Classic Jar" sign anchor: P324 -> M342 -> W740
    entry_p324 = concordance.get_entry("P324")
    assert entry_p324 is not None
    assert "M342" in entry_p324.mahadevan_ids
    assert "W740" in entry_p324.wells_ids

    # Reversibility
    p_from_m = concordance.mahadevan_to_parpola("M342")
    assert p_from_m == "P324"

    # Sequence normalization
    raw_seq = ["P324", "P001", "P999"]
    norm_m = concordance.normalize_sequence(raw_seq, target_catalog="mahadevan")
    assert norm_m[0] == "M342"
    assert norm_m[1] == "M012"
    assert norm_m[2] == "P999"  # unmapped kept by default


def test_corpus_descriptive_invariants(corpus: IndusCorpus) -> None:
    """Verify headline corpus statistics against published Mohenjo-Daro benchmarks."""
    parpola_summary = corpus.get_summary("parpola")
    assert parpola_summary["inscription_count"] == 179
    assert parpola_summary["total_tokens"] == 1003
    assert parpola_summary["signary_types"] == 182
    assert 5.5 <= parpola_summary["mean_length"] <= 5.7
    assert parpola_summary["max_length"] == 13
    assert parpola_summary["min_length"] == 1
    assert 70 <= parpola_summary["singletons_hapax"] <= 85
    assert 0.40 <= parpola_summary["singleton_ratio"] <= 0.45

    # Mahadevan normalization invariant
    m77_summary = corpus.get_summary("mahadevan")
    assert m77_summary["inscription_count"] == 179
    assert m77_summary["total_tokens"] == 1003
    assert 175 <= m77_summary["signary_types"] <= 185
    assert m77_summary["mean_length"] == parpola_summary["mean_length"]


def test_positional_slot_rigidity(corpus: IndusCorpus) -> None:
    """H1: Test edge-to-middle positional entropy variance and slot rigidity."""
    seqs = corpus.get_sequences("parpola")
    prof = calculate_positional_entropy(seqs)

    # Edge (position 0) must be more constrained than internal position 1
    ent_pos0 = prof.position_entropies[0]
    ent_pos1 = prof.position_entropies[1]
    assert ent_pos0 < ent_pos1
    assert ent_pos0 < 4.0  # Strongly constrained boundary
    assert ent_pos1 > 5.5  # High-diversity internal slot

    # Friedman test across slots must reject uniform positional distribution
    assert prof.friedman_chi2 > 30.0
    assert prof.friedman_p_value < 1e-5
    assert prof.is_slot_rigid is True


def test_sign_repetition_deficit(corpus: IndusCorpus) -> None:
    """H2: Test sign repetition suppression (The Farmer-Sproat Invariant)."""
    seqs = corpus.get_sequences("parpola")
    rep = calculate_repetition_metrics(seqs)

    assert rep.total_inscriptions == 179
    assert rep.total_tokens == 1003
    # Inscriptions with repetitions must be low (< 15%)
    assert rep.repetition_rate < 0.15
    # Token repetition rate must be < 3%
    assert rep.token_repetition_rate < 0.03


def test_conditional_block_entropy(corpus: IndusCorpus) -> None:
    """H3: Replicate conditional block entropy profile."""
    seqs = corpus.get_sequences("parpola")
    cond = calculate_conditional_block_entropy(seqs)

    assert 6.0 <= cond.order_0_entropy <= 6.5
    assert 2.3 <= cond.order_1_entropy <= 2.9
    assert 0.2 <= cond.order_2_entropy <= 0.6
    assert 0.35 <= cond.conditional_drop_ratio <= 0.48


def test_shannon_unicity_distance_gate(corpus: IndusCorpus) -> None:
    """H4: Verify Shannon unicity distance violation (mathematical underdetermination)."""
    seqs = corpus.get_sequences("parpola")
    unicity = calculate_unicity_distance(seqs)

    assert unicity.signary_size == 182
    assert unicity.mean_message_length < 6.0
    assert unicity.max_message_length == 13
    assert unicity.unicity_distance_tokens > 500.0
    assert unicity.is_underdetermined is True
    # Combinatorial capacity must exceed 1 million distinct registration tags
    assert unicity.combinatorial_capacity > 1_000_000


def test_hostile_null_permutations(corpus: IndusCorpus) -> None:
    """Verify structural preservation of hostile null surrogate generators."""
    seqs = corpus.get_sequences("parpola")
    gen = NullSurrogateGenerator(seqs, seed=42)

    # Null 1: Uniform
    unif = gen.null_uniform()
    assert len(unif) == len(seqs)
    assert [len(s) for s in unif] == [len(s) for s in seqs]

    # Null 2: Frequency-preserving within-sequence shuffle
    freq = gen.null_frequency_preserving()
    assert len(freq) == len(seqs)
    assert [len(s) for s in freq] == [len(s) for s in seqs]
    # Check that global token frequencies are exactly identical
    orig_counts = collections.Counter(s for q in seqs for s in q)
    freq_counts = collections.Counter(s for q in freq for s in q)
    assert orig_counts == freq_counts

    # Null 3: Positional marginal preserving
    pos = gen.null_positional_marginal_preserving()
    assert len(pos) == len(seqs)
    assert [len(s) for s in pos] == [len(s) for s in seqs]
    # Positional marginal token distributions must be identical per slot
    for p in range(4):
        orig_pos = collections.Counter(q[p] for q in seqs if len(q) > p)
        pos_pos = collections.Counter(q[p] for q in pos if len(q) > p)
        assert orig_pos == pos_pos


def test_epistemic_ledger_integration(corpus: IndusCorpus) -> None:
    """Verify recording and Bonferroni / FDR denominator adjustments in DuckDB."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ledger = EpistemicLedger(Path(tmpdir))
        
        # Record a synthetic trial
        ledger.record_trial(
            trial_id="test-indus-trial-1",
            artifact_id="INDUS_TEST",
            hypothesis_name="H1_SLOT_RIGIDITY",
            key_class="STRUCTURAL",
            payload_len=182,
            unicity_distance=907.5,
            passed_unicity=False,
            raw_fitness=3.32,
            empirical_p_value=0.0001,
            negative_twin_fitness=5.5,
            falsification_status="CANDIDATE",
            referee_evaluated=True,
            referee_verdict="CONFIRMED",
        )

        stats = ledger.get_summary_statistics("INDUS_TEST")
        assert stats["total_trials_denominator"] == 1
        assert stats["candidate_count"] == 1
        assert stats["minimum_empirical_p"] == 0.0001
        assert stats["bonferroni_critical_p"] == 0.05
        assert stats["has_survived_multiplicity"] is True


def test_spectral_clustering_decomposition(corpus: IndusCorpus) -> None:
    """H5: Verify spectral graph decomposition and functional class induction."""
    clusterer_p = IndusSpectralClusterer(corpus, target_catalog="parpola")
    res_p = clusterer_p.decompose(n_clusters=5, seed=42)

    assert len(res_p.eigenvalues) >= 10
    assert res_p.eigengap_index <= 6
    assert res_p.dag_feedforward_ratio > 0.75
    assert len(res_p.classes) == 5

    # Cross-catalog consistency
    clusterer_m = IndusSpectralClusterer(corpus, target_catalog="mahadevan")
    res_m = clusterer_m.decompose(n_clusters=5, seed=42)
    assert res_m.eigengap_index <= 6
    assert res_m.dag_feedforward_ratio > 0.75


def test_hmm_topology_sweep_and_bic(corpus: IndusCorpus) -> None:
    """H6: Verify HMM model selection sweep and BIC global minimum."""
    clusterer = IndusSpectralClusterer(corpus, target_catalog="parpola")
    res = clusterer.decompose(n_clusters=5, seed=42)
    class_seqs = [
        [str(res.sign_to_class[s]) for s in seq]
        for seq in corpus.get_sequences("parpola")
    ]

    sweeper = HMMTopologySweeper(class_seqs)
    sweep = sweeper.sweep(k_values=[2, 3, 4, 5], n_restarts=6, seed=42)

    # Global minimum in this range is 4 or 5 states (compact regular grammar)
    assert sweep.best_bic_k in (4, 5)
    assert sweep.min_bic < 2600.0


def test_grammar_engine_viterbi_and_mdl(corpus: IndusCorpus) -> None:
    """H7 & H8: Verify Viterbi dynamic programming decoding and MDL compression."""
    engine = IndusGrammarEngine(corpus, target_catalog="parpola", n_classes=5, n_states=4, seed=42)
    rep = engine.evaluate_corpus()

    assert rep.dag_compliance_rate > 0.60
    assert rep.compression_ratio_percent > 65.0
    assert rep.raw_corpus_bits > rep.grammar_mdl_bits
    assert rep.unigram_corpus_bits > rep.grammar_mdl_bits

    # Test individual Viterbi decode
    score, states = engine.viterbi_decode([0, 1, 2, 4])
    assert len(states) == 4
    assert all(isinstance(s, int) for s in states)
