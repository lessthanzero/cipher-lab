"""Information-theoretic and statistical discrimination metrics for the Indus script.

Computes positional entropy, sign repetition suppression, conditional block entropy,
and Shannon unicity distance bounds.
"""

from __future__ import annotations

import collections
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Counter, Dict, List, Tuple

import numpy as np
from scipy import stats as sp_stats


@dataclass(frozen=True, slots=True)
class PositionalEntropyProfile:
    position_entropies: dict[int, float]
    mean_position_entropy: float
    friedman_chi2: float
    friedman_p_value: float
    is_slot_rigid: bool


@dataclass(frozen=True, slots=True)
class RepetitionMetrics:
    total_inscriptions: int
    inscriptions_with_repetition: int
    repetition_rate: float
    total_tokens: int
    repeated_token_count: int
    token_repetition_rate: float
    is_suppression_significant: bool


@dataclass(frozen=True, slots=True)
class ConditionalEntropyProfile:
    order_0_entropy: float  # H(X)
    order_1_entropy: float  # H(X2 | X1)
    order_2_entropy: float  # H(X3 | X1, X2)
    conditional_drop_ratio: float  # H1 / H0


@dataclass(frozen=True, slots=True)
class UnicityProfile:
    signary_size: int
    mean_message_length: float
    max_message_length: int
    unigram_entropy: float
    max_theoretical_entropy: float
    redundancy_rate: float
    redundancy_bits_per_symbol: float
    estimated_key_equivocation_bits: float
    unicity_distance_tokens: float
    is_underdetermined: bool
    combinatorial_capacity: float


def calculate_shannon_entropy(tokens: Sequence[str]) -> float:
    """Calculate base-2 Shannon entropy H(X) in bits per symbol."""
    n = len(tokens)
    if n == 0:
        return 0.0
    counts = collections.Counter(tokens)
    ent = 0.0
    for c in counts.values():
        p = c / n
        ent -= p * math.log2(p)
    return ent


def calculate_positional_entropy(
    sequences: Sequence[Sequence[str]],
    max_position: int = 7,
) -> PositionalEntropyProfile:
    """Calculate empirical Shannon entropy per positional slot and test variance across positions.
    
    Registration codes and cargo-tags feature 'constrained edges' (e.g., initial issuer emblem,
    terminal jar sign) and 'diverse middles' (commodity/measure slots). Natural languages feature
    more diffuse entropy profiles across word positions.
    """
    pos_tokens: dict[int, list[str]] = collections.defaultdict(list)
    for seq in sequences:
        for pos, sign in enumerate(seq[:max_position]):
            pos_tokens[pos].append(sign)

    pos_entropies: dict[int, float] = {}
    valid_positions = sorted(p for p in pos_tokens.keys() if len(pos_tokens[p]) >= 10)

    for p in valid_positions:
        pos_entropies[p] = calculate_shannon_entropy(pos_tokens[p])

    # Non-parametric Friedman test across positions for fixed-length subset
    # Construct a matrix of sign frequency ranks for inscriptions having at least 4 positions
    fixed_len_seqs = [seq for seq in sequences if len(seq) >= 4]
    if len(fixed_len_seqs) >= 15:
        # Collect signs at positions 0, 1, 2, 3
        # Rank by overall corpus frequency
        global_counts = collections.Counter()
        for s in sequences:
            global_counts.update(s)
        
        matrix = []
        for seq in fixed_len_seqs:
            row = [global_counts.get(seq[p], 0) for p in range(4)]
            matrix.append(row)
        
        try:
            mat_np = np.array(matrix)
            friedman_stat, friedman_p = sp_stats.friedmanchisquare(
                mat_np[:, 0], mat_np[:, 1], mat_np[:, 2], mat_np[:, 3]
            )
        except Exception:
            friedman_stat, friedman_p = 0.0, 1.0
    else:
        friedman_stat, friedman_p = 0.0, 1.0

    mean_ent = float(np.mean(list(pos_entropies.values()))) if pos_entropies else 0.0
    is_rigid = bool(friedman_p < 0.01)

    return PositionalEntropyProfile(
        position_entropies={p: round(pos_entropies[p], 3) for p in valid_positions},
        mean_position_entropy=round(mean_ent, 3),
        friedman_chi2=round(float(friedman_stat), 2),
        friedman_p_value=float(friedman_p),
        is_slot_rigid=is_rigid,
    )


def calculate_repetition_metrics(
    sequences: Sequence[Sequence[str]],
) -> RepetitionMetrics:
    """Measure internal sign repetition suppression (The Farmer-Sproat Invariant).
    
    Logosyllabic scripts (Egyptian, Mayan, Linear B) exhibit high repetition rates (~15-30%)
    due to phonetic doubling and grammatical affixes. Non-linguistic cargo tags suppress
    repetition within short sequences (<3%).
    """
    total_texts = len(sequences)
    if total_texts == 0:
        return RepetitionMetrics(0, 0, 0.0, 0, 0, 0.0, False)

    texts_with_rep = 0
    total_tokens = 0
    repeated_tokens = 0

    for seq in sequences:
        n = len(seq)
        total_tokens += n
        counts = collections.Counter(seq)
        has_rep = any(c > 1 for c in counts.values())
        if has_rep:
            texts_with_rep += 1
            for c in counts.values():
                if c > 1:
                    repeated_tokens += (c - 1)

    rep_rate = texts_with_rep / total_texts
    token_rep_rate = repeated_tokens / max(total_tokens, 1)

    # Binomial test against expected linguistic baseline of 15% repetition
    baseline_expected = 0.15
    binom_res = sp_stats.binomtest(texts_with_rep, total_texts, baseline_expected, alternative="less")
    is_suppressed = bool(binom_res.pvalue < 0.001)

    return RepetitionMetrics(
        total_inscriptions=total_texts,
        inscriptions_with_repetition=texts_with_rep,
        repetition_rate=round(rep_rate, 4),
        total_tokens=total_tokens,
        repeated_token_count=repeated_tokens,
        token_repetition_rate=round(token_rep_rate, 4),
        is_suppression_significant=is_suppressed,
    )


