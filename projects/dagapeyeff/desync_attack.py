"""Desynchronization Slip and Non-Linear Cartographic Traverse Attack for D'Agapeyeff.

Models the 1939 encipherment clerical error as:
1. Dropped/Inserted Pair Phase-Shift: A dropped coordinate pair at position k
   causing all subsequent columns to shift out of phase.
2. Boustrophedon (Serpentine) Column Traverse: Alternating top-to-bottom / bottom-to-top
   reading of the 14x14 or 14x13 grid (standard cartographic surveying traverse).
3. Diagonal Grid Traverse: Corner-to-corner raster scan.
4. Split-Grid Phase Inversion: Block-separated transposition keys around Position 97.
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


def apply_dropped_pair_slip(pairs: List[str], drop_idx: int, fill_pair: str = "75") -> List[str]:
    """Simulate a dropped pair at drop_idx, shifting all subsequent pairs and appending fill_pair."""
    if drop_idx < 0 or drop_idx >= len(pairs):
        return pairs[:]
    slipped = pairs[:drop_idx] + pairs[drop_idx + 1:]
    slipped.append(fill_pair)
    return slipped


def apply_inserted_pair_slip(pairs: List[str], insert_idx: int, insert_pair: str = "81") -> List[str]:
    """Simulate an erroneously inserted pair at insert_idx, truncating the last pair."""
    if insert_idx < 0 or insert_idx >= len(pairs):
        return pairs[:]
    slipped = pairs[:insert_idx] + [insert_pair] + pairs[insert_idx:-1]
    return slipped


def apply_boustrophedon_traverse(
    pairs: List[str],
    width: int = 13,
    col_order: Optional[List[int]] = None,
) -> List[str]:
    """Read grid in serpentine (boustrophedon) order: col 0 down, col 1 up, col 2 down, etc."""
    n = len(pairs)
    height = math.ceil(n / width)
    grid = []
    for r in range(height):
        grid.append(pairs[r * width : (r + 1) * width])
    
    order = col_order if col_order else list(range(width))
    out = []
    for step, c in enumerate(order):
        col_cells = []
        for r in range(height):
            if c < len(grid[r]):
                col_cells.append(grid[r][c])
        if step % 2 == 1:
            col_cells.reverse()
        out.extend(col_cells)
    return out


def apply_diagonal_traverse(pairs: List[str], width: int = 14) -> List[str]:
    """Traverse grid along anti-diagonals (cartographic quadrangle traverse)."""
    n = len(pairs)
    height = math.ceil(n / width)
    grid = []
    for r in range(height):
        row = pairs[r * width : (r + 1) * width]
        while len(row) < width:
            row.append("75")
        grid.append(row)

    out = []
    for d in range(height + width - 1):
        for r in range(height):
            c = d - r
            if 0 <= c < width:
                out.append(grid[r][c])
    return out[:n]


@dataclass
class DesyncState:
    attack_type: str
    slip_parameter: Any
    alphabet: str
    trans_key: List[int]
    score_q: float
    norm_score: float
    chi_squared: float
    ioc: float
    candidate_pt: str
    competition_eval: Dict[str, Any]


class DesyncAnnealer:
    """Simulated annealing optimizer testing desynchronization slip operators."""

    def __init__(
        self,
        attack_type: str = "boustrophedon",
        grid_mode: str = "14x13_stripped",
        language: str = "english",
        seed_keyword: str = "ORDNANCESURVEY",
        lexical_bonus_weight: float = 0.15,
        seed: int = 42,
    ) -> None:
        self.attack_type = attack_type
        self.grid_mode = grid_mode
        self.language = language
        self.lexical_bonus_weight = lexical_bonus_weight
        self.rng = random.Random(seed)
        self.scorer = QuadgramScorer(language=language)
        self.engine = KerckhoffsEngine()

        raw_196 = get_digit_pairs()
        if grid_mode == "pos97_corrected":
            self.base_pairs = self.engine.apply_position_97_correction(raw_196, replacement="75")
            self.width = 14
        elif grid_mode == "14x13_stripped":
            self.base_pairs = get_stripped_14x13_pairs()
            self.width = 13
        else:
            self.base_pairs = raw_196
            self.width = 14

        self.initial_alphabet = make_polybius_alphabet(seed_keyword)
        self.best_state: Optional[DesyncState] = None

    def _decode_pairs(self, pairs: List[str], alphabet: str) -> str:
        """Instant decode from pre-mapped pair cell indices."""
        ROW_MAP = {"6": 0, "7": 1, "8": 2, "9": 3, "0": 4}
        COL_MAP = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4}
        out = []
        for p in pairs:
            if len(p) == 2:
                r = ROW_MAP.get(p[0], 0)
                c = COL_MAP.get(p[1], 0)
                idx = r * 5 + c
                out.append(alphabet[idx])
            else:
                out.append("?")
        return "".join(out)

    def _transform_pairs(
        self,
        pairs: List[str],
        col_order: List[int],
        slip_param: int,
    ) -> List[str]:
        """Apply the specified desync slip operator."""
        if self.attack_type == "boustrophedon":
            return apply_boustrophedon_traverse(pairs, width=self.width, col_order=col_order)
        elif self.attack_type == "dropped_slip":
            slipped = apply_dropped_pair_slip(pairs, drop_idx=slip_param)
            return self.engine.apply_single_pair_transposition(slipped, width=self.width, col_order=col_order)
        elif self.attack_type == "inserted_slip":
            slipped = apply_inserted_pair_slip(pairs, insert_idx=slip_param)
            return self.engine.apply_single_pair_transposition(slipped, width=self.width, col_order=col_order)
        elif self.attack_type == "diagonal":
            diag = apply_diagonal_traverse(pairs, width=self.width)
            return self.engine.apply_single_pair_transposition(diag, width=self.width, col_order=col_order)
        elif self.attack_type == "split_pos97":
            # First 97 pairs transposed with col_order, remaining pairs reversed
            p1 = self.engine.apply_single_pair_transposition(pairs[:97], width=self.width, col_order=col_order)
            p2 = pairs[97:][::-1]
            return p1 + p2
        else:
            return self.engine.apply_single_pair_transposition(pairs, width=self.width, col_order=col_order)

    def calculate_chi_squared(self, text: str) -> float:
        """Calculate Chi-squared frequency deviation."""
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
        """Compute fitness."""
        clean = "".join(c for c in pt if c.isalpha())
        n = len(clean)
        if n < 4:
            return -9999.0, -9999.0, 999.0, 0.0

        q_tot = self.scorer.score_total(clean)
        q_tot / (n - 3)
        bonus = calculate_cartographic_lexical_bonus(clean) * self.lexical_bonus_weight
        chi2 = self.calculate_chi_squared(clean)
        ioc = calculate_index_of_coincidence(clean)

        return q_tot + bonus, q_tot, chi2, ioc

    def run_desync_chain(
        self,
        duration_secs: float,
        initial_temp: float = 20.0,
        cooling_rate: float = 0.9997,
        loop: Optional[Any] = None,
    ) -> DesyncState:
        """Run simulated annealing exploring desync slips and permutations."""
        t_start = time.time()
        col_order = list(range(self.width))
        self.rng.shuffle(col_order)
        alpha = list(self.initial_alphabet)
        slip_param = self.rng.randrange(len(self.base_pairs))

        transformed_pairs = self._transform_pairs(self.base_pairs, col_order, slip_param)
        pt = self._decode_pairs(transformed_pairs, "".join(alpha))
        fit, q_tot, chi2, ioc = self.score(pt)

        best_fit = fit
        best_state = DesyncState(
            attack_type=self.attack_type,
            slip_parameter=slip_param,
            alphabet="".join(alpha),
            trans_key=col_order[:],
            score_q=q_tot,
            norm_score=q_tot / (len(pt) - 3),
            chi_squared=chi2,
            ioc=ioc,
            candidate_pt=pt,
            competition_eval=evaluate_against_competition(q_tot, chi2, ioc, len(pt)),
        )

        curr_fit = fit
        temp = initial_temp
        iterations = 0
        reheat_counter = 0

        while (time.time() - t_start) < duration_secs:
            iterations += 1
            reheat_counter += 1

            cand_col_order = col_order[:]
            cand_alpha = alpha[:]
            cand_slip = slip_param

            r = self.rng.random()
            if r < 0.40:
                # Column swap
                c1, c2 = self.rng.sample(range(self.width), 2)
                cand_col_order[c1], cand_col_order[c2] = cand_col_order[c2], cand_col_order[c1]
            elif r < 0.80:
                # Alphabet swap
                i1, i2 = self.rng.sample(range(25), 2)
                cand_alpha[i1], cand_alpha[i2] = cand_alpha[i2], cand_alpha[i1]
            else:
                # Mutate slip parameter
                cand_slip = (cand_slip + self.rng.choice([-1, 1, -14, 14, -13, 13])) % len(self.base_pairs)

            cand_transformed = self._transform_pairs(self.base_pairs, cand_col_order, cand_slip)
            cand_pt = self._decode_pairs(cand_transformed, "".join(cand_alpha))
            cand_fit, cand_q, cand_chi2, cand_ioc = self.score(cand_pt)

            delta = cand_fit - curr_fit

            if delta > 0 or self.rng.random() < math.exp(delta / max(temp, 1e-9)):
                col_order = cand_col_order
                alpha = cand_alpha
                slip_param = cand_slip
                curr_fit = cand_fit

                if cand_fit > best_fit:
                    best_fit = cand_fit
                    best_state = DesyncState(
                        attack_type=self.attack_type,
                        slip_parameter=slip_param,
                        alphabet="".join(alpha),
                        trans_key=col_order[:],
                        score_q=cand_q,
                        norm_score=cand_q / (len(cand_pt) - 3),
                        chi_squared=cand_chi2,
                        ioc=cand_ioc,
                        candidate_pt=cand_pt,
                        competition_eval=evaluate_against_competition(cand_q, cand_chi2, cand_ioc, len(cand_pt)),
                    )

            temp = max(temp * cooling_rate, 0.05)

            if reheat_counter >= 15000:
                temp = initial_temp * 0.4
                reheat_counter = 0

            if iterations % 2000 == 0 and loop is not None:
                loop.ledger.record_trial(
                    trial_id=f"desync_{iterations}",
                    artifact_id="dagapeyeff_1939",
                    hypothesis_name=f"H_desync_{self.attack_type}_{self.grid_mode}",
                    key_class=f"desync_{self.attack_type}_{self.grid_mode}",
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
