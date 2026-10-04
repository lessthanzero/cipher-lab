"""Hostile null permutation engines and non-linguistic surrogate generators."""

from __future__ import annotations

import collections
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass(frozen=True, slots=True)
class SignificanceResult:
    observed_metric: float
    null_mean: float
    null_std: float
    z_score: float
    empirical_p_value: float
    cohens_d: float
    ci_95_low: float
    ci_95_high: float
    is_statistically_significant: bool


class NullSurrogateGenerator:
    """Generates hostile null surrogates and computes empirical significance."""

    def __init__(self, sequences: Sequence[Sequence[str]], seed: int = 42) -> None:
        self.sequences = [list(s) for s in sequences]
        self.rng = random.Random(seed)
        
        # Build global sign inventory and frequencies
        self.all_tokens = [s for seq in self.sequences for s in seq]
        self.unique_signs = sorted(list(set(self.all_tokens)))
        self.token_counts = collections.Counter(self.all_tokens)

    def null_uniform(self) -> list[list[str]]:
        """Null Model 1: Uniform random signs sampled with replacement, preserving text lengths."""
        return [
            [self.rng.choice(self.unique_signs) for _ in range(len(seq))]
            for seq in self.sequences
        ]

    def null_frequency_preserving(self) -> list[list[str]]:
        """Null Model 2: Within-sequence order shuffle preserving global unigram frequencies."""
        shuffled = []
        for seq in self.sequences:
            s_copy = list(seq)
            self.rng.shuffle(s_copy)
            shuffled.append(s_copy)
        return shuffled

    def null_positional_marginal_preserving(self) -> list[list[str]]:
        """Null Model 3: Columnar permutation shuffling tokens strictly within positional slots.
        
        Preserves initial/medial/terminal unigram marginals while destroying all horizontal transitions.
        """
        max_len = max(len(s) for s in self.sequences) if self.sequences else 0
        by_pos: dict[int, list[str]] = collections.defaultdict(list)
        for seq in self.sequences:
            for p, sign in enumerate(seq):
                by_pos[p].append(sign)

        # Shuffle each position column independently
        for p in by_pos:
            self.rng.shuffle(by_pos[p])

        # Reconstruct sequences
        pos_ptrs: dict[int, int] = collections.defaultdict(int)
        shuffled: list[list[str]] = []
        for seq in self.sequences:
            new_seq = []
            for p in range(len(seq)):
                idx = pos_ptrs[p]
                new_seq.append(by_pos[p][idx])
                pos_ptrs[p] += 1
            shuffled.append(new_seq)
        return shuffled

    def run_monte_carlo(
        self,
        null_type: str,
        metric_fn: Callable[[list[list[str]]], float],
        n_iterations: int = 1000,
    ) -> list[float]:
        """Run N Monte Carlo surrogate evaluations."""
        generator_fn = {
            "uniform": self.null_uniform,
            "frequency_preserving": self.null_frequency_preserving,
            "positional_preserving": self.null_positional_marginal_preserving,
        }.get(null_type.lower())

        if not generator_fn:
            raise ValueError(f"Unknown null_type: {null_type}")

        metrics = []
        for _ in range(n_iterations):
            surrogate_corpus = generator_fn()
            metrics.append(metric_fn(surrogate_corpus))
        return metrics

    @staticmethod
    def evaluate_significance(
        observed: float,
        null_metrics: Sequence[float],
        alternative: str = "less",
    ) -> SignificanceResult:
        """Compute empirical z-score, p-value, Cohen's d, and 95% bootstrap confidence interval."""
        arr = np.array(null_metrics)
        null_mean = float(np.mean(arr))
        null_std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 1e-6
        if null_std == 0.0:
            null_std = 1e-6

        z = (observed - null_mean) / null_std
        d = z  # Cohen's d against null distribution

        n = len(arr)
        if alternative == "less":
            p = float(np.sum(arr <= observed) + 1) / (n + 1)
        elif alternative == "greater":
            p = float(np.sum(arr >= observed) + 1) / (n + 1)
        else:  # two-sided
            p = float(np.sum(np.abs(arr - null_mean) >= np.abs(observed - null_mean)) + 1) / (n + 1)

        ci_low = float(np.percentile(arr, 2.5))
        ci_high = float(np.percentile(arr, 97.5))
        is_sig = bool(p < 0.001)

        return SignificanceResult(
            observed_metric=round(observed, 4),
            null_mean=round(null_mean, 4),
            null_std=round(null_std, 4),
            z_score=round(z, 2),
            empirical_p_value=round(p, 5),
            cohens_d=round(d, 2),
            ci_95_low=round(ci_low, 4),
            ci_95_high=round(ci_high, 4),
            is_statistically_significant=is_sig,
        )
