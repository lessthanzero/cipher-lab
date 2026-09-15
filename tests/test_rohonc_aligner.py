"""Unit tests for Rohonc Liturgical Harmony Aligner and Diatessaron Matching."""

from __future__ import annotations

import pytest

from projects.rohonc.corpus import FOLIO_TRANSCRIPTIONS
from projects.rohonc.liturgical_aligner import (
    LITURGICAL_PASSION_HARMONY,
    AlignmentResult,
    RohoncLiturgicalAligner,
)


def test_liturgical_harmony_stages() -> None:
    """Verify liturgical stages cover canonical Passion sequence."""
    aligner = RohoncLiturgicalAligner()
    stages = aligner.harmony_stages

    assert len(stages) == 6
    stage_ids = [s.stage_id for s in stages]
    assert "stage_01_palm_sunday" in stage_ids
    assert "stage_02_last_supper" in stage_ids
    assert "stage_03_gethsemane" in stage_ids
    assert "stage_04_pilate" in stage_ids
    assert "stage_05_crucifixion" in stage_ids
    assert "stage_06_resurrection" in stage_ids


def test_semantic_profile_extraction() -> None:
    """Verify that semantic profiles extract roles while filtering punctuation."""
    aligner = RohoncLiturgicalAligner()
    test_lines = [["R001", "R045", "R055", "R046"]]  # Christus · Pilatus .
    profile = aligner.extract_folio_semantic_profile(test_lines)

    assert len(profile) == 2
    assert any("Christus" in r for r in profile)
    assert any("Pilatus" in r for r in profile)


def test_crucifixion_folio_alignment() -> None:
    """Verify that Folio 125v (Crucifixion) aligns to Stage 5 Crucifixion."""
    aligner = RohoncLiturgicalAligner()
    f125v = FOLIO_TRANSCRIPTIONS["folio_125v"]

    res = aligner.align_folio(
        folio_id=f125v["folio"],
        lines=f125v["lines"],
        folio_title=f125v["title"],
        n_null_permutations=200,
    )

    assert res.folio_id == "125v"
    assert "Crucifixion on Golgotha" in res.best_matching_stage
    assert "Cross/INRI" in res.matched_motifs
    assert res.alignment_score >= 40.0
    assert res.p_value < 0.10


def test_corpus_wide_alignment() -> None:
    """Verify alignment across all cataloged folios runs without error."""
    aligner = RohoncLiturgicalAligner()
    results = aligner.align_entire_corpus()

    assert len(results) == len(FOLIO_TRANSCRIPTIONS)
    assert all(isinstance(r, AlignmentResult) for r in results)
