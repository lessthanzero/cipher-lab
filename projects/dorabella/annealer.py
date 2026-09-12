"""Simulated Annealing Engine for Dorabella Cipher (1897).

Permutes the 24-symbol bijective mapping against English quadgram statistics
with twin-negative surrogate gating to prevent phonetic confirmation bias.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)

from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.hypotheses import ALPHABET_24, scramble_tokens
from projects.dorabella.symbols import decode_tokens


@dataclass
class DorabellaCandidate:
    mapping: Dict[int, str]
    q_score: float
    chi_sq: float
    ioc: float
    plaintext: str


class DorabellaAnnealer:
    """Anneals token-to-letter mappings for the 87-character Dorabella Cipher."""

    def __init__(
        self,
        scorer: Optional[QuadgramScorer] = None,
        tokens: Optional[List[int]] = None,
    ) -> None:
        self.scorer = scorer or QuadgramScorer(language="english")
        self.tokens = tokens or DORABELLA_TOKENS
        self.n_tokens = len(self.tokens)

    def evaluate_mapping(self, mapping: Dict[int, str]) -> Tuple[float, float, float, str]:
        """Decode and score candidate mapping."""
        pt = decode_tokens(self.tokens, mapping)
        q = self.scorer.score_total(pt)
        chi = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)
        return q, chi, ioc, pt

    def anneal(
        self,
        initial_mapping: Optional[Dict[int, str]] = None,
        duration_secs: float = 5.0,
        initial_temp: float = 15.0,
        cooling_rate: float = 0.9997,
        seed: Optional[int] = None,
    ) -> DorabellaCandidate:
        """Run simulated annealing chain over the 24! mapping permutations."""
        rng = random.Random(seed)

        if initial_mapping:
            current_map = dict(initial_mapping)
        else:
            letters = list(ALPHABET_24)
            rng.shuffle(letters)
            current_map = {t: letters[t] for t in range(24)}

        curr_q, curr_chi, curr_ioc, curr_pt = self.evaluate_mapping(current_map)
        best_map = dict(current_map)
        best_q = curr_q
        best_chi = curr_chi
        best_ioc = curr_ioc
        best_pt = curr_pt

        temp = initial_temp
        start_time = time.time()

        while (time.time() - start_time) < duration_secs and temp > 0.05:
            # Swap two letter assignments
            t1, t2 = rng.sample(range(24), 2)
            current_map[t1], current_map[t2] = current_map[t2], current_map[t1]

            cand_q, cand_chi, cand_ioc, cand_pt = self.evaluate_mapping(current_map)
            delta = cand_q - curr_q

            if delta > 0 or math.exp(delta / temp) > rng.random():
                curr_q = cand_q
                curr_chi = cand_chi
                curr_ioc = cand_ioc
                curr_pt = cand_pt

                if cand_q > best_q:
                    best_q = cand_q
                    best_chi = cand_chi
                    best_ioc = cand_ioc
                    best_pt = cand_pt
                    best_map = dict(current_map)
            else:
                # Revert swap
                current_map[t1], current_map[t2] = current_map[t2], current_map[t1]

            temp *= cooling_rate

        return DorabellaCandidate(
            mapping=best_map,
            q_score=best_q,
            chi_sq=best_chi,
            ioc=best_ioc,
            plaintext=best_pt,
        )

    def run_twin_negative_control(self, duration_secs: float = 3.0, seed: int = 999) -> float:
        """Evaluate score on scrambled null ciphertext to calibrate empirical p-value."""
        scrambled = scramble_tokens(self.tokens, seed=seed)
        null_annealer = DorabellaAnnealer(scorer=self.scorer, tokens=scrambled)
        null_res = null_annealer.anneal(duration_secs=duration_secs, seed=seed)
        return null_res.q_score
