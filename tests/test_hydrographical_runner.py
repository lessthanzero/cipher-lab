"""Unit tests for HYDROGRAPHICAL Deep Runner."""

from projects.dagapeyeff.hydrographical_deep_runner import (
    NAUTICAL_CARTOGRAPHIC_KEYWORDS,
    get_hydrographical_transposed_pairs,
)


def test_hydrographical_transposed_pairs_shape():
    pairs = get_hydrographical_transposed_pairs()
    assert len(pairs) == 182
    assert all(len(p) == 2 for p in pairs)
    assert all(p[0] in "67890" for p in pairs)
    assert all(p[1] in "12345" for p in pairs)
    # Ensure Column 14 nulls (which contained 04) are stripped
    assert "04" not in pairs


def test_nautical_keywords_pool():
    assert "HYDROGRAPHICAL" in NAUTICAL_CARTOGRAPHIC_KEYWORDS
    assert "ADMIRALTY" in NAUTICAL_CARTOGRAPHIC_KEYWORDS
    assert len(NAUTICAL_CARTOGRAPHIC_KEYWORDS) >= 10
