"""Unit tests for Qumran Cryptic Scripts module."""

import pytest

from projects.qumran_cryptic.alphabet import (
    CRYPTIC_A_ASCII,
    CRYPTIC_A_TOKENS,
    HEBREW_ALPHABET,
    decode_cryptic_a,
    encode_cryptic_a,
    normalize_hebrew_text,
)
from projects.qumran_cryptic.corpus import get_qumran_cryptic_corpus
from projects.qumran_cryptic.markov_model import SectarianHebrewMarkovModel
from projects.qumran_cryptic.solver import QumranCrypticSolver


def test_alphabet_bijections() -> None:
    # 22 letters in canonical Hebrew
    assert len(HEBREW_ALPHABET) == 22
    assert len(CRYPTIC_A_TOKENS) == 22
    assert len(CRYPTIC_A_ASCII) == 22

    # Reversible encoding and decoding
    sample = "מדרש ספר משה אשר כתב אל בני ישראל"
    encoded_ascii = encode_cryptic_a(sample, format_mode="ascii")
    assert isinstance(encoded_ascii, str)
    decoded = decode_cryptic_a(encoded_ascii)
    assert decoded == normalize_hebrew_text(sample)


def test_corpus_catalog() -> None:
    corpus = get_qumran_cryptic_corpus()
    assert "4Q249" in corpus
    assert "4Q317" in corpus
    assert "4Q313" in corpus

    # 4Q249 has sufficient length for decipherment
    ms = corpus["4Q249"]
    assert ms.token_count > 100
    assert ms.script_type == "Cryptic A"


def test_unicity_distance_gate() -> None:
    solver = QumranCrypticSolver()
    # Unicity distance for 22-letter monoalphabetic substitution is ~21-25 chars
    eval_short = solver.calculate_unicity_distance(manuscript_length=15)
    assert not eval_short.passed_unicity_gate

    eval_4q249 = solver.calculate_unicity_distance(manuscript_length=179)
    assert eval_4q249.passed_unicity_gate
    assert eval_4q249.unicity_distance_chars < 30.0


def test_markov_scoring() -> None:
    model = SectarianHebrewMarkovModel()
    real_text = "שומרי הברית ודורשי רצונו בתורת אל"
    gibberish = "טקפזחגצטקפזחגצטקפזחגצ"
    score_real = model.score_text(real_text)
    score_gibberish = model.score_text(gibberish)
    # Real text must score higher (less negative) than gibberish
    assert score_real > score_gibberish
