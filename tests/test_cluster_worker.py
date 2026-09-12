"""Unit tests for Cluster Worker module."""

from projects.dagapeyeff.cluster_worker import (
    ClusterTrialResult,
    apply_traversal_on_pairs,
)


def test_cluster_trial_result_dataclass():
    res = ClusterTrialResult(
        trial_id="test_001",
        node_name="test_node",
        worker_id=0,
        keyword_label="HYDROGRAPHICAL",
        traversal="standard",
        direction="standard_encryption",
        order="row_then_col",
        pairing="sequential",
        dual_alphabets=True,
        q_score=-845.0,
        chi_sq=20.0,
        ioc=0.065,
        alphabet1="A" * 25,
        alphabet2="B" * 25,
        plaintext_preview="TEST",
        timestamp=123456.0,
    )
    assert res.q_score == -845.0
    assert res.node_name == "test_node"


def test_apply_traversal_on_pairs():
    pairs = [f"{i:02d}" for i in range(28)]  # 28 pairs = 14x2
    std = apply_traversal_on_pairs(pairs, "standard", width=14)
    assert std == pairs

    cart = apply_traversal_on_pairs(pairs, "cartesian_bottom_up", width=14)
    assert len(cart) == 28
    assert cart != pairs
    assert cart[:14] == pairs[14:]  # Inverted rows

    boust = apply_traversal_on_pairs(pairs, "boustrophedon_horiz", width=14)
    assert len(boust) == 28
    assert boust[:14] == pairs[:14]
    assert boust[14:] == pairs[14:][::-1]  # Inverted second row