def calculate_conditional_block_entropy(
    sequences: Sequence[Sequence[str]],
) -> ConditionalEntropyProfile:
    """Calculate 0-order, 1st-order, and 2nd-order conditional block entropy in bits.
    
    H0 = H(X)
    H1 = H(X2 | X1) = H(X1, X2) - H(X1)
    H2 = H(X3 | X1, X2) = H(X1, X2, X3) - H(X1, X2)
    """
    unigram_counts: Counter[str] = collections.Counter()
    bigram_counts: Counter[tuple[str, str]] = collections.Counter()
    trigram_counts: Counter[tuple[str, str, str]] = collections.Counter()

    for seq in sequences:
        for sign in seq:
            unigram_counts[sign] += 1
        for i in range(len(seq) - 1):
            bigram_counts[(seq[i], seq[i + 1])] += 1
        for i in range(len(seq) - 2):
            trigram_counts[(seq[i], seq[i + 1], seq[i + 2])] += 1

    total_unigrams = sum(unigram_counts.values())
    total_bigrams = sum(bigram_counts.values())
    total_trigrams = sum(trigram_counts.values())

    # H0
    h0 = 0.0
    if total_unigrams > 0:
        for c in unigram_counts.values():
            p = c / total_unigrams
            h0 -= p * math.log2(p)

    # H1 = sum -p(w1, w2) * log2( p(w1, w2) / p(w1) )
    h1 = 0.0
    if total_bigrams > 0:
        for (w1, _w2), bg_c in bigram_counts.items():
            p_bg = bg_c / total_bigrams
            p_w1 = unigram_counts[w1] / total_unigrams
            if p_w1 > 0:
                h1 -= p_bg * math.log2((bg_c / total_bigrams) / p_w1)

    # H2 = sum -p(w1, w2, w3) * log2( p(w1, w2, w3) / p(w1, w2) )
    h2 = 0.0
    if total_trigrams > 0:
        for (w1, w2, _w3), tg_c in trigram_counts.items():
            p_tg = tg_c / total_trigrams
            p_bg = bigram_counts[(w1, w2)] / total_bigrams
            if p_bg > 0:
                h2 -= p_tg * math.log2((tg_c / total_trigrams) / p_bg)

    ratio = h1 / h0 if h0 > 0 else 1.0

    return ConditionalEntropyProfile(
        order_0_entropy=round(h0, 3),
        order_1_entropy=round(max(h1, 0.0), 3),
        order_2_entropy=round(max(h2, 0.0), 3),
        conditional_drop_ratio=round(ratio, 3),
    )


def calculate_unicity_distance(
    sequences: Sequence[Sequence[str]],
) -> UnicityProfile:
    """Calculate Shannon Unicity Distance U0 = H(K) / D and combinatorial capacity."""
    all_tokens = [sign for seq in sequences for sign in seq]
    n_tokens = len(all_tokens)
    if n_tokens == 0:
        raise ValueError("Cannot calculate unicity on empty corpus")

    counts = collections.Counter(all_tokens)
    signary_size = len(counts)
    mean_len = n_tokens / len(sequences)
    max_len = max(len(s) for s in sequences)

    # Empirical 1-gram entropy
    h_l = calculate_shannon_entropy(all_tokens)
    h_max = math.log2(signary_size) if signary_size > 1 else 1.0

    # Redundancy rate R = 1 - (H_L / H_max)
    red_rate = max(1.0 - (h_l / h_max), 1e-6)
    d_bits = red_rate * h_max  # Redundancy in bits per sign

    # Substitution key equivocation H(K) = log2(n!) = sum_{k=1}^n log2(k)
    key_equivocation_bits = sum(math.log2(k) for k in range(1, signary_size + 1))

    # Unicity distance U0 = H(K) / D
    unicity_tokens = key_equivocation_bits / d_bits
    is_underdetermined = bool(max_len < unicity_tokens)

    # Combinatorial capacity across positions
    pos_dist = collections.defaultdict(set)
    for seq in sequences:
        for p, s in enumerate(seq):
            pos_dist[p].add(s)
    
    comb_capacity = 1.0
    for p in sorted(pos_dist.keys())[:5]:
        comb_capacity *= len(pos_dist[p])

    return UnicityProfile(
        signary_size=signary_size,
        mean_message_length=round(mean_len, 2),
        max_message_length=max_len,
        unigram_entropy=round(h_l, 3),
        max_theoretical_entropy=round(h_max, 3),
        redundancy_rate=round(red_rate, 4),
        redundancy_bits_per_symbol=round(d_bits, 3),
        estimated_key_equivocation_bits=round(key_equivocation_bits, 1),
        unicity_distance_tokens=round(unicity_tokens, 1),
        is_underdetermined=is_underdetermined,
        combinatorial_capacity=float(comb_capacity),
    )
