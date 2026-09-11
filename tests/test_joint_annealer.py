import pytest
from projects.dagapeyeff.joint_annealer import (
    JointDagapeyeffAnnealer,
    make_polybius_alphabet,
)


def test_make_polybius_alphabet():
    alpha = make_polybius_alphabet("SCHUVALOF")
    assert len(alpha) == 25
    assert len(set(alpha)) == 25
    assert "J" not in alpha
    assert alpha.startswith("SCHUVALOF") or "S" in alpha[:9]


def test_joint_annealer_initialization():
    # Test 14x14 standard
    ann_std = JointDagapeyeffAnnealer(grid_mode="14x14", language="english")
    assert len(ann_std.pairs) == 196
    assert ann_std.width == 14

    # Test 14x13 stripped
    ann_str = JointDagapeyeffAnnealer(grid_mode="14x13_stripped", language="english")
    assert len(ann_str.pairs) == 182
    assert ann_str.width == 13

    # Test pos97 corrected
    ann_p97 = JointDagapeyeffAnnealer(grid_mode="pos97_corrected", language="russian_translit")
    assert len(ann_p97.pairs) == 196
    assert ann_p97.pairs[97] == "75"


def test_joint_annealer_short_chain():
    ann = JointDagapeyeffAnnealer(grid_mode="14x14", language="english", seed=123)
    best_state = ann.run_annealing_chain(duration_secs=0.5, initial_temp=10.0)
    assert best_state is not None
    assert len(best_state.candidate_pt) == 196
    assert best_state.score_q > -3000.0
