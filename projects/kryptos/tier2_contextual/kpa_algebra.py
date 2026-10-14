"""Tier 2 Known-Plaintext Attack (KPA) Algebraic Solver for Kryptos K4.

Solves the exact algebraic equations C[i] <-> P[i] across the 24 confirmed public crib
characters:
  - Slice [21:34] (13 chars): C = FLRVQQPRNGKSS <-> P = EASTNORTHEAST
  - Slice [63:74] (11 chars): C = NYPVTTMZFPK <-> P = BERLINCLOCK
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.manifests import CONTEXTUAL_PATH, load_dataset


STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


@dataclass(frozen=True)
class KeystreamPoint:
    index: int
    cipher_char: str
    plain_char: str
    key_shift: int
    key_char: str


@dataclass(frozen=True)
class PeriodConsistencyResult:
    period: int
    is_consistent: bool
    num_tested_residues: int
    num_conflicts: int
    partial_key: str
    conflicting_indices: List[Tuple[int, int]]


def extract_known_pairs() -> List[Tuple[int, str, str]]:
    """Load confirmed cribs and return list of (0-based index, cipher_char, plain_char)."""
    dataset = load_dataset(CONTEXTUAL_PATH, current_tier=2)
    pairs: List[Tuple[int, str, str]] = []
    for crib in dataset["verified_cribs"]:
        start = crib["indices_0_based"]["start"]
        c_text = crib["ciphertext_slice"]
        p_text = crib["plaintext"]
        for offset, (c, p) in enumerate(zip(c_text, p_text)):
            pairs.append((start + offset, c, p))
    return sorted(pairs, key=lambda x: x[0])


def derive_keystream(
    pairs: List[Tuple[int, str, str]],
    alphabet: str = STANDARD_ALPHABET,
    cipher_type: str = "vigenere",
) -> List[KeystreamPoint]:
    """Derive keystream points under specified classical cipher model and alphabet."""
    m = len(alphabet)
    points: List[KeystreamPoint] = []

    for idx, c, p in pairs:
        c_val = alphabet.index(c)
        p_val = alphabet.index(p)

        if cipher_type == "vigenere":
            # C = (P + K) mod M => K = (C - P) mod M
            k_val = (c_val - p_val) % m
        elif cipher_type == "beaufort":
            # C = (K - P) mod M => K = (C + P) mod M
            k_val = (c_val + p_val) % m
        elif cipher_type == "variant_beaufort":
            # C = (P - K) mod M => K = (P - C) mod M
            k_val = (p_val - c_val) % m
        else:
            raise ValueError(f"Unsupported cipher type: {cipher_type}")

        k_char = alphabet[k_val]
        points.append(KeystreamPoint(
            index=idx,
            cipher_char=c,
            plain_char=p,
            key_shift=k_val,
            key_char=k_char,
        ))

    return points


def check_period_consistency(
    points: List[KeystreamPoint],
    period: int,
    alphabet: str = STANDARD_ALPHABET,
) -> PeriodConsistencyResult:
    """Test whether derived keystream points are consistent with a periodic key of length L."""
    residues: Dict[int, Tuple[int, KeystreamPoint]] = {}
    conflicts: List[Tuple[int, int]] = []

    for pt in points:
        rem = pt.index % period
        if rem in residues:
            prev_shift, prev_pt = residues[rem]
            if prev_shift != pt.key_shift:
                conflicts.append((prev_pt.index, pt.index))
        else:
            residues[rem] = (pt.key_shift, pt)

    is_consistent = len(conflicts) == 0

    # Build partial key string for length L
    key_chars = []
    for r in range(period):
        if r in residues:
            key_chars.append(alphabet[residues[r][0]])
        else:
            key_chars.append("?")
    partial_key = "".join(key_chars)

    return PeriodConsistencyResult(
        period=period,
        is_consistent=is_consistent,
        num_tested_residues=len(residues),
        num_conflicts=len(conflicts),
        partial_key=partial_key,
        conflicting_indices=conflicts,
    )


def sweep_periods(
    max_period: int = 26,
    alphabet: str = STANDARD_ALPHABET,
    cipher_type: str = "vigenere",
) -> List[PeriodConsistencyResult]:
    """Test all periods 2..max_period for algebraic consistency."""
    pairs = extract_known_pairs()
    points = derive_keystream(pairs, alphabet=alphabet, cipher_type=cipher_type)
    results = [
        check_period_consistency(points, p, alphabet=alphabet)
        for p in range(2, max_period + 1)
    ]
    return results


def run_kpa_algebra_audit() -> Dict[str, Any]:
    """Audit KPA consistency across Vigenere, Beaufort, Variant Beaufort, and Kryptos tableau."""
    configurations = [
        ("Vigenère (Standard Alphabet)", STANDARD_ALPHABET, "vigenere"),
        ("Beaufort (Standard Alphabet)", STANDARD_ALPHABET, "beaufort"),
        ("Variant Beaufort (Standard Alphabet)", STANDARD_ALPHABET, "variant_beaufort"),
        ("Quagmire III / Vigenère (Kryptos Tableau)", KRYPTOS_ALPHABET, "vigenere"),
        ("Beaufort (Kryptos Tableau)", KRYPTOS_ALPHABET, "beaufort"),
    ]

    report: Dict[str, Any] = {}
    for name, alph, c_type in configurations:
        sweep = sweep_periods(max_period=26, alphabet=alph, cipher_type=c_type)
        consistent_periods = [res for res in sweep if res.is_consistent]
        report[name] = {
            "tested_periods": len(sweep),
            "consistent_periods_count": len(consistent_periods),
            "consistent_periods": [
                {"period": res.period, "partial_key": res.partial_key, "conflicts": res.num_conflicts}
                for res in consistent_periods
            ],
            "min_conflict_period": min(sweep, key=lambda x: x.num_conflicts).period,
            "min_conflicts": min(sweep, key=lambda x: x.num_conflicts).num_conflicts,
        }

    return report


if __name__ == "__main__":
    rep = run_kpa_algebra_audit()
    print("=" * 70)
    print("CIPHERLAB — TIER 2 KPA ALGEBRAIC CONSISTENCY AUDIT")
    print("=" * 70)
    for model_name, data in rep.items():
        print(f"\nModel: {model_name}")
        print(f"  Consistent Periods Found: {data['consistent_periods_count']}")
        if data['consistent_periods']:
            for cp in data['consistent_periods']:
                print(f"    -> Period {cp['period']:2d}: Key Pattern '{cp['partial_key']}'")
        else:
            print(f"    -> ZERO consistent periods in range [2..26].")
            print(f"    -> Lowest conflicts at Period {data['min_conflict_period']} ({data['min_conflicts']} conflicts).")
    print("=" * 70)
