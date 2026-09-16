"""Unit tests for Rohonc Syllabic Phonetic Annealer & Language Models."""

from __future__ import annotations

import pytest

from projects.rohonc.syllabic_annealer import (
    AnnealingResult,
    CV_SYLLABLES,
    LATIN_VULGATE_LEXICON,
    OLD_HUNGARIAN_LEXICON,
    RohoncSyllabicAnnealer,
)


def test_lexicons_and_cv_inventory() -> None:
    """Verify that Old Hungarian, Latin, and CV inventories are initialized."""
    assert len(OLD_HUNGARIAN_LEXICON) >= 40
    assert "isten" in OLD_HUNGARIAN_LEXICON
    assert "krisztus" in OLD_HUNGARIAN_LEXICON

    assert len(LATIN_VULGATE_LEXICON) >= 40
    assert "deus" in LATIN_VULGATE_LEXICON
    assert "christus" in LATIN_VULGATE_LEXICON

    assert len(CV_SYLLABLES) >= 40
    assert "ka" in CV_SYLLABLES
    assert "te" in CV_SYLLABLES


def test_annealer_initialization() -> None:
    """Verify annealer targets non-logographic glyphs."""
    annealer = RohoncSyllabicAnnealer(language="hungarian", seed=42)
    assert len(annealer.target_glyphs) >= 10
    assert "R013" in annealer.target_glyphs
    assert "R014" in annealer.target_glyphs
    # Logograms like R001 (Christus) should NOT be in target syllabic glyphs
    assert "R001" not in annealer.target_glyphs
    assert "R002" not in annealer.target_glyphs


def test_mapping_evaluation() -> None:
    """Verify mapping evaluation computes score and vowel harmony."""
    annealer = RohoncSyllabicAnnealer(language="hungarian", seed=42)
    sample_mapping = {g: "te" for g in annealer.target_glyphs}
    score, hits, harmony = annealer.evaluate_mapping(sample_mapping)

    assert isinstance(score, float)
    assert isinstance(hits, int)
    assert 0.0 <= harmony <= 1.0


def test_annealing_run() -> None:
    """Verify annealing runs and returns improved candidate mapping."""
    annealer = RohoncSyllabicAnnealer(language="latin", seed=42)
    result = annealer.run_annealing(iterations=200)

    assert isinstance(result, AnnealingResult)
    assert result.iterations == 200
    assert len(result.best_mapping) == len(annealer.target_glyphs)
    assert len(result.sample_decipherments) > 0
    assert result.duration_seconds > 0.0
