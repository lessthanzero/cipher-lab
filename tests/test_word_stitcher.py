"""Unit tests for Word Stitcher module."""

from projects.dagapeyeff.word_stitcher import (
    ENGLISH_CORE_LEXICON,
    count_dictionary_words,
)


def test_lexicon_presence():
    assert "EAST" in ENGLISH_CORE_LEXICON
    assert "WEST" in ENGLISH_CORE_LEXICON
    assert "SAIL" in ENGLISH_CORE_LEXICON
    assert "HULL" in ENGLISH_CORE_LEXICON
    assert len(ENGLISH_CORE_LEXICON) >= 40


def test_count_dictionary_words():
    sample = "THENEWSAILORWENTTOEASTHULLANDWESTPORT"
    total_len, words = count_dictionary_words(sample)
    assert total_len > 0
    assert "EAST" in words
    assert "WEST" in words
    assert "HULL" in words
    assert "SAIL" in words or "SAILOR" in words or "AND" in words
