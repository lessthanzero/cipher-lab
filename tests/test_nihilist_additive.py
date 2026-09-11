import pytest
from projects.dagapeyeff.nihilist_additive import (
    add_additive_key,
    coords_to_pairs,
    derive_additive_key_from_keyword,
    pairs_to_coords,
    subtract_additive_key,
)


def test_pairs_and_coords_roundtrip():
    pairs = ["61", "72", "83", "94", "05", "65", "01"]
    coords = pairs_to_coords(pairs)
    assert coords == [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (1, 5), (5, 1)]
    reconstructed = coords_to_pairs(coords)
    assert reconstructed == pairs


def test_derive_additive_key():
    shifts = derive_additive_key_from_keyword("SCHUVALOF")
    assert len(shifts) == 9
    for kr, kc in shifts:
        assert 0 <= kr < 5
        assert 0 <= kc < 5


def test_additive_key_roundtrip():
    coords = [(1, 2), (3, 4), (5, 1), (2, 3), (4, 5)]
    key = [(1, 2), (0, 4), (3, 1)]
    
    enc = add_additive_key(coords, key)
    dec = subtract_additive_key(enc, key)
    assert dec == coords
