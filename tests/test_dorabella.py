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


def test_liszt_1886_corpus_integrity() -> None:
    """Verify 1886 Liszt fragment structure, word segmentation, and provenance."""
    from projects.dorabella.liszt_corpus import (
        LISZT_1886_RAW,
        LISZT_1886_WORDS,
        LISZT_1886_WORD_LENGTHS,
        LISZT_METADATA,
        evaluate_dual_corpus,
    )
    from projects.dorabella.corpus import DORABELLA_AUTHENTIC_CONSENSUS

    assert len(LISZT_1886_RAW) == 18
    assert len(LISZT_1886_WORDS) == 4
    assert [len(w) for w in LISZT_1886_WORDS] == [3, 6, 3, 6]
    assert LISZT_METADATA.has_underscore is True
    assert LISZT_METADATA.composer == "Franz Liszt"
    assert "Les Préludes" in LISZT_METADATA.piece

    # Test dual-corpus evaluator with identity mapping
    key = {c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    eval_res = evaluate_dual_corpus(key, DORABELLA_AUTHENTIC_CONSENSUS)
    assert len(eval_res["dorabella_plaintext"]) == 87
    assert eval_res["liszt_words"] == ["BMK", "GKKOIM", "MCG", "KMBKCC"]
    assert eval_res["liszt_plaintext"] == "BMK GKKOIM MCG KMBKCC_"


def test_liszt_1886_midi_synthesis(tmp_path) -> None:
    """Verify Liszt fragment can be synthesized into standard MIDI."""
    from projects.dorabella.dual_musical_engine import DualMusicalCipherEngine

    liszt_tokens = [16, 18, 14, 6, 14, 13, 2, 1, 10, 18, 2, 6, 14, 10, 16, 14, 2, 3]
    engine = DualMusicalCipherEngine(tokens=liszt_tokens)
    out_file = tmp_path / "test_liszt.mid"
    engine.generate_midi_file(output_path=out_file, scale="e_minor", tempo_bpm=96)
    assert out_file.exists()
    assert out_file.stat().st_size > 100

    out_wav = tmp_path / "test_liszt.wav"
    engine.generate_wav_file(output_path=out_wav, scale="e_minor", tempo_bpm=96, timbre="flute")
    assert out_wav.exists()
    assert out_wav.stat().st_size > 1000



def test_counterpoint_evaluator() -> None:
    """Verify contrapuntal voice-leading alignment against Enigma and candidate themes."""
    from projects.dorabella.counterpoint_evaluator import CounterpointEvaluator, DIES_IRAE_CANTUS

    evaluator = CounterpointEvaluator()
    res = evaluator.evaluate_alignment(DIES_IRAE_CANTUS, "Dies Irae", offset=1)
    assert res.total_aligned_notes == 9
    assert res.consonance_ratio > 0.80
    assert res.parallel_fifths_count == 0
    assert res.parallel_octaves_count == 0


def test_vowel_restoration_engine() -> None:
    """Verify shorthand consonant skeleton parsing and beam search expansion."""
    from projects.dorabella.vowel_restoration_engine import ShorthandVowelRestorer, to_skeleton

    assert to_skeleton("DORABELLA") == "DRBLL"
    assert to_skeleton("EDWARD") == "DWRD"

    restorer = ShorthandVowelRestorer()
    assert "DRBLL" in restorer.skeleton_to_words
    assert "DORABELLA" in restorer.skeleton_to_words["DRBLL"]

    res = restorer.restore_sentence_beam_search("DRBLL", beam_width=5)
    assert len(res) > 0
    assert all(len(phrase) > 0 for score, phrase in res)




