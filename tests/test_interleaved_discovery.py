"""Unit tests for Interleaved Discovery module."""

from projects.dagapeyeff.interleaved_discovery_90min import (
    get_all_admiralty_key_configurations,
)


def test_admiralty_key_configurations():
    configs = get_all_admiralty_key_configurations()
    assert len(configs) >= 15
    for label, perm in configs:
        assert len(perm) == 14
        assert sorted(perm) == list(range(14))
