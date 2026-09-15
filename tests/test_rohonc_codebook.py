"""Unit tests for Király-Tokai Codebook Engine, NER, and Formulaic Cluster Discovery."""

from __future__ import annotations

import pytest

from projects.rohonc.codebook import (
    KIRALY_TOKAI_CODEBOOK,
    CodebookEntry,
    NamedEntityMatch,
    RohoncCodebookEngine,
)
from projects.rohonc.corpus import FOLIO_TRANSCRIPTIONS, get_all_rohonc_lines


def test_kiraly_tokai_codebook_coverage() -> None:
    """Verify that core Király-Tokai codebook contains all mandatory liturgical categories."""
    engine = RohoncCodebookEngine()
    categories = {entry.category for entry in engine.codebook.values()}

    assert "divine" in categories
    assert "sacred_person" in categories
    assert "evangelist" in categories
    assert "historical_actor" in categories
    assert "sacramental" in categories
    assert "affix" in categories
    assert "numeral" in categories
    assert "delimiter" in categories

    # Test key divine monograms
    assert engine.classify_token("R001").latin_equivalent.startswith("Christus")
    assert engine.classify_token("R002").latin_equivalent.startswith("Deus")
    assert engine.classify_token("R039").latin_equivalent.startswith("Sancta Maria")
    assert engine.classify_token("R025").latin_equivalent.startswith("Trinitas")

    # Test evangelists
    assert engine.classify_token("R051").latin_equivalent == "Matthaeus"
    assert engine.classify_token("R052").latin_equivalent == "Marcus"
    assert engine.classify_token("R053").latin_equivalent == "Lucas"
    assert engine.classify_token("R054").latin_equivalent == "Iohannes"


def test_named_entity_extraction() -> None:
    """Verify named entity recognition across sample lines."""
    engine = RohoncCodebookEngine()

    # Test passion trial sequence: Pilate + Christ + Soldiers
    test_lines = [
        ["R055", "R045", "R001", "R046"],  # Pilate · Christ .
        ["R060", "R010", "R045", "R057"],  # Soldier-plural · Peter
    ]
    entities = engine.extract_named_entities(test_lines, folio_label="test_folio")

    assert len(entities) >= 3
    names = [e.entity_name for e in entities]
    assert any("Pilatus" in n for n in names)
    assert any("Christus" in n for n in names)
    assert any("Petrus" in n for n in names)


def test_evangelist_chapter_citation_parsing() -> None:
    """Verify compound scriptural citations: e.g. [Evangelist, WordSeparator, Numeral]."""
    engine = RohoncCodebookEngine()

    # R051 (Matthaeus) + R045 (·) + R019 (I / 1)
    citation_line = [["R051", "R045", "R019", "R046"]]
    matches = engine.extract_named_entities(citation_line, folio_label="178r")

    citation_matches = [m for m in matches if m.entity_type == "scriptural_citation"]
    assert len(citation_matches) == 1
    assert "Matthaeus" in citation_matches[0].entity_name
    assert "Cap. I" in citation_matches[0].entity_name


def test_interlinear_gloss_generation() -> None:
    """Verify that interlinear gloss generation translates recognized tokens correctly."""
    engine = RohoncCodebookEngine()
    lines = [["R001", "R041", "R042", "R043"]]
    glosses = engine.generate_folio_gloss(lines)

    assert len(glosses) == 1
    assert "Christus" in glosses[0]
    assert "Pater" in glosses[0]
    assert "Filius" in glosses[0]
    assert "Spiritus Sanctus" in glosses[0]


def test_formulaic_cluster_discovery() -> None:
    """Verify discovery of frequent recurrent n-grams in the corpus."""
    engine = RohoncCodebookEngine()
    lines = get_all_rohonc_lines()
    clusters = engine.find_recurring_clusters(lines, n=2, min_freq=2)

    assert len(clusters) > 0
    # Check that top cluster is Apostles plural: [R044, R010]
    top_cluster = clusters[0]
    assert top_cluster["signs"] == ["R044", "R010"]
    assert top_cluster["frequency"] >= 5
    assert "Apostolus" in top_cluster["gloss"]
