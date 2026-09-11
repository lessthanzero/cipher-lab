"""Unit tests for Admiralty Sweep module."""

from projects.dagapeyeff.admiralty_sweep import (
    ADMIRALTY_KEYWORDS_14,
    generate_hydrographical_duplicate_rankings,
)


def test_admiralty_keywords_presence():
    assert "HYDROGRAPHICAL" in ADMIRALTY_KEYWORDS_14
    assert "ADMIRALTYCHART" in ADMIRALTY_KEYWORDS_14
    assert "SOUNDINGSCHART" in ADMIRALTY_KEYWORDS_14
    assert len(ADMIRALTY_KEYWORDS_14) >= 6


def test_hydrographical_duplicate_rankings():
    variants = generate_hydrographical_duplicate_rankings()
    assert len(variants) >= 8  # 1 std + 7 tie-breaks + 1 kerckhoffs defect
    for label, ranks in variants:
        assert len(ranks) == 14
        assert sorted(ranks) == list(range(14))
