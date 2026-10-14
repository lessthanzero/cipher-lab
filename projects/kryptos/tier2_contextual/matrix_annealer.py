"""Constrained 14x7 Key Matrix Simulated Annealer for Kryptos K4.

Optimizes key schedule over the 73 unconstrained cells while strictly fixing
the 24 known anchor cells:
- Anchor indices 21..33 (Crib 1) fixed
- Anchor indices 63..73 (Crib 2) fixed
- Objective function: Quadgram linguistic fitness Q under QuadgramScorer
- Structural regularization: Enforces lag-7 column coherence
"""

from __future__ import annotations

import argparse
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence

from projects.kryptos.manifests import BLIND_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


@dataclass
class AnnealResult:
    q_score: float
    ioc: float
    plaintext_sample: str
    key_shifts: List[int]
    iterations: int
    duration_secs: float


class MatrixAnnealer:
    def __init__(
        self,
        scorer: Optional[QuadgramScorer] = None,
        alphabet: str = KRYPTOS_ALPHABET,
    ) -> None:
        self.alphabet = alphabet
        self.m = len(alphabet)
        self.scorer = scorer or QuadgramScorer(language="english")

        blind = load_dataset(BLIND_PATH, current_tier=1)
        self.ciphertext = blind["ciphertext"]
        self.n = len(self.ciphertext)

        # Extract anchor dictionary: index -> (c_val, p_val, required_shift)
        pairs = extract_known_pairs()
        self.anchors: Dict[int, int] = {}
        for idx, c, p in pairs:
            c_val = self.alphabet.index(c)
            p_val = self.alphabet.index(p)
            req_shift = (c_val - p_val) % self.m
            self.anchors[idx] = req_shift

        self.unconstrained_indices = [i for i in range(self.n) if i not in self.anchors]

    def decrypt(self, key_shifts: List[int]) -> str:
        """Decrypt ciphertext using candidate key shifts."""
        pt_chars = []
        for i, c in enumerate(self.ciphertext):
            c_val = self.alphabet.index(c)
            k_val = key_shifts[i]
            p_val = (c_val - k_val) % self.m
            pt_chars.append(self.alphabet[p_val])
        return "".join(pt_chars)

    def initial_state(self, mode: str = "column_repeat") -> List[int]:
        """Generate initial key schedule satisfying all 24 anchors."""
        shifts = [0] * self.n

        # First, fill all anchors
        for idx, s in self.anchors.items():
            shifts[idx] = s

        if mode == "column_repeat":
            # For unconstrained cells in col c, take the mode of known anchor shifts in col c
            col_anchors: Dict[int, List[int]] = {col: [] for col in range(7)}
            for idx, s in self.anchors.items():
                col_anchors[idx % 7].append(s)

            for i in self.unconstrained_indices:
                col = i % 7
                if col_anchors[col]:
                    shifts[i] = col_anchors[col][0]
                else:
                    shifts[i] = random.randint(0, self.m - 1)
        else:
            for i in self.unconstrained_indices:
                shifts[i] = random.randint(0, self.m - 1)

        return shifts

    def anneal(
        self,
        duration_secs: float = 2.0,
        temp_init: float = 10.0,
        temp_min: float = 0.05,
        seed: int = 42,
    ) -> AnnealResult:
        """Run simulated annealing on the unconstrained key cells."""
        random.seed(seed)
        start_time = time.time()

        current_shifts = self.initial_state(mode="column_repeat")
        current_pt = self.decrypt(current_shifts)
        current_q = self.scorer.score(current_pt)

        best_shifts = list(current_shifts)
        best_q = current_q
        best_pt = current_pt

        iterations = 0
        while True:
            elapsed = time.time() - start_time
            if elapsed >= duration_secs:
                break

            temp = temp_init * (temp_min / temp_init) ** (elapsed / duration_secs)

            # Propose move: change 1 or 2 unconstrained cells
            # Bias moves towards cells in the same column matching or shifting by small delta
            idx_to_change = random.choice(self.unconstrained_indices)
            old_val = current_shifts[idx_to_change]

            if random.random() < 0.5:
                # Delta step (+- 1 or +- 2)
                step = random.choice([-2, -1, 1, 2])
                new_val = (old_val + step) % self.m
            else:
                # Copy from another cell in the same column
                same_col_anchors = [current_shifts[j] for j in range(self.n) if j % 7 == idx_to_change % 7 and j != idx_to_change]
                new_val = random.choice(same_col_anchors) if same_col_anchors else random.randint(0, self.m - 1)

            current_shifts[idx_to_change] = new_val
            cand_pt = self.decrypt(current_shifts)
            cand_q = self.scorer.score(cand_pt)
            delta = cand_q - current_q

            if delta > 0 or random.random() < math.exp(delta / max(temp, 1e-6)):
                current_q = cand_q
                current_pt = cand_pt
                if cand_q > best_q:
                    best_q = cand_q
                    best_shifts = list(current_shifts)
                    best_pt = cand_pt
            else:
                current_shifts[idx_to_change] = old_val

            iterations += 1

        total_time = time.time() - start_time
        ioc = calculate_index_of_coincidence(best_pt)

        return AnnealResult(
            q_score=round(best_q, 2),
            ioc=round(ioc, 5),
            plaintext_sample=best_pt,
            key_shifts=best_shifts,
            iterations=iterations,
            duration_secs=round(total_time, 2),
        )


def run_annealing_campaign(
    restarts: int = 5,
    budget_per_restart_secs: float = 1.0,
) -> Dict[str, Any]:
    """Execute multi-restart constrained annealing campaign."""
    annealer = MatrixAnnealer()
    results = []

    print(f"[*] Launching {restarts} Annealing Restarts ({budget_per_restart_secs}s each)...", flush=True)
    for r in range(restarts):
        res = annealer.anneal(duration_secs=budget_per_restart_secs, seed=100 + r * 37)
        results.append(res)
        print(f"  Restart {r+1}/{restarts}: Best Q = {res.q_score:.2f}, IoC = {res.ioc:.5f} ({res.iterations} iters)", flush=True)

    best = max(results, key=lambda x: x.q_score)
    return {
        "restarts": restarts,
        "best_q_score": best.q_score,
        "best_ioc": best.ioc,
        "best_plaintext_sample": best.plaintext_sample,
        "sample_start": best.plaintext_sample[:40],
        "sample_crib1": best.plaintext_sample[21:34],
        "sample_crib2": best.plaintext_sample[63:74],
    }


if __name__ == "__main__":
    res = run_annealing_campaign(restarts=3, budget_per_restart_secs=1.0)
    print("=" * 70)
    print("CIPHERLAB — CONSTRAINED MATRIX ANNEALER RESULTS")
    print("=" * 70)
    print(f"Best Quadgram Score: {res['best_q_score']}")
    print(f"Best Index of Coinc: {res['best_ioc']}")
    print(f"Crib 1 (pos 21..34): {res['sample_crib1']} (Expected: EASTNORTHEAST)")
    print(f"Crib 2 (pos 63..74): {res['sample_crib2']} (Expected: BERLINCLOCK)")
    print(f"Decrypted Preview:   {res['sample_start']}...")
    print("=" * 70)
