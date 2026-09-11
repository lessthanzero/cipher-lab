"""High-Performance Two-Square Simulated Annealing Optimizer for D'Agapeyeff.

Directly targets and benchmarks against Tim Marland's project-best record
(Q = -692.13, Phase 6 dagapeyeffresearch.com).

Explores:
1. Vertical Two-Square (Square 1 on top, Square 2 on bottom; column coordinate swap)
2. Horizontal Two-Square (Square 1 on left, Square 2 on right; row coordinate swap)
3. Dual independent alphabets (50 degrees of freedom) vs Single shared alphabet (25 degrees)
4. Sequential stream pairing vs Vertical grid-column pairing
5. Optional pair transposition coupling
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from cipher_lab.stats import (
    QuadgramScorer,
    calculate_index_of_coincidence,
)
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_corpus import calculate_cartographic_lexical_bonus
from projects.dagapeyeff.corpus import (
    get_digit_pairs,
    get_stripped_14x13_pairs,
)
from projects.dagapeyeff.kerckhoffs import KerckhoffsEngine
from projects.dagapeyeff.two_square import (
    STANDARD_ALPHABET,
    TwoSquareEngine,
    pairs_to_coordinates,
)


def make_polybius_alphabet(keyword: str) -> str:
    """Derive 25-letter Polybius alphabet from keyword (merging I/J)."""
    seen = set()
    out = []
    for c in keyword.upper().replace("J", "I"):
        if c.isalpha() and c not in seen:
            seen.add(c)
            out.append(c)
    for c in STANDARD_ALPHABET:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return "".join(out[:25])


@dataclass
class TwoSquareState:
    alphabet1: str
    alphabet2: str
    row_key: Optional[List[int]]
    col_key: Optional[List[int]]
    score_q: float
    norm_score: float
    chi_squared: float
    ioc: float
    candidate_pt: str
    competition_eval: Dict[str, Any]


class TwoSquareAnnealer:
    """Simulated annealing optimizer for Two-Square D'Agapeyeff attacks."""

    def __init__(
        self,
        grid_mode: str = "14x14",
        orientation: str = "vertical",
        dual_alphabets: bool = True,
        pairing_mode: str = "sequential",
        with_transposition: bool = False,
        language: str = "english",
        seed_keyword1: str = "ORDNANCE",
        seed_keyword2: Optional[str] = "MOSKVA",
        lexical_bonus_weight: float = 0.15,
        seed: int = 42,
    ) -> None:
        self.grid_mode = grid_mode
        self.orientation = orientation
        self.dual_alphabets = dual_alphabets
        self.pairing_mode = pairing_mode
        self.with_transposition = with_transposition
        self.language = language
        self.lexical_bonus_weight = lexical_bonus_weight
        self.rng = random.Random(seed)
        self.scorer = QuadgramScorer(language=language)

        # Load raw pairs
        raw_196 = get_digit_pairs()
        if grid_mode == "pos97_corrected":
            engine = KerckhoffsEngine()
            self.pairs = engine.apply_position_97_correction(raw_196, replacement="75")
            self.width = 14
            self.height = 14
        elif grid_mode == "14x13_stripped":
            self.pairs = get_stripped_14x13_pairs()
            self.width = 13
            self.height = 14
        elif grid_mode == "diagonal_pelling_182":
            from projects.dagapeyeff.cartographic_grid import read_diagonal_matrix_transpose
            diag_196 = read_diagonal_matrix_transpose(raw_196, width=14)
            self.pairs = diag_196[:182]
            self.width = 14
            self.height = 13
        elif grid_mode == "diagonal_pelling_196":
            from projects.dagapeyeff.cartographic_grid import read_diagonal_matrix_transpose
            self.pairs = read_diagonal_matrix_transpose(raw_196, width=14)
            self.width = 14
            self.height = 14
        else:
            self.pairs = raw_196
            self.width = 14
            self.height = 14

        self.coords = pairs_to_coordinates(self.pairs)
        self.engine = TwoSquareEngine(
            orientation=self.orientation,
            pairing_mode=self.pairing_mode,
            grid_width=self.width,
        )

        # Precompute fixed lookup indices for ultra-fast zero-transposition evaluation
        self._precompute_fixed_indices()

        # Initial alphabets
        self.init_alpha1 = make_polybius_alphabet(seed_keyword1)
        if dual_alphabets and seed_keyword2:
            self.init_alpha2 = make_polybius_alphabet(seed_keyword2)
        else:
            self.init_alpha2 = self.init_alpha1

        self.best_state: Optional[TwoSquareState] = None

    def _precompute_fixed_indices(self) -> None:
        """Precompute cell index lookups in Square 1 and Square 2 when transposition is off."""
        n = len(self.coords)
        self.fixed_indices_1: List[int] = []
        self.fixed_indices_2: List[int] = []

        if self.pairing_mode == "sequential":
            for i in range(0, n - 1, 2):
                r1, c1 = self.coords[i]
                r2, c2 = self.coords[i + 1]
                if self.orientation == "vertical":
                    if c1 != c2:
                        self.fixed_indices_1.append(r1 * 5 + c2)
                        self.fixed_indices_2.append(r2 * 5 + c1)
                    else:
                        self.fixed_indices_1.append(r1 * 5 + c1)
                        self.fixed_indices_2.append(r2 * 5 + c2)
                else:  # horizontal
                    if r1 != r2:
                        self.fixed_indices_1.append(r2 * 5 + c1)
                        self.fixed_indices_2.append(r1 * 5 + c2)
                    else:
                        self.fixed_indices_1.append(r1 * 5 + c1)
                        self.fixed_indices_2.append(r2 * 5 + c2)
        elif self.pairing_mode == "vertical_grid":
            # Grid column pairs
            grid_idx_1: Dict[int, int] = {}
            grid_idx_2: Dict[int, int] = {}
            w = self.width
            num_rows = n // w
            for c in range(w):
                for r in range(0, num_rows - 1, 2):
                    idx1 = r * w + c
                    idx2 = (r + 1) * w + c
                    if idx2 < n:
                        r1, c1 = self.coords[idx1]
                        r2, c2 = self.coords[idx2]
                        if self.orientation == "vertical":
                            if c1 != c2:
                                grid_idx_1[idx1] = r1 * 5 + c2
                                grid_idx_2[idx2] = r2 * 5 + c1
                            else:
                                grid_idx_1[idx1] = r1 * 5 + c1
                                grid_idx_2[idx2] = r2 * 5 + c2
                        else:
                            if r1 != r2:
                                grid_idx_1[idx1] = r2 * 5 + c1
                                grid_idx_2[idx2] = r1 * 5 + c2
                            else:
                                grid_idx_1[idx1] = r1 * 5 + c1
                                grid_idx_2[idx2] = r2 * 5 + c2
            self.grid_map_1 = grid_idx_1
            self.grid_map_2 = grid_idx_2

    def _fast_decode_sequential(self, a1: List[str], a2: List[str]) -> str:
        """Decode using precomputed sequential indices."""
        num_pairs = len(self.fixed_indices_1)
        chars = [None] * (num_pairs * 2)
        idx1 = self.fixed_indices_1
        idx2 = self.fixed_indices_2
        for i in range(num_pairs):
            chars[2 * i] = a1[idx1[i]]
            chars[2 * i + 1] = a2[idx2[i]]
        return "".join(chars)

    def _fast_decode_grid(self, a1: List[str], a2: List[str]) -> str:
        """Decode using precomputed grid indices."""
        n = len(self.coords)
        out = [None] * n
        for idx, cell in self.grid_map_1.items():
            out[idx] = a1[cell]
        for idx, cell in self.grid_map_2.items():
            out[idx] = a2[cell]
        for i in range(n):
            if out[i] is None:
                r, c = self.coords[i]
                out[i] = a1[r * 5 + c]
        return "".join(out)

    def _transpose_coords(
        self,
        coords: List[Tuple[int, int]],
        row_key: List[int],
        col_key: List[int],
    ) -> List[Tuple[int, int]]:
        """Apply row and column permutation on coordinates."""
        w = self.width
        h = self.height
        grid = [coords[r * w : (r + 1) * w] for r in range(h)]
        
        col_permuted = []
        for r in range(h):
            row_slice = grid[r]
            col_permuted.append([row_slice[c] for c in col_key if c < len(row_slice)])

        row_permuted = [col_permuted[r] for r in row_key if r < len(col_permuted)]
        out = []
        for r in row_permuted:
            out.extend(r)
        return out

    def decode(
        self,
        a1: List[str],
        a2: List[str],
        row_key: Optional[List[int]] = None,
        col_key: Optional[List[int]] = None,
    ) -> str:
        """Decode state to plaintext string."""
        if not self.with_transposition:
            if self.pairing_mode == "sequential":
                return self._fast_decode_sequential(a1, a2)
            else:
                return self._fast_decode_grid(a1, a2)
        else:
            # With transposition
            trans_coords = self._transpose_coords(self.coords, row_key or list(range(self.height)), col_key or list(range(self.width)))
            self.engine.set_alphabets("".join(a1), "".join(a2))
            return self.engine.decipher_coordinates(trans_coords)

    def calculate_chi_squared(self, text: str) -> float:
        """Calculate Chi-squared deviation against standard English."""
        ENGLISH_FREQ = {
            "A": 8.167, "B": 1.492, "C": 2.782, "D": 4.253, "E": 12.702, "F": 2.228,
            "G": 2.015, "H": 6.094, "I": 6.966, "J": 0.153, "K": 0.772, "L": 4.025,
            "M": 2.406, "N": 6.749, "O": 7.507, "P": 1.929, "Q": 0.095, "R": 5.987,
            "S": 6.327, "T": 9.056, "U": 2.758, "V": 0.978, "W": 2.360, "X": 0.150,
            "Y": 1.974, "Z": 0.074,
        }
        clean = [c for c in text if c.isalpha()]
        n = len(clean)
        if n == 0:
            return 999.0
        counts: Dict[str, int] = {}
        for c in clean:
            counts[c] = counts.get(c, 0) + 1
        chi2 = 0.0
        for ltr, freq in ENGLISH_FREQ.items():
            exp = (freq / 100.0) * n
            obs = counts.get(ltr, 0)
            chi2 += ((obs - exp) ** 2) / exp
        return chi2

    def score(self, pt: str) -> Tuple[float, float, float, float]:
        """Compute (total_score_with_bonus, total_q, norm_q, chi2, ioc)."""
        clean = "".join(c for c in pt if c.isalpha())
        n = len(clean)
        if n < 4:
            return -9999.0, -9999.0, -12.0, 999.0, 0.0

        q_total = self.scorer.score_total(clean)
        q_norm = q_total / (n - 3)

        # Lexical cartographic / Nihilist bonus
        bonus = calculate_cartographic_lexical_bonus(clean) * self.lexical_bonus_weight

        chi2 = self.calculate_chi_squared(clean)
        ioc = calculate_index_of_coincidence(clean)

        total_fitness = q_total + bonus
        return total_fitness, q_total, q_norm, chi2, ioc

    def anneal(
        self,
        max_iterations: int = 50000,
        t_start: float = 20.0,
        t_end: float = 0.02,
    ) -> TwoSquareState:
        """Run simulated annealing with exponential temperature decay."""
        a1 = list(self.init_alpha1)
        a2 = list(self.init_alpha2)
        row_k = list(range(self.height)) if self.with_transposition else None
        col_k = list(range(self.width)) if self.with_transposition else None

        pt = self.decode(a1, a2, row_k, col_k)
        total_fit, q_tot, q_norm, chi2, ioc = self.score(pt)

        best_fit = total_fit
        best_state = TwoSquareState(
            alphabet1="".join(a1),
            alphabet2="".join(a2),
            row_key=row_k[:] if row_k else None,
            col_key=col_k[:] if col_k else None,
            score_q=q_tot,
            norm_score=q_norm,
            chi_squared=chi2,
            ioc=ioc,
            candidate_pt=pt,
            competition_eval=evaluate_against_competition(q_tot, chi2, ioc, len(pt)),
        )

        curr_fit = total_fit
        decay = (t_end / t_start) ** (1.0 / max(1, max_iterations))
        t = t_start

        for step in range(max_iterations):
            cand_a1 = a1[:]
            cand_a2 = a2[:] if self.dual_alphabets else cand_a1
            cand_row_k = row_k[:] if row_k else None
            cand_col_k = col_k[:] if col_k else None

            # Mutate
            r = self.rng.random()
            if self.with_transposition and r < 0.25:
                # Transposition mutation
                if self.rng.random() < 0.6 and cand_col_k:
                    c1, c2 = self.rng.sample(range(self.width), 2)
                    cand_col_k[c1], cand_col_k[c2] = cand_col_k[c2], cand_col_k[c1]
                elif cand_row_k:
                    r1, r2 = self.rng.sample(range(self.height), 2)
                    cand_row_k[r1], cand_row_k[r2] = cand_row_k[r2], cand_row_k[r1]
            elif self.dual_alphabets and r < 0.625:
                # Mutate Square 2
                i1, i2 = self.rng.sample(range(25), 2)
                cand_a2[i1], cand_a2[i2] = cand_a2[i2], cand_a2[i1]
            else:
                # Mutate Square 1
                i1, i2 = self.rng.sample(range(25), 2)
                cand_a1[i1], cand_a1[i2] = cand_a1[i2], cand_a1[i1]
                if not self.dual_alphabets:
                    cand_a2 = cand_a1

            cand_pt = self.decode(cand_a1, cand_a2, cand_row_k, cand_col_k)
            cand_total_fit, cand_q, cand_norm, cand_chi2, cand_ioc = self.score(cand_pt)

            delta = cand_total_fit - curr_fit

            if delta > 0 or self.rng.random() < math.exp(delta / max(t, 1e-9)):
                a1 = cand_a1
                a2 = cand_a2
                row_k = cand_row_k
                col_k = cand_col_k
                curr_fit = cand_total_fit

                if cand_total_fit > best_fit:
                    best_fit = cand_total_fit
                    best_state = TwoSquareState(
                        alphabet1="".join(a1),
                        alphabet2="".join(a2),
                        row_key=row_k[:] if row_k else None,
                        col_key=col_k[:] if col_k else None,
                        score_q=cand_q,
                        norm_score=cand_norm,
                        chi_squared=cand_chi2,
                        ioc=cand_ioc,
                        candidate_pt=cand_pt,
                        competition_eval=evaluate_against_competition(cand_q, cand_chi2, cand_ioc, len(cand_pt)),
                    )

            t *= decay

        self.best_state = best_state
        return best_state

    def run_two_square_chain(
        self,
        duration_secs: float,
        initial_temp: float = 20.0,
        cooling_rate: float = 0.9998,
        loop: Optional[Any] = None,
    ) -> TwoSquareState:
        """Run continuous simulated annealing chain for duration_secs."""
        t_start = time.time()

        a1 = list(self.init_alpha1)
        a2 = list(self.init_alpha2)
        row_k = list(range(self.height)) if self.with_transposition else None
        col_k = list(range(self.width)) if self.with_transposition else None

        pt = self.decode(a1, a2, row_k, col_k)
        total_fit, q_tot, q_norm, chi2, ioc = self.score(pt)

        best_fit = total_fit
        best_state = TwoSquareState(
            alphabet1="".join(a1),
            alphabet2="".join(a2),
            row_key=row_k[:] if row_k else None,
            col_key=col_k[:] if col_k else None,
            score_q=q_tot,
            norm_score=q_norm,
            chi_squared=chi2,
            ioc=ioc,
            candidate_pt=pt,
            competition_eval=evaluate_against_competition(q_tot, chi2, ioc, len(pt)),
        )

        curr_fit = total_fit
        temp = initial_temp
        iterations = 0
        reheat_counter = 0

        while (time.time() - t_start) < duration_secs:
            iterations += 1
            reheat_counter += 1

            cand_a1 = a1[:]
            cand_a2 = a2[:] if self.dual_alphabets else cand_a1
            cand_row_k = row_k[:] if row_k else None
            cand_col_k = col_k[:] if col_k else None

            r = self.rng.random()
            if self.with_transposition and r < 0.25:
                if self.rng.random() < 0.6 and cand_col_k:
                    c1, c2 = self.rng.sample(range(self.width), 2)
                    cand_col_k[c1], cand_col_k[c2] = cand_col_k[c2], cand_col_k[c1]
                elif cand_row_k:
                    r1, r2 = self.rng.sample(range(self.height), 2)
                    cand_row_k[r1], cand_row_k[r2] = cand_row_k[r2], cand_row_k[r1]
            elif self.dual_alphabets and r < 0.625:
                i1, i2 = self.rng.sample(range(25), 2)
                cand_a2[i1], cand_a2[i2] = cand_a2[i2], cand_a2[i1]
            else:
                i1, i2 = self.rng.sample(range(25), 2)
                cand_a1[i1], cand_a1[i2] = cand_a1[i2], cand_a1[i1]
                if not self.dual_alphabets:
                    cand_a2 = cand_a1

            cand_pt = self.decode(cand_a1, cand_a2, cand_row_k, cand_col_k)
            cand_total_fit, cand_q, cand_norm, cand_chi2, cand_ioc = self.score(cand_pt)

            delta = cand_total_fit - curr_fit

            if delta > 0 or self.rng.random() < math.exp(delta / max(temp, 1e-9)):
                a1 = cand_a1
                a2 = cand_a2
                row_k = cand_row_k
                col_k = cand_col_k
                curr_fit = cand_total_fit

                if cand_total_fit > best_fit:
                    best_fit = cand_total_fit
                    best_state = TwoSquareState(
                        alphabet1="".join(a1),
                        alphabet2="".join(a2),
                        row_key=row_k[:] if row_k else None,
                        col_key=col_k[:] if col_k else None,
                        score_q=cand_q,
                        norm_score=cand_norm,
                        chi_squared=cand_chi2,
                        ioc=cand_ioc,
                        candidate_pt=cand_pt,
                        competition_eval=evaluate_against_competition(cand_q, cand_chi2, cand_ioc, len(cand_pt)),
                    )

            temp = max(temp * cooling_rate, 0.05)

            # Reheat periodically to escape local minima
            if reheat_counter >= 15000:
                temp = initial_temp * 0.4
                reheat_counter = 0

            # Log to discovery loop ledger periodically
            if iterations % 2000 == 0 and loop is not None:
                loop.ledger.record_trial(
                    trial_id=f"two_sq_{iterations}",
                    artifact_id="dagapeyeff_1939",
                    hypothesis_name=f"H_two_sq_{self.orientation}_{self.grid_mode}_{self.language}",
                    key_class=f"two_square_{self.orientation}_{self.grid_mode}",
                    payload_len=len(best_state.candidate_pt),
                    unicity_distance=26.25,
                    passed_unicity=True,
                    raw_fitness=best_state.norm_score,
                    empirical_p_value=0.5,
                    negative_twin_fitness=0.0,
                    falsification_status="ACTIVE_SEARCH",
                    abstention_reason="",
                )

        self.best_state = best_state
        return best_state

