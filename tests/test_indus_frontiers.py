"""Unit tests for Indus Epigraphic Frontiers (Ledger, Stratigraphy, Spatial Archaeology)."""

import json
from pathlib import Path

import pytest

from projects.indus.pan_analytics import PanIndusAnalyzer
from projects.indus.pan_corpus import PanIndusCorpus
from projects.indus.reader import IndusReader
from projects.indus.spatial_archaeology import SpatialArchaeologyAnalyzer
from projects.indus.stratigraphy import StratigraphyAnalyzer
from projects.indus.transcription_ledger import determine_administrative_typology


@pytest.fixture(scope="module")
def shared_corpus():
    return PanIndusCorpus()


@pytest.fixture(scope="module")
def shared_reader(shared_corpus):
    analyzer = PanIndusAnalyzer(corpus=shared_corpus)
    return IndusReader(corpus=shared_corpus, analyzer=analyzer)


def test_reader_read_inscription(shared_reader, shared_corpus):
    ins = shared_corpus.inscriptions[0]
    reading = shared_reader.read_inscription(ins)
    assert reading is not None
    assert reading.artifact_id == ins.artifact_id
    assert reading.n_clauses >= 1
    assert len(reading.clauses) >= 1


def test_administrative_typology_classification(shared_reader, shared_corpus):
    by_base = {}
    for ins in shared_corpus.inscriptions:
        base = ins.artifact_id.split(".")[0]
        by_base.setdefault(base, []).append(ins)
    multi_bases = {b for b, inss in by_base.items() if len(inss) >= 2}

    # Test an authority seal
    for ins in shared_corpus.inscriptions:
        reading = shared_reader.read_inscription(ins)
        t = determine_administrative_typology(reading, ins, multi_bases)
        assert t in (
            "AUTHORITY_CONSIGNMENT",
            "GUILD_VOUCHER",
            "COMMODITY_TALLY",
            "MULTI_REGISTER_TABLET",
            "CREOLIZED_FOREIGN",
        )


def test_stratigraphy_analysis(shared_corpus):
    analyzer = StratigraphyAnalyzer(corpus=shared_corpus)
    # Quick test of phase metrics
    metrics_3b = analyzer.compute_phase_metrics("Phase 2B", ["TAB:B"])
    metrics_3c = analyzer.compute_phase_metrics("Phase 3", ["TAB:I"])

    assert metrics_3b.sample_size > 500
    assert metrics_3c.sample_size > 400
    # Period 3C compliance must exceed 3B
    assert metrics_3c.compliant_rate > metrics_3b.compliant_rate
    # Period 3C entropy must be lower than 3B
    assert metrics_3c.conditional_entropy_bits < metrics_3b.conditional_entropy_bits


def test_spatial_archaeology_analysis(shared_corpus):
    analyzer = SpatialArchaeologyAnalyzer(corpus=shared_corpus)
    # Test sector classification
    sectors = set()
    for ins in shared_corpus.inscriptions:
        sec = analyzer.classify_sector(ins)
        if sec:
            sectors.add(sec)

    assert "MD_CITADEL_SD" in sectors
    assert "MD_COMMERCIAL_VS" in sectors
    assert "HP_WORKMEN_F" in sectors
    assert "HP_CITADEL_AB" in sectors

    # Verify workmen F tablet dominance
    report = analyzer.generate_full_report(n_permutations=50)
    assert report.sectors["HP_WORKMEN_F"].tablets_pct > 80.0
    assert report.sectors["MD_COMMERCIAL_VS"].unicorn_pct > 85.0
