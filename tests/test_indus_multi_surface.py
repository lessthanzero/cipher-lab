"""Unit tests for Indus Multi-Surface Epigraphic Analyzer."""

import pytest

from projects.indus.multi_surface import MultiSurfaceAnalyzer
from projects.indus.pan_corpus import PanIndusCorpus


@pytest.fixture(scope="module")
def multi_analyzer() -> MultiSurfaceAnalyzer:
    return MultiSurfaceAnalyzer()


def test_multi_surface_indexing(multi_analyzer: MultiSurfaceAnalyzer) -> None:
    artifacts = multi_analyzer.artifacts
    # There are 551 multi-surface artifacts
    assert len(artifacts) == 551

    # Check 3D prism presence
    prisms = multi_analyzer.analyze_3d_prisms()
    assert len(prisms) == 39

    for p in prisms:
        assert p["n_surfaces"] >= 3
        assert len(p["faces"]) >= 3


def test_intra_face_monotonicity(multi_analyzer: MultiSurfaceAnalyzer) -> None:
    report = multi_analyzer.generate_report()
    assert report.total_multi_artifacts == 551
    assert report.total_faces == 1141
    # Intra-face monotonicity should be ~49.7%
    assert 0.45 <= report.intra_face_monotonic_rate <= 0.55


def test_inter_face_reset_elevation(multi_analyzer: MultiSurfaceAnalyzer) -> None:
    report = multi_analyzer.generate_report()
    # Inter-face reset rate is elevated >2x compared to within-line reset rate
    assert report.reset_elevation_ratio >= 2.0
    assert report.inter_face_reset_rate > 0.50
    assert report.within_line_reset_rate < 0.30


def test_terminal_to_initial_enrichment(multi_analyzer: MultiSurfaceAnalyzer) -> None:
    report = multi_analyzer.generate_report()
    # Class 4 -> Class 0 transition enrichment should be >7x
    assert report.terminal_to_initial_enrichment >= 7.0
    assert report.terminal_to_initial_inter_face_rate >= 0.14


def test_concatenated_clausal_coverage(multi_analyzer: MultiSurfaceAnalyzer) -> None:
    report = multi_analyzer.generate_report()
    # Concatenated multi-surface text should be explained by <=3 clauses in >=70% of cases
    assert report.concatenated_three_clause_rate >= 0.70
