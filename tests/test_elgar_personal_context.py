"""Unit tests for the Elgarian personal context, Pall Mall solver, and MIDI engine."""

from __future__ import annotations

from pathlib import Path

from cipher_lab.stats import QuadgramScorer

from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.dual_musical_engine import DualMusicalCipherEngine
from projects.dorabella.elgar_lexicon import FULL_ELGARIAN_LEXICON, ElgarLexiconScorer
from projects.dorabella.pall_mall_solver import PallMallGrilleSolver


def test_elgar_lexicon_matches() -> None:
    """Verify Elgarian personal vocabulary matching and scoring bonuses."""
    scorer = ElgarLexiconScorer()
    assert len(FULL_ELGARIAN_LEXICON) > 30

    test_sample = "DORABELLAWITHDANATMALVERNAMDGFORLI"
    matches = scorer.find_lexicon_matches(test_sample)
    assert "DORABELLA" in matches
    assert "DAN" in matches
    assert "MALVERN" in matches
    assert "AMDG" in matches
    assert "FORLI" in matches

    score_boosted, matched_words = scorer.score_with_elgar_bonus(test_sample, bonus_per_word=25.0)
    base_score = scorer.base_scorer.score_total(test_sample)
    assert score_boosted > base_score
    assert len(matched_words) >= 5


def test_pall_mall_6letter_polyalphabetic() -> None:
    """Verify Pall Mall 1896 solver executes across 6-letter candidate keywords."""
    scorer = QuadgramScorer(language="english")
    solver = PallMallGrilleSolver(scorer=scorer)

    pt_vig = solver.decrypt_polyalphabetic_period_6(DORABELLA_TOKENS, "EDWARD", mode="vigenere")
    assert len(pt_vig) == 87
    assert all(c.isalpha() for c in pt_vig)

    pt_beau = solver.decrypt_polyalphabetic_period_6(DORABELLA_TOKENS, "ENIGMA", mode="beaufort")
    assert len(pt_beau) == 87

    candidates = solver.evaluate_all_6letter_keywords()
    assert len(candidates) >= 15
    top_cand = candidates[0]
    assert len(top_cand[4]) == 87
    assert isinstance(top_cand[2], float)  # Q score


def test_dual_musical_cipher_midi_generation(tmp_path: Path) -> None:
    """Verify pure-Python MIDI synthesizer writes a valid binary file."""
    engine = DualMusicalCipherEngine()
    melody = engine.extract_melodic_stream(scale="g_major", orientation_offset=0)
    assert len(melody) == 87
    for pitch, duration in melody:
        assert 60 <= pitch <= 85
        assert duration in [480, 240, 120]

    out_midi = tmp_path / "test_dorabella.mid"
    engine.generate_midi_file(
        output_path=out_midi,
        scale="e_minor",
        orientation_offset=2,
        tempo_bpm=108,
    )
    assert out_midi.exists()
    assert out_midi.stat().st_size > 500

    # Verify MIDI header chunk magic bytes: 'MThd'
    with open(out_midi, "rb") as f:
        magic = f.read(4)
        assert magic == b"MThd"
