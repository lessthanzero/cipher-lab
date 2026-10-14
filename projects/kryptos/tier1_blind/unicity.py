"""Shannon Unicity Distance Invariant and Keyspace Gating for Kryptos K4.

Computes Shannon unicity distance U_0 = H(K) / D and evaluates whether a candidate
cipher family is mathematically determined for N = 97 characters.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict


# Redundancy of standard English text (Shannon, 1949): D = log2(26) - 1.5 ~ 3.20 bits/char
ENGLISH_REDUNDANCY_BITS: float = math.log2(26.0) - 1.5  # ~ 3.2004


@dataclass(frozen=True)
class UnicityVerdict:
    model_name: str
    key_entropy_bits: float
    unicity_distance_chars: float
    corpus_length: int
    is_determined: bool
    entropy_ratio: float
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "key_entropy_bits": round(self.key_entropy_bits, 2),
            "unicity_distance_chars": round(self.unicity_distance_chars, 2),
            "corpus_length": self.corpus_length,
            "is_determined": self.is_determined,
            "entropy_ratio": round(self.entropy_ratio, 3),
            "recommendation": self.recommendation,
        }


def compute_unicity_distance(
    key_entropy_bits: float,
    redundancy_bits_per_char: float = ENGLISH_REDUNDANCY_BITS,
) -> float:
    """Calculate Shannon unicity distance U_0 = H(K) / D."""
    if redundancy_bits_per_char <= 0:
        raise ValueError("Redundancy must be strictly positive.")
    return key_entropy_bits / redundancy_bits_per_char


def evaluate_cipher_family_unicity(
    model_name: str,
    key_entropy_bits: float,
    corpus_length: int = 97,
) -> UnicityVerdict:
    """Evaluate whether candidate cipher family satisfies unicity bounds on corpus of length N."""
    u_0 = compute_unicity_distance(key_entropy_bits)
    is_determined = corpus_length >= u_0
    ratio = corpus_length / u_0 if u_0 > 0 else float("inf")

    if is_determined:
        if ratio >= 2.0:
            rec = "ROBUST: Corpus significantly exceeds unicity distance; unique solution mathematically reachable."
        else:
            rec = "MARGINAL: Corpus marginally exceeds unicity distance; false positive solutions are possible."
    else:
        rec = "REJECT / UNDERDETERMINED: Corpus length violates Shannon unicity bound (N < U_0). Refuse unconstrained text generation!"

    return UnicityVerdict(
        model_name=model_name,
        key_entropy_bits=key_entropy_bits,
        unicity_distance_chars=u_0,
        corpus_length=corpus_length,
        is_determined=is_determined,
        entropy_ratio=ratio,
        recommendation=rec,
    )


def audit_scheidt_families(corpus_length: int = 97) -> Dict[str, Any]:
    """Audit unicity limits across Scheidt's candidate cipher families."""
    # Entropy estimations:
    # 1. Periodic Vigenere / Beaufort (period L=7)
    vigenere_l7 = 7.0 * math.log2(26.0)  # ~ 32.9 bits
    # 2. Quagmire III (Keyword L=8, period L=7)
    q3_entropy = 8.0 * math.log2(26.0) + 7.0 * math.log2(26.0)  # ~ 70.5 bits
    # 3. Double Columnar Transposition (widths W1=10, W2=10)
    dct_entropy = math.log2(math.factorial(10)) * 2.0  # ~ 21.8 * 2 = 43.6 bits
    # 4. Compound Quagmire III + Double Columnar
    compound_entropy = q3_entropy + dct_entropy  # ~ 114.1 bits
    # 5. Unconstrained arbitrary substitution + arbitrary transposition (26! * 97!)
    unconstrained_arbitrary = math.log2(math.factorial(26)) + math.log2(math.factorial(97))  # ~ 88.4 + 504 = ~ 592 bits

    models = [
        ("Periodic Vigenère (Period 7)", vigenere_l7),
        ("Quagmire III (Keywords L1=8, L2=7)", q3_entropy),
        ("Double Columnar Transposition (10x10)", dct_entropy),
        ("Compound Quagmire III + Double Transposition", compound_entropy),
        ("Unconstrained Arbitrary Substitution + Transposition", unconstrained_arbitrary),
    ]

    results = [
        evaluate_cipher_family_unicity(name, ent, corpus_length).to_dict()
        for name, ent in models
    ]

    available_budget_bits = corpus_length * ENGLISH_REDUNDANCY_BITS
    return {
        "corpus_length": corpus_length,
        "available_redundancy_budget_bits": round(available_budget_bits, 2),
        "families": results,
    }
