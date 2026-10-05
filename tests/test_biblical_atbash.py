"""Unit tests for Biblical Atbash Cryptographic module."""

import pytest

from projects.biblical_atbash.cipher import (
    ATBASH_MAP,
    HEBREW_ALPHABET,
    normalize_hebrew_word,
    transform_albam,
    transform_atbah,
    transform_atbash,
)
from projects.biblical_atbash.lexicon import BiblicalLexicon
from projects.biblical_atbash.null_engine import AtbashNullEngine
from projects.biblical_atbash.sweep import BiblicalAtbashSweeper


def test_atbash_reversibility() -> None:
    # Atbash must be strictly self-inverse: Atbash(Atbash(x)) == x
    for letter in HEBREW_ALPHABET:
        assert transform_atbash(transform_atbash(letter)) == letter

    # Jeremiah 25:26 canonical cipher: ששך <-> בבל
    assert transform_atbash("ששכ") == "בבל"
    assert transform_atbash("בבל") == "ששכ"


def test_jeremiah_atbash_sweep() -> None:
    lexicon = BiblicalLexicon()
    sweeper = BiblicalAtbashSweeper(lexicon=lexicon)
    hits = sweeper.sweep_verses()
    assert len(hits) >= 2

    sheshach_hits = [h for h in hits if h.transformed_text == "בבל"]
    assert len(sheshach_hits) >= 1
    assert sheshach_hits[0].is_known_biblical_cipher

    lebkamai_hits = [h for h in hits if h.transformed_text in ("כשדים", "כשדימ")]
    assert len(lebkamai_hits) >= 1
    assert lebkamai_hits[0].is_known_biblical_cipher


def test_null_engine_significance() -> None:
    engine = AtbashNullEngine()
    # Evaluating ששך against 500 permutations should demonstrate low null hit rate
    res = engine.evaluate_candidate("ששך", n_permutations=500, seed=42)
    assert res["is_lexicon_hit"] is True
    assert res["transformed_atbash"] == "בבל"
    # Null hit rate for a random 3-letter word hitting the lexicon should be < 5%
    assert res["null_hit_rate"] < 0.05
    assert res["z_score"] > 2.0
