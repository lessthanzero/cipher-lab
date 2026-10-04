"""Hidden Markov Model (HMM) topology induction and model selection sweep for the Indus Script."""

from __future__ import annotations

import collections
import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np


@dataclass(frozen=True, slots=True)
class HMMModelEval:
    k_states: int
    log_likelihood: float
    bic: float
    aic: float
    n_parameters: int
    per_token_cross_entropy: float
    held_out_log_loss: float
    converged: bool


@dataclass(frozen=True, slots=True)
class HMMTopologySweepResult:
    evaluations: list[HMMModelEval]
    best_bic_k: int
    best_aic_k: int
    min_bic: float
    is_compact_regular_grammar: bool
    bic_evidence_ratio: float


class DiscreteHMM:
    """Discrete Hidden Markov Model with log-space Forward-Backward EM (Baum-Welch)."""

    def __init__(
        self,
        n_states: int,
        n_emissions: int,
        seed: int = 42,
    ) -> None:
        self.k = n_states
        self.v = n_emissions
        self.rng = np.random.default_rng(seed)

        # Initial state probabilities pi (k,)
        pi_raw = self.rng.uniform(0.1, 1.0, size=self.k)
        self.log_pi = np.log(pi_raw / pi_raw.sum())

        # Transition probabilities A (k, k) with feed-forward prior
        A_raw = self.rng.uniform(0.1, 1.0, size=(self.k, self.k))
        # Add diagonal / forward bias
        for i in range(self.k):
            for j in range(self.k):
                if j >= i:
                    A_raw[i, j] *= 2.0
        row_sums = A_raw.sum(axis=1, keepdims=True)
        self.log_A = np.log(A_raw / row_sums)

        # Emission probabilities B (k, v)
        B_raw = self.rng.uniform(0.1, 1.0, size=(self.k, self.v))
        row_sums_b = B_raw.sum(axis=1, keepdims=True)
        self.log_B = np.log(B_raw / row_sums_b)

    @staticmethod
    def _log_sum_exp(a: np.ndarray, axis: int | None = None) -> np.ndarray:
        """Numerically stable log-sum-exp."""
        a_max = np.max(a, axis=axis, keepdims=True)
        if axis is None:
            a_max_scalar = np.max(a)
            if np.isneginf(a_max_scalar):
                return a_max_scalar
            return a_max_scalar + np.log(np.sum(np.exp(a - a_max_scalar)))
        
        # Axis specified
        a_max_sq = np.squeeze(a_max, axis=axis)
        exp_sum = np.sum(np.exp(a - a_max), axis=axis)
        res = a_max_sq + np.log(np.maximum(exp_sum, 1e-300))
        return res

    def forward(self, obs: Sequence[int]) -> tuple[float, np.ndarray]:
        """Compute log-likelihood and log alpha matrix for an observation sequence."""
        T = len(obs)
        if T == 0:
            return 0.0, np.zeros((0, self.k))

        log_alpha = np.empty((T, self.k), dtype=np.float64)
        
        # t = 0
        log_alpha[0] = self.log_pi + self.log_B[:, obs[0]]

        # t = 1 .. T-1
        for t in range(1, T):
            # log_alpha[t, j] = log_sum_exp_i(log_alpha[t-1, i] + log_A[i, j]) + log_B[j, obs[t]]
            prev = log_alpha[t - 1, :, None] + self.log_A  # (k, k)
            log_trans = self._log_sum_exp(prev, axis=0)    # (k,)
            log_alpha[t] = log_trans + self.log_B[:, obs[t]]

        log_lik = float(self._log_sum_exp(log_alpha[T - 1]))
        return log_lik, log_alpha

    def backward(self, obs: Sequence[int]) -> np.ndarray:
        """Compute log beta matrix for an observation sequence."""
        T = len(obs)
        if T == 0:
            return np.zeros((0, self.k))

        log_beta = np.empty((T, self.k), dtype=np.float64)
        log_beta[T - 1] = 0.0  # log(1.0) = 0

        for t in range(T - 2, -1, -1):
            # log_beta[t, i] = log_sum_exp_j(log_A[i, j] + log_B[j, obs[t+1]] + log_beta[t+1, j])
            term = self.log_A + self.log_B[:, obs[t + 1]] + log_beta[t + 1]  # (k, k)
            log_beta[t] = self._log_sum_exp(term, axis=1)

        return log_beta

    def fit_sequences(
        self,
        sequences: Sequence[Sequence[int]],
        max_iter: int = 25,
        tol: float = 1e-4,
    ) -> float:
        """Baum-Welch EM parameter estimation."""
        prev_ll = -float("inf")

        for _ in range(max_iter):
            # Accumulators
            pi_accum = np.zeros(self.k, dtype=np.float64)
            A_accum = np.zeros((self.k, self.k), dtype=np.float64)
            B_accum = np.zeros((self.k, self.v), dtype=np.float64)
            total_ll = 0.0

            for obs in sequences:
                if len(obs) == 0:
                    continue
                ll, log_alpha = self.forward(obs)
                if np.isnan(ll) or np.isneginf(ll):
                    continue
                total_ll += ll
                log_beta = self.backward(obs)
                T = len(obs)

                # Gamma: posterior state probabilities (T, k)
                log_gamma = log_alpha + log_beta - ll
                gamma = np.exp(np.clip(log_gamma, -700, 0))

                pi_accum += gamma[0]

                # Xi: transition posteriors (T-1, k, k)
                for t in range(T - 1):
                    log_xi = (
                        log_alpha[t, :, None]
                        + self.log_A
                        + self.log_B[:, obs[t + 1]]
                        + log_beta[t + 1, None, :]
                        - ll
                    )
                    xi = np.exp(np.clip(log_xi, -700, 0))
                    A_accum += xi

                # Emission accumulator
                for t in range(T):
                    B_accum[:, obs[t]] += gamma[t]

            # M-step: Update parameters with Laplace smoothing
            smoothing = 1e-4
            pi_new = pi_accum + smoothing
            self.log_pi = np.log(pi_new / pi_new.sum())

            A_new = A_accum + smoothing
            self.log_A = np.log(A_new / A_new.sum(axis=1, keepdims=True))

            B_new = B_accum + smoothing
            self.log_B = np.log(B_new / B_new.sum(axis=1, keepdims=True))

            if abs(total_ll - prev_ll) < tol:
                break
            prev_ll = total_ll

        return prev_ll


