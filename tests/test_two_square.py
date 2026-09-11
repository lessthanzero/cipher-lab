"""Unit tests for Two-Square Engine and Optimizer."""

import pytest
from projects.dagapeyeff.two_square import (
    TwoSquareEngine,
    pairs_to_coordinates,
    coordinates_to_pairs,
)
from projects.dagapeyeff.two_square_annealer import TwoSquareAnnealer


def test_two_square_vertical_round_trip():
    """Verify exact round-trip encryption and decryption in vertical orientation."""
    engine = TwoSquareEngine(
        alphabet1="ABCDEFGHIKLMNOPQRSTUVWXYZ",
        alphabet2="ZYXWVUTSRQPONMLKIHGFEDCBA",
        orientation="vertical",
    )
    plaintext = "COMMUNICATIONSSECRET"
    ciphertext, coords = engine.encipher_plaintext(plaintext)
    decrypted = engine.decipher_coordinates(coords)
    assert decrypted == plaintext
    assert len(ciphertext) == len(plaintext)


def test_two_square_horizontal_round_trip():
    """Verify exact round-trip encryption and decryption in horizontal orientation."""
    engine = TwoSquareEngine(
        alphabet1="ABCDEFGHIKLMNOPQRSTUVWXYZ",
        alphabet2="ZYXWVUTSRQPONMLKIHGFEDCBA",
        orientation="horizontal",
    )
    plaintext = "ORDNANCESURVEYMAPS"
    ciphertext, coords = engine.encipher_plaintext(plaintext)
    decrypted = engine.decipher_coordinates(coords)
    assert decrypted == plaintext


def test_pairs_to_coordinates_fidelity():
    """Verify string pairs convert to 0..4 coordinates and back."""
    pairs = ["75", "62", "82", "85", "91", "04"]
    coords = pairs_to_coordinates(pairs)
    assert len(coords) == 6
    # 75 -> row 7 (index 1), col 5 (index 4)
    assert coords[0] == (1, 4)
    # 04 -> row 0 (index 4), col 4 (index 3)
    assert coords[5] == (4, 3)

    reconstructed = coordinates_to_pairs(coords)
    assert reconstructed == pairs


def test_two_square_annealer_execution():
    """Verify TwoSquareAnnealer runs and produces valid scores and competition evaluation."""
    annealer = TwoSquareAnnealer(
        grid_mode="14x14",
        orientation="vertical",
        dual_alphabets=True,
        pairing_mode="sequential",
        seed=42,
    )
    state = annealer.anneal(max_iterations=1000)
    assert len(state.candidate_pt) == 196
    assert -1500.0 < state.score_q < 0.0
    assert state.competition_eval["scored_all_196_positions"] is True
    assert "delta_q" in state.competition_eval
    assert state.ioc > 0.03


def test_two_square_grid_mode_14x13():
    """Verify TwoSquareAnnealer supports 14x13 stripped mode."""
    annealer = TwoSquareAnnealer(
        grid_mode="14x13_stripped",
        orientation="vertical",
        dual_alphabets=False,
        pairing_mode="sequential",
        seed=99,
    )
    state = annealer.anneal(max_iterations=1000)
    assert len(state.candidate_pt) == 182
    assert -1500.0 < state.score_q < 0.0


def test_two_square_diagonal_pelling_182():
    """Verify TwoSquareAnnealer supports diagonal_pelling_182 mode."""
    annealer = TwoSquareAnnealer(
        grid_mode="diagonal_pelling_182",
        orientation="vertical",
        dual_alphabets=True,
        pairing_mode="sequential",
        seed=101,
    )
    state = annealer.anneal(max_iterations=1000)
    assert len(state.candidate_pt) == 182
    assert -1500.0 < state.score_q < 0.0
    assert "04" not in annealer.pairs
