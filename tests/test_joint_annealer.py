from projects.dagapeyeff.cartographic_corpus import calculate_cartographic_lexical_bonus
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


def test_cartographic_lexical_bonus():
    # Coherent cartographic string
    carto_str = "ORDNANCESURVEYSHEETNUMBERTENRETRIANGULATION"
    random_str = "QZXJVKWPBFMZQZXJVKWPBFMZ"
    assert calculate_cartographic_lexical_bonus(carto_str) > calculate_cartographic_lexical_bonus(random_str)

    # Nihilist root matches
    nihil_str = "SOMETHINGNIHILISTCIPHER"
    assert calculate_cartographic_lexical_bonus(nihil_str) > 20.0


def test_joint_annealer_additive_key():
    # Test post-transposition additive key
    ann_post = JointDagapeyeffAnnealer(
        grid_mode="14x13_stripped",
        language="english",
        seed_keyword="NIHILIST",
        additive_order="post_transposition",
        initial_additive_keyword="SCHUVALOF",
    )
    assert ann_post.additive_order == "post_transposition"
    assert ann_post.additive_key_period == 9
    best_post = ann_post.run_annealing_chain(duration_secs=0.3)
    assert best_post is not None
    assert len(best_post.candidate_pt) == 182

    # Test pre-transposition additive key
    ann_pre = JointDagapeyeffAnnealer(
        grid_mode="14x14",
        language="english",
        seed_keyword="ORDNANCESURVEY",
        additive_order="pre_transposition",
        additive_key_period=7,
    )
    assert ann_pre.additive_order == "pre_transposition"
    best_pre = ann_pre.run_annealing_chain(duration_secs=0.3)
    assert best_pre is not None
    assert len(best_pre.candidate_pt) == 196
