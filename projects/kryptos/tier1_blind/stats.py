"""Tier 1 Blind Structural and Statistical Profiler for Kryptos K4.

Operates purely on the verified 97-character ciphertext without cribs or hints.
"""

from __future__ import annotations

import collections
import math
from typing import Any, Dict, List, Tuple

from cipher_lab.stats import (
    calculate_chi_squared,
    calculate_index_of_coincidence,
    calculate_shannon_entropy,
    kasiski_examination,
)


def calculate_autocorrelation(text: str, max_lag: int = 48) -> List[Dict[str, Any]]:
    """Compute autocorrelation match count and z-score for each lag L in [1..max_lag]."""
    n = len(text)
    results = []
    # In random English text (26 equal letters), match prob = 1/26 ~ 0.03846
    p_match = 1.0 / 26.0

    for lag in range(1, min(max_lag + 1, n)):
        matches = sum(1 for i in range(n - lag) if text[i] == text[i + lag])
        comparisons = n - lag
        expected = comparisons * p_match
        variance = comparisons * p_match * (1.0 - p_match)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0
        z_score = (matches - expected) / std_dev

        results.append({
            "lag": lag,
            "matches": matches,
            "comparisons": comparisons,
            "match_ratio": round(matches / comparisons, 4) if comparisons > 0 else 0.0,
            "z_score": round(z_score, 3),
        })

    return results


def analyze_factorization_constraints(n: int = 97) -> Dict[str, Any]:
    """Analyze mathematical grid factorization constraints for length N."""
    is_prime = True
    if n <= 1:
        is_prime = False
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            is_prime = False
            break

    # Analyze nearby composite dimensions if padding / nulls were stripped
    candidate_nearby_grids = []
    for delta in range(-15, 16):
        n_mod = n + delta
        if n_mod > 0:
            factors = []
            for r in range(2, int(math.isqrt(n_mod)) + 1):
                if n_mod % r == 0:
                    c = n_mod // r
                    factors.append({"rows": r, "cols": c})
                    if r != c:
                        factors.append({"rows": c, "cols": r})
            if factors:
                candidate_nearby_grids.append({
                    "target_len": n_mod,
                    "delta": delta,
                    "interpretation": "padding_stripped" if delta < 0 else ("padding_added" if delta > 0 else "exact"),
                    "rectangles": factors,
                })

    return {
        "length": n,
        "is_prime": is_prime,
        "implication": (
            "Because N=97 is prime, a simple rectangular transposition R x C = 97 is mathematically impossible. "
            "Any transposition MUST be: (1) an incomplete irregular columnar grid, "
            "(2) padded with nulls or stripped of margin padding, or "
            "(3) governed by a physical geometric mask/stencil or variable-step route."
        ),
        "nearby_composite_candidates": candidate_nearby_grids,
    }


def compute_blind_profile(ciphertext: str) -> Dict[str, Any]:
    """Generate complete Tier 1 blind statistical profile for ciphertext."""
    n = len(ciphertext)
    counts = collections.Counter(ciphertext)
    alphabet_size = len(counts)

    ioc = calculate_index_of_coincidence(ciphertext)
    entropy = calculate_shannon_entropy(ciphertext)
    chi2 = calculate_chi_squared(ciphertext)
    autocorr = calculate_autocorrelation(ciphertext, max_lag=48)
    kasiski = kasiski_examination(ciphertext, seq_len=3)
    factor_constraints = analyze_factorization_constraints(n)

    # Find highest autocorrelation peaks
    top_lags = sorted(autocorr, key=lambda x: x["z_score"], reverse=True)[:5]

    return {
        "text_length": n,
        "unique_characters": alphabet_size,
        "character_counts": dict(sorted(counts.items())),
        "index_of_coincidence": round(ioc, 5),
        "natural_english_ioc_reference": 0.0667,
        "random_alphabet_ioc_reference": 0.0385,
        "ioc_interpretation": (
            "Polyalphabetic-like" if ioc < 0.050 else ("Near-Monoalphabetic / Transposition-like" if ioc > 0.060 else "Mixed / Masked")
        ),
        "shannon_entropy_bits": round(entropy, 4),
        "chi_squared_vs_english": round(chi2, 2),
        "autocorrelation_top_lags": top_lags,
        "kasiski_repeated_ngrams": kasiski,
        "factorization_constraints": factor_constraints,
    }
