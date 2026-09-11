"""Deterministic 0-token cryptanalysis statistics and null surrogate generators."""

from __future__ import annotations

import collections
import math
import random
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Dict, Optional

from cipher_lab.models import UnicityCheck


def calculate_index_of_coincidence(text: str) -> float:
    """Calculate the normalized Index of Coincidence (IC) of an alphabetic text.
    
    Standard English text has an IC around 0.066 - 0.068.
    Random text on a 26-letter alphabet has an IC around 1/26 ≈ 0.0385.
    """
    clean = [c.upper() for c in text if c.isalpha()]
    n = len(clean)
    if n <= 1:
        return 0.0
    
    counts = collections.Counter(clean)
    sum_counts = sum(count * (count - 1) for count in counts.values())
    return sum_counts / (n * (n - 1))


def calculate_shannon_entropy(tokens: Sequence[Any]) -> float:
    """Calculate base-2 Shannon entropy H(X) in bits per symbol."""
    n = len(tokens)
    if n == 0:
        return 0.0
    
    counts = collections.Counter(tokens)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
    return entropy


def calculate_conditional_entropy(tokens: Sequence[Any]) -> float:
    """Calculate first-order conditional entropy H(X_2 | X_1) in bits."""
    n = len(tokens)
    if n <= 1:
        return 0.0
    
    unigrams = collections.Counter(tokens)
    bigrams = collections.Counter(zip(tokens[:-1], tokens[1:]))
    
    total_bigrams = n - 1
    cond_entropy = 0.0
    for (w1, _w2), bg_count in bigrams.items():
        p_bigram = bg_count / total_bigrams
        cond_entropy -= p_bigram * math.log2(bg_count / unigrams[w1])
    return cond_entropy


def kasiski_examination(text: str, seq_len: int = 3) -> dict[int, int]:
    """Find repeated n-grams in text and compute gcd intervals for polyalphabetic period detection."""
    clean = "".join(c.upper() for c in text if c.isalnum())
    repeats: dict[str, list[int]] = collections.defaultdict(list)
    for i in range(len(clean) - seq_len + 1):
        seq = clean[i : i + seq_len]
        repeats[seq].append(i)
    
    diff_counts: dict[int, int] = collections.defaultdict(int)
    for seq, positions in repeats.items():
        if len(positions) > 1:
            for i in range(len(positions) - 1):
                diff = positions[i + 1] - positions[i]
                diff_counts[diff] += 1
    return dict(sorted(diff_counts.items(), key=lambda x: x[1], reverse=True))


class QuadgramScorer:
    """Log-likelihood quadgram scorer with floor smoothing for text fitness evaluation."""

    _CACHED_TABLES: dict[str, dict[str, float]] = {}

    def __init__(
        self,
        quadgram_table: dict[str, float] | None = None,
        floor_val: float = -12.0,
        language: str = "english",
        corpus_path: Path | str | None = None,
    ) -> None:
        self.floor = floor_val
        self.language = language.lower()
        if quadgram_table is not None:
            self.ngrams = quadgram_table
        else:
            self.ngrams = self._load_or_default_quadgrams(corpus_path)

    def _load_or_default_quadgrams(self, corpus_path: Path | str | None) -> dict[str, float]:
        cache_key = f"{self.language}_{corpus_path}"
        if cache_key in QuadgramScorer._CACHED_TABLES:
            return QuadgramScorer._CACHED_TABLES[cache_key]

        # Check explicit path or common locations
        paths_to_check = []
        if corpus_path:
            paths_to_check.append(Path(corpus_path))
        
        # Standard repository data directory search
        cwd = Path.cwd()
        if self.language == "english":
            paths_to_check.extend([
                cwd / "data" / "corpora" / "english_quadgrams.txt",
                cwd / "cipher-lab" / "data" / "corpora" / "english_quadgrams.txt",
                Path(__file__).resolve().parents[4] / "data" / "corpora" / "english_quadgrams.txt",
            ])
        elif self.language == "russian_translit":
            paths_to_check.extend([
                cwd / "data" / "corpora" / "russian_translit_quadgrams.txt",
                cwd / "cipher-lab" / "data" / "corpora" / "russian_translit_quadgrams.txt",
                Path(__file__).resolve().parents[4] / "data" / "corpora" / "russian_translit_quadgrams.txt",
            ])

        for p in paths_to_check:
            if p.is_file():
                try:
                    table = {}
                    total = 0
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                q, c = parts[0].upper(), int(parts[1])
                                table[q] = c
                                total += c
                    if total > 0:
                        log_table = {q: math.log10(c / total) for q, c in table.items()}
                        QuadgramScorer._CACHED_TABLES[cache_key] = log_table
                        return log_table
                except Exception:
                    pass

        # Fallback to defaults
        if self.language == "russian_translit":
            fallback = self._default_russian_translit_quadgrams()
        elif self.language == "french":
            fallback = self._default_french_quadgrams()
        else:
            fallback = self._default_english_quadgrams()
        QuadgramScorer._CACHED_TABLES[cache_key] = fallback
        return fallback

    def score_total(self, text: str) -> float:
        """Calculate un-normalized sum of quadgram log-probabilities (Q-score)."""
        clean = "".join(c.upper() for c in text if c.isalpha())
        if len(clean) < 4:
            return self.floor * len(clean)
        return sum(self.ngrams.get(clean[i : i + 4], self.floor) for i in range(len(clean) - 3))

    def score(self, text: str) -> float:
        """Calculate length-normalized log-likelihood of text given quadgram statistics."""
        clean = "".join(c.upper() for c in text if c.isalpha())
        if len(clean) < 4:
            return self.floor
        
        total_score = self.score_total(clean)
        return total_score / (len(clean) - 3)

    def _default_english_quadgrams(self) -> dict[str, float]:
        """A lightweight seed of highly diagnostic English quadgrams."""
        return {
            "TION": -2.8, "NTHE": -3.0, "THER": -3.1, "THAT": -3.2, "OFTH": -3.3,
            "FTHE": -3.4, "THES": -3.5, "WITH": -3.5, "HERE": -3.6, "OFTT": -3.7,
            "INTH": -3.1, "ATIO": -3.3, "EDTO": -3.7, "FROM": -3.8, "HAVE": -3.8,
            "THIS": -3.6, "WHIC": -3.9, "HICH": -3.9, "ANDT": -3.7, "OTHE": -3.5,
        }

    def _default_russian_translit_quadgrams(self) -> dict[str, float]:
        """Diagnostic Russian transliterated (Latin alphabet) quadgrams and Russian keywords."""
        return {
            "KOTO": -2.9, "OTOR": -2.9, "TORY": -3.0, "CHTO": -3.1, "ETOT": -3.1,
            "PISM": -3.3, "ISMO": -3.3, "SHIF": -3.4, "HIFR": -3.4, "KART": -3.2,
            "ARTA": -3.2, "SKVA": -3.5, "OSKV": -3.5, "SKOY": -3.1, "SKII": -3.2,
            "ENIE": -2.8, "NIYE": -2.9, "OVAT": -3.2, "STVO": -3.0, "SCHU": -3.4,
            "UVAL": -3.4, "VALO": -3.3, "ALOV": -3.3, "ALOF": -3.4, "AGAP": -3.4,
            "GAPY": -3.4, "ROSS": -3.3, "OSSI": -3.3, "SSIY": -3.3, "SIYA": -3.3,
        }

    def _default_french_quadgrams(self) -> dict[str, float]:
        """Diagnostic French quadgrams."""
        return {
            "TION": -2.7, "MENT": -2.8, "DANS": -2.9, "POUR": -3.0, "ELLE": -3.1,
            "ETTE": -3.1, "VOUS": -3.1, "NOUS": -3.2, "AVEC": -3.2, "SONT": -3.3,
            "CETT": -3.2, "DONT": -3.3, "PLUS": -3.2, "LEUR": -3.3, "FAIT": -3.4,
        }


