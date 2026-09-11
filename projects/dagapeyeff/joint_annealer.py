"""High-Performance Joint Simulated Annealing Optimizer for D'Agapeyeff.

Simultaneously mutates the pair-transposition key (row/column permutations)
and the 5x5 Polybius alphabet square against multilingual quadgram distributions.
Directly competes against Tim Marland's SOTA project records (dagapeyeffresearch.com).
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from cipher_lab.loop import CipherDiscoveryLoop
from cipher_lab.stats import QuadgramScorer
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_corpus import calculate_cartographic_lexical_bonus
from projects.dagapeyeff.corpus import (
    get_digit_pairs,
    get_payload_digits,
    get_stripped_14x13_pairs,
)
from projects.dagapeyeff.kerckhoffs import KerckhoffsEngine
from projects.dagapeyeff.nihilist_additive import (
    coords_to_pairs,
    derive_additive_key_from_keyword,
    pairs_to_coords,
    subtract_additive_key,
)


def make_polybius_alphabet(keyword: str) -> str:
    """Derive 25-letter Polybius alphabet from keyword (merging I/J)."""
    seen = set()
    out = []
    for c in keyword.upper().replace("J", "I"):
        if c.isalpha() and c not in seen:
            seen.add(c)
            out.append(c)
    for c in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in seen:
            seen.add(c)
            out.append(c)
    return "".join(out[:25])


@dataclass
class AnnealingState:
    row_key: List[int]
    col_key: List[int]
    alphabet: str
    width: int
    score_q: float
    norm_score: float
    candidate_pt: str
    additive_key: Optional[List[Tuple[int, int]]] = None
    additive_order: str = "none"


class JointDagapeyeffAnnealer:
    """Jointly optimizes pair-stream transposition, Polybius square substitution, and modular additive keys."""

    def __init__(
        self,
        grid_mode: str = "14x13_stripped",
        language: str = "english",
        seed_keyword: str = "NIHILIST",
        lexical_bonus_weight: float = 0.15,
        additive_order: str = "none",
        additive_key_period: int = 0,
        initial_additive_keyword: Optional[str] = None,
        seed: int = 42,
    ) -> None:
        self.grid_mode = grid_mode
        self.language = language
        self.lexical_bonus_weight = lexical_bonus_weight
        self.additive_order = additive_order
        self.additive_key_period = additive_key_period
        self.rng = random.Random(seed)
        self.scorer = QuadgramScorer(language=language)
        
        # Load pair data based on mode
        raw_196 = get_digit_pairs()
        if grid_mode == "pos97_corrected":
            engine = KerckhoffsEngine()
            self.pairs = engine.apply_position_97_correction(raw_196, replacement="75")
            self.width = 14
            self.num_rows = 14
        elif grid_mode == "14x13_stripped":
            self.pairs = get_stripped_14x13_pairs()
            self.width = 13
            self.num_rows = 14
        else:  # standard 14x14
            self.pairs = raw_196
            self.width = 14
            self.num_rows = 14

        self.row_map = {"6": 1, "7": 2, "8": 3, "9": 4, "0": 5}
        self.initial_alphabet = make_polybius_alphabet(seed_keyword)
        self.best_state: Optional[AnnealingState] = None

        # Setup initial additive key
        if initial_additive_keyword:
            self.initial_additive_key = derive_additive_key_from_keyword(initial_additive_keyword, self.initial_alphabet)
            self.additive_key_period = len(self.initial_additive_key)
        elif additive_key_period > 0:
            self.initial_additive_key = [(self.rng.randrange(5), self.rng.randrange(5)) for _ in range(additive_key_period)]
        else:
            self.initial_additive_key = None

    def _decode(self, pairs: List[str], alphabet: str) -> str:
        """Fast decode pairs using given 25-letter alphabet."""
        grid_chars = {}
        idx = 0
        for r in range(1, 6):
            for c in range(1, 6):
                grid_chars[(r, c)] = alphabet[idx]
                idx += 1

        chars = []
        for p in pairs:
            if len(p) == 2:
                r = self.row_map.get(p[0], 1)
                try:
                    c = int(p[1])
                except ValueError:
                    c = 1
                chars.append(grid_chars.get((r, c), "?"))
        return "".join(chars)

    def _decode_state(
        self,
        pairs: List[str],
        row_key: List[int],
        col_key: List[int],
        alphabet: str,
        additive_key: Optional[List[Tuple[int, int]]],
        additive_order: str,
    ) -> str:
        """Decode with optional pre- or post-transposition modular subtraction."""
        if additive_order == "post_transposition" and additive_key:
            coords = pairs_to_coords(pairs)
            dec_coords = subtract_additive_key(coords, additive_key)
            sub_pairs = coords_to_pairs(dec_coords)
            trans_pairs = self._transpose(sub_pairs, row_key, col_key)
            return self._decode(trans_pairs, alphabet)
        elif additive_order == "pre_transposition" and additive_key:
            trans_pairs = self._transpose(pairs, row_key, col_key)
            coords = pairs_to_coords(trans_pairs)
            dec_coords = subtract_additive_key(coords, additive_key)
            sub_pairs = coords_to_pairs(dec_coords)
            return self._decode(sub_pairs, alphabet)
        else:
            trans_pairs = self._transpose(pairs, row_key, col_key)
            return self._decode(trans_pairs, alphabet)

    def _transpose(self, pairs: List[str], row_key: List[int], col_key: List[int]) -> List[str]:
        """Apply Kerckhoffs transposition on pairs."""
        w = self.width
        h = self.num_rows
        # 1. Arrange in rows
        grid = [pairs[r * w : (r + 1) * w] for r in range(h)]
        
        # 2. Permute columns according to col_key
        col_permuted = []
        for r in range(h):
            row_slice = grid[r]
            col_permuted.append([row_slice[c] for c in col_key if c < len(row_slice)])

        # 3. Permute rows according to row_key
        row_permuted = [col_permuted[r] for r in row_key if r < len(col_permuted)]

        # 4. Flatten back to pair stream
        out = []
        for r in row_permuted:
            out.extend(r)
        return out

    def step(
        self,
        current_state: AnnealingState,
        temp: float,
    ) -> AnnealingState:
        """Execute one mutation step and evaluate Metropolis-Hastings criterion."""
        # Mutate copy
        new_row_key = current_state.row_key[:]
        new_col_key = current_state.col_key[:]
        new_alpha_list = list(current_state.alphabet)
        new_additive_key = [k for k in current_state.additive_key] if current_state.additive_key else None

        mutation_type = self.rng.random()
        if new_additive_key and mutation_type < 0.25:
            # Mutate one position in additive key
            idx = self.rng.randrange(len(new_additive_key))
            new_additive_key[idx] = (self.rng.randrange(5), self.rng.randrange(5))
        elif mutation_type < 0.55:
            # Swap 2 columns
            i, j = self.rng.sample(range(self.width), 2)
            new_col_key[i], new_col_key[j] = new_col_key[j], new_col_key[i]
        elif mutation_type < 0.80:
            # Swap 2 rows
            i, j = self.rng.sample(range(self.num_rows), 2)
            new_row_key[i], new_row_key[j] = new_row_key[j], new_row_key[i]
        elif mutation_type < 0.95:
            # Swap 2 alphabet letters
            i, j = self.rng.sample(range(25), 2)
            new_alpha_list[i], new_alpha_list[j] = new_alpha_list[j], new_alpha_list[i]
        else:
            # Reversal mutation on columns
            i, j = sorted(self.rng.sample(range(self.width), 2))
            new_col_key[i : j + 1] = reversed(new_col_key[i : j + 1])

        new_alpha = "".join(new_alpha_list)
        new_pt = self._decode_state(
            self.pairs, new_row_key, new_col_key, new_alpha, new_additive_key, current_state.additive_order
        )
        new_q = self.scorer.score_total(new_pt)

        # Calculate guided score if lexical bonus enabled
        if self.lexical_bonus_weight > 0.0:
            cur_lex = calculate_cartographic_lexical_bonus(current_state.candidate_pt)
            new_lex = calculate_cartographic_lexical_bonus(new_pt)
            cur_guided = current_state.score_q + (self.lexical_bonus_weight * cur_lex)
            new_guided = new_q + (self.lexical_bonus_weight * new_lex)
            delta = new_guided - cur_guided
        else:
            delta = new_q - current_state.score_q

        # Acceptance check
        accept = False
        if delta > 0.0:
            accept = True
        elif temp > 1e-4:
            prob = math.exp(delta / temp)
            if self.rng.random() < prob:
                accept = True

        if accept:
            new_state = AnnealingState(
                row_key=new_row_key,
                col_key=new_col_key,
                alphabet=new_alpha,
                width=self.width,
                score_q=new_q,
                norm_score=new_q / (len(new_pt) - 3),
                candidate_pt=new_pt,
                additive_key=new_additive_key,
                additive_order=current_state.additive_order,
            )
            if self.best_state is None or new_q > self.best_state.score_q:
                self.best_state = new_state
            return new_state

        return current_state

    def run_annealing_chain(
        self,
        duration_secs: float,
        initial_temp: float = 20.0,
        cooling_rate: float = 0.9997,
        loop: Optional[CipherDiscoveryLoop] = None,
    ) -> AnnealingState:
        """Run continuous simulated annealing chain for duration_secs."""
        t_start = time.time()
        
        # Initial state
        row_key = list(range(self.num_rows))
        col_key = list(range(self.width))
        self.rng.shuffle(row_key)
        self.rng.shuffle(col_key)
        init_additive_key = [k for k in self.initial_additive_key] if self.initial_additive_key else None
        
        pt = self._decode_state(
            self.pairs, row_key, col_key, self.initial_alphabet, init_additive_key, self.additive_order
        )
        init_q = self.scorer.score_total(pt)

        current_state = AnnealingState(
            row_key=row_key,
            col_key=col_key,
            alphabet=self.initial_alphabet,
            width=self.width,
            score_q=init_q,
            norm_score=init_q / (len(pt) - 3),
            candidate_pt=pt,
            additive_key=init_additive_key,
            additive_order=self.additive_order,
        )
        self.best_state = current_state

        temp = initial_temp
        iterations = 0
        reheat_counter = 0

        while (time.time() - t_start) < duration_secs:
            iterations += 1
            reheat_counter += 1
            current_state = self.step(current_state, temp)
            temp = max(temp * cooling_rate, 0.05)

            # Reheat periodically to escape local minima
            if reheat_counter >= 15000:
                temp = initial_temp * 0.5
                reheat_counter = 0

            # Log to discovery loop periodically or when viable
            if iterations % 2000 == 0 and loop is not None:
                comp = evaluate_against_competition(
                    self.best_state.score_q,
                    999.0,
                    0.065,
                    len(self.best_state.candidate_pt),
                )
                loop.ledger.record_trial(
                    trial_id=f"sa_{iterations}",
                    artifact_id="dagapeyeff_1939",
                    hypothesis_name=f"H_sa_{self.grid_mode}_{self.language}",
                    key_class=f"joint_sa_{self.grid_mode}",
                    payload_len=len(self.best_state.candidate_pt),
                    unicity_distance=26.25,
                    passed_unicity=True,
                    raw_fitness=self.best_state.norm_score,
                    empirical_p_value=0.5,
                    negative_twin_fitness=0.0,
                    falsification_status="ACTIVE_SEARCH",
                    abstention_reason="",
                )

        return self.best_state