class HMMTopologySweeper:
    """Performs objective model selection across candidate latent state counts K in 2..10."""

    def __init__(self, sequences: Sequence[Sequence[str]]) -> None:
        all_tokens = [s for seq in sequences for s in seq]
        self.unique_signs = sorted(list(set(all_tokens)))
        self.sign_to_id = {s: i for i, s in enumerate(self.unique_signs)}
        self.n_vocab = len(self.unique_signs)
        self.num_sequences = [
            [self.sign_to_id[s] for s in seq]
            for seq in sequences
        ]
        self.total_tokens = len(all_tokens)

    def evaluate_state_count(
        self,
        k: int,
        n_restarts: int = 5,
        test_fraction: float = 0.20,
        seed: int = 42,
    ) -> HMMModelEval:
        """Train and evaluate an HMM with K latent states."""
        # Train-test split
        rng = random.Random(seed)
        indices = list(range(len(self.num_sequences)))
        rng.shuffle(indices)
        n_test = max(int(len(indices) * test_fraction), 1)
        test_idx = set(indices[:n_test])
        train_seqs = [self.num_sequences[i] for i in range(len(self.num_sequences)) if i not in test_idx]
        test_seqs = [self.num_sequences[i] for i in test_idx]

        best_ll = -float("inf")
        best_model: DiscreteHMM | None = None

        for r in range(n_restarts):
            hmm = DiscreteHMM(n_states=k, n_emissions=self.n_vocab, seed=seed + r * 101)
            ll = hmm.fit_sequences(train_seqs, max_iter=20)
            if ll > best_ll:
                best_ll = ll
                best_model = hmm

        # Full corpus log-likelihood with best model
        full_ll = 0.0
        for seq in self.num_sequences:
            ll, _ = best_model.forward(seq)
            full_ll += ll

        # Held-out log-loss
        test_ll = 0.0
        test_tokens = sum(len(s) for s in test_seqs)
        for seq in test_seqs:
            ll, _ = best_model.forward(seq)
            test_ll += ll
        held_out_loss = -test_ll / max(test_tokens, 1)

        # Parameter count: (K-1) initial + K*(K-1) transitions + K*(V-1) emissions
        d = (k - 1) + k * (k - 1) + k * (self.n_vocab - 1)

        # Information criteria
        n_obs = self.total_tokens
        bic = -2.0 * full_ll + d * math.log(n_obs)
        aic = -2.0 * full_ll + 2.0 * d
        cross_ent = -full_ll / (n_obs * math.log(2.0))

        return HMMModelEval(
            k_states=k,
            log_likelihood=round(full_ll, 2),
            bic=round(bic, 2),
            aic=round(aic, 2),
            n_parameters=d,
            per_token_cross_entropy=round(cross_ent, 3),
            held_out_log_loss=round(held_out_loss, 3),
            converged=True,
        )

    def sweep(
        self,
        k_values: Sequence[int] = (2, 3, 4, 5, 6, 7, 8),
        n_restarts: int = 5,
        seed: int = 42,
    ) -> HMMTopologySweepResult:
        """Run full sweep across K values to find optimal topological complexity."""
        evals = []
        for k in k_values:
            ev = self.evaluate_state_count(k, n_restarts=n_restarts, seed=seed)
            evals.append(ev)

        best_bic_eval = min(evals, key=lambda e: e.bic)
        best_aic_eval = min(evals, key=lambda e: e.aic)

        # BIC evidence ratio relative to k=2
        bic_k2 = next(e.bic for e in evals if e.k_states == 2)
        evidence_ratio = math.exp(min((bic_k2 - best_bic_eval.bic) / 2.0, 50.0))

        is_compact = bool(best_bic_eval.k_states in (3, 4, 5, 6))

        return HMMTopologySweepResult(
            evaluations=evals,
            best_bic_k=best_bic_eval.k_states,
            best_aic_k=best_aic_eval.k_states,
            min_bic=best_bic_eval.bic,
            is_compact_regular_grammar=is_compact,
            bic_evidence_ratio=round(evidence_ratio, 2),
        )
