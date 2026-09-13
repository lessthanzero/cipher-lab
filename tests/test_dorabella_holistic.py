"""Unit and epistemic tests for the Dorabella holistic investigation."""

from __future__ import annotations

from pathlib import Path

from cipher_lab.stats import QuadgramScorer

from projects.dorabella.cluster_worker import run_surrogate_monte_carlo
from projects.dorabella.corpus import (
    DORABELLA_TOKENS,
    DOT_LOCATION,
    LINE_1_TOKENS,
    LINE_2_TOKENS,
    LINE_3_TOKENS,
    LINE_PARTITIONS,
)
from projects.dorabella.holistic import HolisticDorabellaContext
from projects.dorabella.musical_cipher import MusicalCipherEvaluator
from projects.dorabella.symbols import (
    get_hump_distribution,
    get_orientation_distribution,
)
from projects.dorabella.tachygraphy import TachygraphicEvaluator
from projects.dorabella.transposition_solver import DorabellaTranspositionSolver


def test_dorabella_holistic_context() -> None:
    """Verify holistic knowledge base initializes and exposes all 5 multi-disciplinary domains."""
    holistic = HolisticDorabellaContext()
    summary = holistic.get_summary()
    assert "History" in summary
    assert "Bibliography" in summary
    assert "Geography" in summary
    assert "Biology" in summary
    assert "Politics" in summary

    assert "Dan the bulldog" in summary["Biology"]
    assert "The Ark" in summary["Biology"]
    assert "Malvern" in summary["Geography"]
    assert "Wase" in summary["Bibliography"]

    cribs = holistic.get_lexicon_cribs()
    assert len(cribs) > 15
    assert "DORABELLA" in cribs
    assert "BULLDOG" in cribs
    assert "ARK" in cribs


def test_dorabella_authentic_consensus() -> None:
    """Verify authentic cross-scholar consensus transcription properties."""
    from cipher_lab.stats import calculate_index_of_coincidence
    from projects.dorabella.corpus import DORABELLA_AUTHENTIC_CONSENSUS

    assert len(DORABELLA_AUTHENTIC_CONSENSUS) == 87
    distinct = set(DORABELLA_AUTHENTIC_CONSENSUS)
    assert len(distinct) == 20
    ioc = calculate_index_of_coincidence(DORABELLA_AUTHENTIC_CONSENSUS)
    # Authentic consensus text sits within natural English range (0.055 to 0.065)
    assert 0.055 <= ioc <= 0.065


def test_dorabella_canonical_line_partitions() -> None:
    """Verify authentic 3 physical lines: 24, 33, 30 symbols, total 87."""
    assert len(LINE_1_TOKENS) == 24
    assert len(LINE_2_TOKENS) == 33
    assert len(LINE_3_TOKENS) == 30
    assert len(DORABELLA_TOKENS) == 87
    assert len(LINE_PARTITIONS) == 3
    assert DOT_LOCATION == (3, 5)


def test_dorabella_physical_distributions() -> None:
    """Verify hump counts and orientation frequencies."""
    humps = get_hump_distribution()
    assert sum(humps.values()) == 87
    assert humps[1] > 0 and humps[2] > 0 and humps[3] > 0

    oris = get_orientation_distribution()
    assert sum(oris.values()) == 87
    assert len(oris) == 8


def test_dorabella_musical_cipher() -> None:
    """Verify melodic contour evaluator runs and produces valid voice-leading scores."""
    evaluator = MusicalCipherEvaluator()
    best_root, best_score, note_names = evaluator.search_optimal_tonal_alignment()
    assert 0 <= best_root < 8
    assert isinstance(best_score, float)
    assert len(note_names) == 87
    flutter = evaluator.compute_rhythmic_flutter_correlation()
    assert flutter >= 0.0


def test_dorabella_tachygraphy() -> None:
    """Verify Taylor and Pitman shorthand decoders execute cleanly."""
    scorer = QuadgramScorer(language="english")
    evaluator = TachygraphicEvaluator(scorer=scorer)
    results = evaluator.evaluate_tachygraphic_hypotheses()
    assert "H_shorthand_taylor" in results
    assert "H_shorthand_pitman" in results
    for hyp, (q, ioc, text) in results.items():
        assert len(text) > 0
        assert isinstance(q, float)
        assert isinstance(ioc, float)


def test_dorabella_transposition() -> None:
    """Verify matrix 3x29, boustrophedon, and keyword columnar transpositions."""
    solver = DorabellaTranspositionSolver()
    vert = solver.vertical_columnar_read_3x29()
    assert len(vert) == 87
    assert set(vert) == set(DORABELLA_TOKENS)

    boust = solver.boustrophedon_read()
    assert len(boust) == 87

    kw_trans = solver.columnar_keyword_transposition("MALVERN")
    assert len(kw_trans) == 87


def test_dorabella_cluster_worker_fast(tmp_path: Path) -> None:
    """Verify batch Monte Carlo null surrogate generator executes cleanly."""
    out_file = tmp_path / "test_null_surrogates.json"
    summary = run_surrogate_monte_carlo(
        num_surrogates=5,
        anneal_duration_secs=0.1,
        seed=101,
        output_path=out_file,
    )
    assert summary["num_surrogates"] == 5
    assert "q_null_mean" in summary
    assert out_file.exists()
