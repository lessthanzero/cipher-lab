"""Unit and epistemic integrity tests for Dorabella Cipher module."""

from __future__ import annotations

from projects.dorabella.annealer import DorabellaAnnealer
from projects.dorabella.corpus import DORABELLA_TOKENS, get_dorabella_unicity
from projects.dorabella.hypotheses import (
    generate_keyword_alphabet_24,
    scramble_tokens,
)
from projects.dorabella.symbols import get_dorabella_symbols


def test_dorabella_tokens_integrity() -> None:
    """Verify canonical Dorabella token length, range, and line partitions."""
    assert len(DORABELLA_TOKENS) == 87
    assert all(0 <= t < 24 for t in DORABELLA_TOKENS)
    # 23 unique symbols appear in the 87 characters (one symbol variant is unused)
    assert len(set(DORABELLA_TOKENS)) == 23


def test_dorabella_symbols_geometry() -> None:
    """Verify physical symbol mapping to humps and orientation angles."""
    symbols = get_dorabella_symbols()
    assert len(symbols) == 87
    for s in symbols:
        assert 1 <= s.humps <= 3
        assert 0 <= s.orientation_idx <= 7
        assert s.angle_deg == s.orientation_idx * 45
        assert s.direction_name in ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]


def test_dorabella_unicity_distance() -> None:
    """Verify mathematical unicity gate for monoalphabetic vs homophonic spaces."""
    mono = get_dorabella_unicity("monoalphabetic")
    assert mono.is_underdetermined is False
    assert mono.unicity_distance_chars < len(DORABELLA_TOKENS)

    homo = get_dorabella_unicity("homophonic")
    assert homo.is_underdetermined is True
    assert homo.unicity_distance_chars > len(DORABELLA_TOKENS)


def test_dorabella_keyword_alphabet() -> None:
    """Verify keyed 24-letter alphabet generation."""
    alpha = generate_keyword_alphabet_24("EDWARDELGAR")
    assert len(alpha) == 24
    assert len(set(alpha)) == 24
    assert alpha.startswith("EDWARL")  # G, then remainder


def test_dorabella_scramble_preserves_marginals() -> None:
    """Verify twin-negative scrambled control preserves token marginal counts."""
    from collections import Counter
    orig_counts = Counter(DORABELLA_TOKENS)
    scrambled = scramble_tokens(DORABELLA_TOKENS, seed=123)
    scrambled_counts = Counter(scrambled)
    assert orig_counts == scrambled_counts


def test_dorabella_annealer_fast_step() -> None:
    """Verify simulated annealer executes without error."""
    annealer = DorabellaAnnealer()
    res = annealer.anneal(duration_secs=0.5, seed=42)
    assert len(res.plaintext) == 87
    assert res.q_score < 0
