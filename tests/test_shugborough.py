"""Comprehensive unit and integration test suite for the Shugborough Inscription project."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from projects.shugborough.corpus import (
    SHUGBOROUGH_EPIGRAPHIC_UPPER,
    SHUGBOROUGH_FRAMING,
    SHUGBOROUGH_TEXT,
    get_shugborough_unicity,
    get_token_summary,
)
from projects.shugborough.epigraphy import ShugboroughEpigraphy
from projects.shugborough.information_theory import ShugboroughInformationTheory
from projects.shugborough.initialism_model import (
    LatinLanguageModel,
    ShugboroughInitialismEvaluator,
)
from projects.shugborough.pseudohistory_debunker import ShugboroughPseudohistoryDebunker
from projects.shugborough.runner import ShugboroughExperimentRunner


def test_shugborough_corpus_basic() -> None:
    """Verify primary corpus text, framing characters, and token summary."""
    assert SHUGBOROUGH_TEXT == "OUOSVAVV"
    assert len(SHUGBOROUGH_TEXT) == 8
    assert SHUGBOROUGH_FRAMING == ("D", "M")
    assert SHUGBOROUGH_EPIGRAPHIC_UPPER == "O·U·O·S·V·A·V·V"

    summary = get_token_summary()
    assert summary["length_upper"] == 8
    assert summary["length_total"] == 10
    assert summary["interpuncts_present"] is True
    assert summary["u_v_distinction_observed"] is True


def test_shugborough_unicity_distance() -> None:
    """Verify that the inscription violates Shannon unicity distance (underdetermined)."""
    unicity = get_shugborough_unicity()
    assert unicity.is_underdetermined is True
    assert unicity.payload_length == 8
    # Unicity distance for 26-letter substitution must be >= 25 chars
    assert unicity.unicity_distance_chars >= 25.0


def test_information_theory_entropy_profile() -> None:
    """Verify detailed entropy metrics and mathematical guarantees."""
    profile = ShugboroughInformationTheory.get_entropy_profile()
    assert profile.length_n == 8
    assert profile.alphabet_size == 26
    # 8 characters, some repeated (O appears twice, V appears three times)
    assert 2.0 < profile.shannon_entropy_bits_per_symbol < 3.0
    assert profile.unicity_monoalphabetic_chars > 25.0
    assert profile.is_unicity_satisfied is False

    guarantees = ShugboroughInformationTheory.evaluate_mathematical_guarantees()
    assert "FALSE" in guarantees["verdict"]
    assert "Epistemic abstention is mandatory" in guarantees["epistemic_mandate"]


def test_epigraphic_stone_properties() -> None:
    """Verify codicological stone examination: Scheemakers, interpuncts, U vs V, Dis Manibus."""
    profile = ShugboroughEpigraphy.get_canonical_profile()
    assert profile.sculptor == "Peter Scheemakers (1691–1781)"
    assert "Thomas Anson" in profile.commissioner
    assert profile.is_initialism_confirmed_by_interpuncts is True
    assert profile.is_artwork_mirrored is True
    assert "Dis Manibus" in profile.funerary_dedication

    upper = profile.upper_line_tokens
    assert len(upper) == 8

    # Letter 2 must be rounded vocalic U
    assert upper[1].char == "U"
    assert upper[1].is_vocalic_u is True

    # Letters 5, 7, 8 must be sharp pointed V
    assert upper[4].char == "V"
    assert upper[4].is_vocalic_u is False
    assert upper[6].char == "V"
    assert upper[7].char == "V"

    # All upper letters must have separating interpunct dots
    for l in upper:
        assert l.has_interpunct_after is True


def test_epigraphic_letterform_validation() -> None:
    """Verify candidate words check against O-U-O-S-V-A-V-V."""
    valid_phrase = [
        "Optimae", "Uxoris", "Optimi", "Sodalis",
        "Viri", "Annae", "Venables", "Vernon"
    ]
    is_valid, errors = ShugboroughEpigraphy.validate_letterform_constraints(valid_phrase)
    assert is_valid is True
    assert len(errors) == 0

    # Test invalid length
    is_valid, errors = ShugboroughEpigraphy.validate_letterform_constraints(["Optimae", "Uxoris"])
    assert is_valid is False
    assert "Expected 8 words" in errors[0]

    # Test mismatch at position 1 (Expect O, got A)
    bad_phrase = [
        "Amantissimae", "Uxoris", "Optimi", "Sodalis",
        "Viri", "Annae", "Venables", "Vernon"
    ]
    is_valid, errors = ShugboroughEpigraphy.validate_letterform_constraints(bad_phrase)
    assert is_valid is False
    assert any("Position 1: Expected initial 'O'" in err for err in errors)


def test_bayesian_latin_language_model() -> None:
    """Verify Latin language model loads vocabulary and scores transitions."""
    lm = LatinLanguageModel()
    assert lm.vocab_size > 1000
    assert lm.total_words > 10000

    # Common Latin transition should have higher probability than random nonsense
    lp_common = lm.get_bigram_log_prob("dis", "manibus")
    lp_rare = lm.get_bigram_log_prob("dis", "zephyro")
    assert lp_common > lp_rare

    joint_lp, mean_trans = lm.score_phrase(["dis", "manibus", "sacrum"])
    assert joint_lp < 0.0
    assert mean_trans < 0.0


def test_initialism_evaluator_candidates() -> None:
    """Verify that all major published initialism candidates are ranked and evaluated."""
    evaluator = ShugboroughInitialismEvaluator()
    evals = evaluator.evaluate_all()
    assert len(evals) >= 6

    # Verify key hypotheses exist in evaluation
    cand_ids = {e.candidate_id for e in evals}
    assert "mitchell_antigone_2022" in cand_ids
    assert "stonor_lawn_1951" in cand_ids
    assert "massey_2014" in cand_ids
    assert "regimbal_2005" in cand_ids

    # Find Mitchell / Antigone candidate
    mitchell = next(e for e in evals if e.candidate_id == "mitchell_antigone_2022")
    assert mitchell.epigraphic_u_v_concord is True
    assert "Leading Historical/Epigraphic Candidate" in mitchell.verdict
    assert "Dis Manibus universally governs" in mitchell.dis_manibus_compatibility

    # Find Stonor candidate (must note biographical falsification: no widower in Anson family)
    stonor = next(e for e in evals if e.candidate_id == "stonor_lawn_1951")
    assert "Biographically Falsified" in stonor.verdict


def test_polyalphabetic_triviality_proof() -> None:
    """Verify Shannon perfect secrecy proof: any 8-letter word can be generated."""
    debunker = ShugboroughPseudohistoryDebunker()

    proof_magdalen = debunker.prove_polyalphabetic_triviality("MAGDALEN")
    assert proof_magdalen.derived_vigenere_key == "CUIPVPRI"
    assert "Shannon's Perfect Secrecy theorem" in proof_magdalen.mathematical_implication

    # Test that an arbitrary word produces an exact key
    proof_arbitrary = debunker.prove_polyalphabetic_triviality("CLEOPATR")
    assert len(proof_arbitrary.derived_vigenere_key) == 8

    # Verify decrypting OUOSVAVV with derived key reproduces target
    c_text = "OUOSVAVV"
    k_text = proof_arbitrary.derived_vigenere_key
    decrypted = []
    for c, k in zip(c_text, k_text):
        p_val = ((ord(c) - ord("A")) - (ord(k) - ord("A"))) % 26
        decrypted.append(chr(p_val + ord("A")))
    assert "".join(decrypted) == "CLEOPATR"


def test_geometric_pareidolia_and_treasure_falsification() -> None:
    """Verify Ramsey theory calculations and treasure coordinate falsification."""
    debunker = ShugboroughPseudohistoryDebunker()

    geom = debunker.evaluate_geometric_pareidolia(num_salient_points=40)
    assert geom["possible_lines"] == 780 if "possible_lines" in geom else geom["possible_connecting_lines"] == 780
    assert geom["possible_triangles"] == 9880
    assert "inevitable mathematical certainty" in geom["ramsey_verdict"]

    treasure = debunker.evaluate_anson_treasure_coordinates()
    assert treasure["verdict"] == "REJECTED (Unfalsifiable degrees-of-freedom overfitting)"


def test_shugborough_experiment_runner(tmp_path: Path) -> None:
    """Verify end-to-end campaign execution and trial logging to DuckDB and JSONL."""
    test_db = tmp_path / "test_shugborough.duckdb"
    test_jsonl = tmp_path / "test_shugborough.jsonl"

    runner = ShugboroughExperimentRunner(db_path=test_db, jsonl_path=test_jsonl)
    results = runner.run_full_campaign()

    assert test_db.exists()
    assert test_jsonl.exists()
    assert len(results["candidates"]) >= 6

    # Verify records in DuckDB
    import duckdb
    con = duckdb.connect(str(test_db))
    rows = con.execute("SELECT trial_id, modality, verdict FROM shugborough_trials").fetchall()
    con.close()

    assert len(rows) >= 8
    trial_ids = {r[0] for r in rows}
    assert "shugborough_info_theory_baseline" in trial_ids
    assert "shugborough_epigraphic_stone_audit" in trial_ids
    assert "debunk_polyalphabetic_magdalen" in trial_ids
