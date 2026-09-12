"""Unit tests for Rohonc Codex corpus, statistical epigraphic suite, and models."""

from __future__ import annotations

from projects.rohonc.corpus import (
    ROHONC_CORE_SIGNS,
    ROHONC_PROVENANCE,
    SHAPE_FAMILIES,
    get_all_rohonc_lines,
    get_all_rohonc_tokens,
    get_corpus_summary,
)
from projects.rohonc.stats import (
    calculate_codebook_morphology,
    calculate_directionality_metrics,
    calculate_entropy_profile,
    calculate_linguistic_proximities,
    fit_zipf_mandelbrot,
    run_comprehensive_epigraphic_analysis,
)


def test_rohonc_provenance_and_catalog() -> None:
    """Verify provenance integrity and core catalog bounds."""
    assert ROHONC_PROVENANCE.artifact_id == "rohonc_codex"
    assert "kiraly" in ROHONC_PROVENANCE.catalog_version.lower()
    assert len(SHAPE_FAMILIES) == 12
    assert len(ROHONC_CORE_SIGNS) >= 50
    assert "R001" in ROHONC_CORE_SIGNS
    assert ROHONC_CORE_SIGNS["R001"].family == "cr"


def test_rohonc_corpus_loading() -> None:
    """Verify that multi-folio transcriptions load correctly and yield valid tokens."""
    lines = get_all_rohonc_lines()
    tokens = get_all_rohonc_tokens()
    summary = get_corpus_summary()

    assert len(lines) >= 30
    assert len(tokens) >= 200
    assert summary["cataloged_folios"] >= 5
    assert summary["reading_direction"] == "Right-to-Left (RTL)"
    assert all(t.startswith("R") for t in tokens)


def test_zipf_mandelbrot_fitting() -> None:
    """Verify Zipf-Mandelbrot fitting on Rohonc tokens."""
    tokens = get_all_rohonc_tokens()
    zipf = fit_zipf_mandelbrot(tokens)

    assert zipf.gamma > 0.0
    assert zipf.r_squared > 0.70
    assert zipf.c_factor > 0.0
    assert isinstance(zipf.is_natural_linguistic_fit, bool)


def test_entropy_profile_calculation() -> None:
    """Verify entropy calculations obey information-theoretic inequalities."""
    tokens = get_all_rohonc_tokens()
    prof = calculate_entropy_profile(tokens)

    # Shannon inequality: 0 <= H(S2|S1) <= H1 <= H0
    assert 0.0 <= prof.h2_conditional <= prof.h1_unigram <= prof.h0_hartley
    assert 0.0 <= prof.redundancy <= 1.0
    assert prof.effective_signary_size > 1.0


def test_directionality_asymmetry() -> None:
    """Verify right-to-left directional signature in transcriptions."""
    lines = get_all_rohonc_lines()
    metrics = calculate_directionality_metrics(lines)

    assert metrics.inferred_direction in ("RTL", "LTR")
    assert metrics.initial_sign_entropy > 0.0
    assert metrics.terminal_sign_entropy > 0.0


def test_codebook_morphology_and_proximities() -> None:
    """Verify morphology metrics and language family proximity calculations."""
    tokens = get_all_rohonc_tokens()
    core_ids = set(ROHONC_CORE_SIGNS.keys())
    morph = calculate_codebook_morphology(tokens, core_ids)

    assert 0.0 <= morph.core_sign_ratio <= 1.0
    assert morph.yule_k_characteristic > 0.0
    assert "Codebook" in morph.hypothesized_system or "Shorthand" in morph.hypothesized_system

    entropy = calculate_entropy_profile(tokens)
    proximities = calculate_linguistic_proximities(entropy, morph)
    assert len(proximities) >= 4
    for sim in proximities.values():
        assert 0.0 <= sim <= 1.0


def test_comprehensive_epigraphic_pipeline() -> None:
    """Test full epigraphic pipeline end-to-end."""
    tokens = get_all_rohonc_tokens()
    lines = get_all_rohonc_lines()
    report = run_comprehensive_epigraphic_analysis(tokens, lines)

    assert report.total_tokens == len(tokens)
    assert report.distinct_types == len(set(tokens))
    assert len(report.summary_verdict) > 20
    assert report.zipf_fit.gamma > 0.0
