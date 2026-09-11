"""Unit tests for Desynchronization Slip & Traverse Attacks."""

import pytest
from projects.dagapeyeff.desync_attack import (
    apply_dropped_pair_slip,
    apply_inserted_pair_slip,
    apply_boustrophedon_traverse,
    apply_diagonal_traverse,
    DesyncAnnealer,
)


def test_dropped_pair_slip_length():
    """Verify dropped slip maintains length by appending fill_pair."""
    pairs = ["75", "62", "82", "85", "91"]
    slipped = apply_dropped_pair_slip(pairs, drop_idx=2, fill_pair="00")
    assert len(slipped) == len(pairs)
    assert slipped[0] == "75"
    assert slipped[1] == "62"
    assert slipped[2] == "85"  # "82" was dropped
    assert slipped[-1] == "00"


def test_boustrophedon_traverse_invertibility():
    """Verify boustrophedon traverse preserves all symbols."""
    pairs = [str(i).zfill(2) for i in range(20)]
    boustro = apply_boustrophedon_traverse(pairs, width=5)
    assert sorted(boustro) == sorted(pairs)
    assert len(boustro) == len(pairs)


def test_desync_annealer_execution():
    """Verify DesyncAnnealer runs and produces valid scores."""
    annealer = DesyncAnnealer(attack_type="boustrophedon", grid_mode="14x13_stripped", seed=42)
    state = annealer.run_desync_chain(duration_secs=0.5)
    assert len(state.candidate_pt) == 182
    assert -1600.0 < state.score_q < 0.0
    assert state.ioc > 0.03
