from pathlib import Path

from cipher_lab.loop import CipherDiscoveryLoop

from projects.dagapeyeff.corpus import (
    get_digit_pairs,
    get_pair_frequencies,
    get_payload_digits,
    get_raw_digits,
    verify_pair_structure,
)
from projects.dagapeyeff.kerckhoffs import KerckhoffsEngine


def test_dagapeyeff_corpus_integrity():
    raw = get_raw_digits()
    assert len(raw) == 395
    payload = get_payload_digits()
    assert len(payload) == 392
    pairs = get_digit_pairs()
    assert len(pairs) == 196
    
    struct_info = verify_pair_structure()
    assert struct_info["valid_pct"] == 100.0
    
    freqs = get_pair_frequencies()
    assert freqs["81"] == 20  # Dominant pair 81 appears exactly 20 times (Marland finding 4)
    assert len(freqs) == 18   # Exactly 18 unique pairs exist in ciphertext


def test_dagapeyeff_discovery_loop(tmp_path: Path):
    engine = KerckhoffsEngine()
    pairs = get_digit_pairs()
    pt = engine.decode_pair_stream(pairs)
    assert len(pt) == 196

    loop = CipherDiscoveryLoop(
        artifact_id="test_dagapeyeff",
        ciphertext=get_payload_digits(),
        alphabet_size=25,
        key_space_bits=84.0,
        historical_context="1939 British textbook challenge",
        data_dir=tmp_path,
        time_budget_secs=10.0,
    )
    
    eval_res = loop.evaluate_candidate(
        hypothesis_name="H0_test_polybius",
        key_class="fractionation",
        key_desc="Standard Polybius 5x5",
        candidate_pt=pt,
    )
    
    assert eval_res.candidate_id is not None
    assert eval_res.passed_unicity_gate is True
    assert eval_res.is_statistically_viable is False
    
    summary = loop.ledger.get_summary_statistics("test_dagapeyeff")
    assert summary["total_trials_denominator"] == 1
