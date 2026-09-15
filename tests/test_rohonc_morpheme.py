"""Unit tests for Rohonc Graph-Theoretic Morpheme Clusterer & Positional Affix Classifier."""

from __future__ import annotations

import pytest

from projects.rohonc.morpheme_clusterer import (
    MorphemeCommunity,
    RohoncMorphemeClusterer,
    SignGraphMetrics,
)


def test_cooccurrence_graph_building() -> None:
    """Verify co-occurrence graph generation over sample lines."""
    test_lines = [
        ["R001", "R002", "R025"],
        ["R001", "R025", "R039"],
    ]
    clusterer = RohoncMorphemeClusterer(lines=test_lines)
    edges = clusterer.build_cooccurrence_graph()

    assert len(edges) > 0
    # Pair (R001, R025) appears in both lines -> weight 2
    pair = tuple(sorted(["R001", "R025"]))
    assert edges[pair] == 2


def test_positional_bias_calculation() -> None:
    """Verify left-terminal vs right-initial positional bias calculations."""
    test_lines = [
        ["R001", "R014", "R010"],  # R001 is Right (initial), R010 is Left (terminal)
        ["R001", "R035", "R010"],
        ["R002", "R014", "R010"],
    ]
    clusterer = RohoncMorphemeClusterer(lines=test_lines)
    biases = clusterer.calculate_positional_biases()

    assert "R010" in biases
    assert "R001" in biases

    # In RTL: line[0] is Right (initial), line[-1] is Left (terminal)
    l_bias_r010, r_bias_r010 = biases["R010"]
    assert l_bias_r010 == 1.0  # Appears at left edge 100% of the time
    assert r_bias_r010 == 0.0

    l_bias_r001, r_bias_r001 = biases["R001"]
    assert r_bias_r001 >= 0.60  # Mostly at right edge


def test_sign_graph_metrics_and_affix_candidacy() -> None:
    """Verify sign metrics identify key affixes and divine hubs."""
    clusterer = RohoncMorphemeClusterer()
    metrics = clusterer.compute_sign_metrics()

    assert len(metrics) > 0
    sign_ids = [m.sign_id for m in metrics]
    assert "R001" in sign_ids
    assert "R010" in sign_ids

    # R010 (plural affix) should be recognized as a candidate affix
    r010_m = next(m for m in metrics if m.sign_id == "R010")
    assert r010_m.is_candidate_affix is True
    assert r010_m.degree >= 5


def test_functional_communities_extraction() -> None:
    """Verify extraction of the 5 canonical functional communities."""
    clusterer = RohoncMorphemeClusterer()
    comms = clusterer.extract_functional_communities()

    assert len(comms) == 5
    labels = [c.label for c in comms]
    assert any("Divine" in l for l in labels)
    assert any("Passion" in l for l in labels)
    assert any("Evangelist" in l for l in labels)
    assert any("Mariological" in l for l in labels)
    assert any("Affixes" in l for l in labels)