def check_unicity_distance(
    payload_len: int,
    alphabet_size: int,
    key_space_bits: float,
    redundancy: float = 3.2,
) -> UnicityCheck:
    """Calculate Shannon unicity distance U_0 = H(K) / D and enforce Gate 0.
    
    If payload_len < unicity_distance, single-key solution is mathematically underdetermined.
    """
    unicity_chars = key_space_bits / redundancy if redundancy > 0 else float("inf")
    underdetermined = payload_len < unicity_chars
    warning = None
    if underdetermined:
        warning = (
            f"Payload length ({payload_len}) < Unicity Distance ({unicity_chars:.1f} chars). "
            f"Key space has {key_space_bits:.1f} bits. Problem is mathematically underdetermined."
        )
    
    return UnicityCheck(
        payload_length=payload_len,
        alphabet_size=alphabet_size,
        estimated_key_space_bits=key_space_bits,
        unicity_distance_chars=unicity_chars,
        is_underdetermined=underdetermined,
        warning=warning,
    )


def order_shuffle_null(tokens: Sequence[Any], n_samples: int = 1000, seed: int = 42) -> list[list[Any]]:
    """Generate order-shuffled surrogates: preserves unigram frequencies while breaking sequential order."""
    rng = random.Random(seed)
    base = list(tokens)
    samples = []
    for _ in range(n_samples):
        surrogate = base[:]
        rng.shuffle(surrogate)
        samples.append(surrogate)
    return samples


def calculate_empirical_p_value(
    observed_score: float,
    null_scores: Sequence[float],
    higher_is_better: bool = True,
) -> float:
    """Calculate empirical p-value against a Monte Carlo null distribution."""
    if not null_scores:
        return 1.0
    
    if higher_is_better:
        count = sum(1 for s in null_scores if s >= observed_score)
    else:
        count = sum(1 for s in null_scores if s <= observed_score)
    
    return (count + 1) / (len(null_scores) + 1)


# Standard letter frequency distributions (percentages)
ENGLISH_LETTER_FREQS = {
    "A": 8.17, "B": 1.49, "C": 2.78, "D": 4.25, "E": 12.70, "F": 2.23, "G": 2.02,
    "H": 6.09, "I": 6.97, "J": 0.15, "K": 0.77, "L": 4.03, "M": 2.41, "N": 6.75,
    "O": 7.51, "P": 1.93, "Q": 0.10, "R": 5.99, "S": 6.33, "T": 9.06, "U": 2.76,
    "V": 0.98, "W": 2.36, "X": 0.15, "Y": 1.97, "Z": 0.07,
}


def calculate_chi_squared(text: str, expected_freqs: Optional[Dict[str, float]] = None) -> float:
    """Calculate Chi-squared statistic against expected letter frequencies.
    
    Standard English text of ~200 chars typically has Chi-sq < 35.0.
    Random uniform or scrambled text has Chi-sq > 150.0.
    """
    clean = [c.upper() for c in text if c.isalpha()]
    n = len(clean)
    if n == 0:
        return 999.0
    
    freq_table = expected_freqs if expected_freqs is not None else ENGLISH_LETTER_FREQS
    counts = collections.Counter(clean)
    
    chi_sq = 0.0
    for letter, exp_pct in freq_table.items():
        exp_count = (exp_pct / 100.0) * n
        obs_count = counts.get(letter, 0)
        chi_sq += ((obs_count - exp_count) ** 2) / max(exp_count, 1e-4)
        
    return chi_sq
