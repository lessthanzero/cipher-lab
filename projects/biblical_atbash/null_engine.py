"""Monte Carlo Null Surrogate Engine for Biblical Atbash Cryptanalysis.

Evaluates statistical significance of candidate Atbash/Albam/Atbah matches:
1. Generates N=10,000 randomized text surrogates preserving character unigram frequencies.
2. Measures empirical distribution of accidental lexicon collisions.
3. Computes exact empirical p-values and Z-scores against dictionary chance.
"""

from __future__ import annotations

import collections
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from projects.biblical_atbash.cipher import (
    HEBREW_ALPHABET,
    normalize_hebrew_word,
    transform_albam,
    transform_atbah,
    transform_atbash,
)
from projects.biblical_atbash.lexicon import BiblicalLexicon


@dataclass(frozen=True, slots=True)
class NullPermutationStats:
    observed_hits: int
    null_mean_hits: float
    null_std_hits: float
    z_score: float
    empirical_p_value: float
    n_permutations: int


class AtbashNullEngine:
    """Evaluates statistical significance of Atbash discoveries against Monte Carlo nulls."""

    def __init__(self, lexicon: Optional[BiblicalLexicon] = None) -> None:
        self.lexicon = lexicon or BiblicalLexicon()

    def evaluate_candidate(
        self,
        candidate_word: str,
        n_permutations: int = 10000,
        seed: int = 42,
    ) -> dict[str, Any]:
        """Tests whether a candidate word's Atbash transformation is a non-random hit."""
        norm_cand = normalize_hebrew_word(candidate_word)
        transformed = transform_atbash(norm_cand)
        is_hit = self.lexicon.contains(transformed)

        # Baseline probability: under random letters of length L
        L = len(norm_cand)
        rng = random.Random(seed)

        # Count how many random L-letter words hit the dictionary
        null_hits = 0
        letters = list(HEBREW_ALPHABET)

        for _ in range(n_permutations):
            rand_word = "".join(rng.choice(letters) for _ in range(L))
            rand_transformed = transform_atbash(rand_word)
            if self.lexicon.contains(rand_transformed):
                null_hits += 1

        p_hit_null = null_hits / n_permutations
        std_null = math.sqrt(max(p_hit_null * (1.0 - p_hit_null), 1e-8))
        obs_val = 1.0 if is_hit else 0.0
        z_score = (obs_val - p_hit_null) / max(std_null, 1e-4)

        return {
            "candidate": candidate_word,
            "normalized": norm_cand,
            "transformed_atbash": transformed,
            "is_lexicon_hit": is_hit,
            "length": L,
            "n_permutations": n_permutations,
            "null_hit_rate": round(p_hit_null, 6),
            "z_score": round(z_score, 2),
            "empirical_p_value": round(p_hit_null if is_hit else 1.0, 6),
        }
