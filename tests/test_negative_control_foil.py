from cipher_lab.stats import calculate_index_of_coincidence

from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.negative_control_foil import run_pipeline_on_pairs


def test_negative_control_pipeline_execution():
    """Verify that negative control pipeline runs deterministically and computes statistics."""
    raw_196 = get_digit_pairs()
    # Fast 0.5s smoke execution
    res = run_pipeline_on_pairs(raw_196, seed=42, chain_duration=0.5, max_polish_steps=10)
    
    assert res.q_score < 0
    assert res.chi_sq > 0
    assert 0.05 < res.ioc < 0.10
    assert len(res.best_text) == 60
    
    # Check that IoC function matches
    calc_ioc = calculate_index_of_coincidence(res.best_text)
    assert calc_ioc > 0.04
