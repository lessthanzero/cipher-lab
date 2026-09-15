"""Unit tests for Rohonc Pseudohistory Debunker Engine."""

from __future__ import annotations

import pytest

from projects.rohonc.debunker import DebunkVerdict, RohoncDebunkerEngine


def test_debunk_nemes_forgery_myth() -> None:
    """Verify that the 19th-century Nemes forgery claim is definitively falsified."""
    debunker = RohoncDebunkerEngine()
    verdict = debunker.debunk_nemes_forgery_myth()

    assert isinstance(verdict, DebunkVerdict)
    assert verdict.is_falsified is True
    assert verdict.claim_id == "nemes_19c_forgery"
    assert "watermark" in verdict.falsification_vector.lower()
    assert verdict.observed_metric < verdict.expected_threshold


def test_debunk_enachiuc_dacian_claim() -> None:
    """Verify that Viorica Enăchiuc's Dacian battle claim is falsified by mapping consistency."""
    debunker = RohoncDebunkerEngine()
    verdict = debunker.debunk_enachiuc_dacian_claim()

    assert verdict.is_falsified is True
    assert verdict.claim_id == "enachiuc_2002_dacian"
    assert verdict.observed_metric < verdict.expected_threshold  # 0.12 < 0.85


def test_debunk_lackadaisical_romanian_claim() -> None:
    """Verify Lackadaisical Security's rotational cipher is falsified by unicity distance."""
    debunker = RohoncDebunkerEngine()
    verdict = debunker.debunk_lackadaisical_romanian_claim()

    assert verdict.is_falsified is True
    assert verdict.claim_id == "lackadaisical_2025_rotational"
    assert verdict.observed_metric < verdict.expected_threshold  # 12 tokens < 314 required


def test_debunk_nyiri_sumerian_and_singh_hindi() -> None:
    """Verify that Sumerian/Hindi claims are falsified by RTL directionality & Christian context."""
    debunker = RohoncDebunkerEngine()
    verdict = debunker.debunk_nyiri_sumerian_and_singh_hindi()

    assert verdict.is_falsified is True
    assert verdict.claim_id == "nyiri_sumerian_singh_hindi"
    assert verdict.observed_metric >= verdict.expected_threshold  # 4.8 sigma >= 3.0


def test_run_all_debunkers() -> None:
    """Verify batch execution of all refutation modules."""
    debunker = RohoncDebunkerEngine()
    verdicts = debunker.run_all_debunkers()

    assert len(verdicts) == 4
    assert all(v.is_falsified for v in verdicts)
