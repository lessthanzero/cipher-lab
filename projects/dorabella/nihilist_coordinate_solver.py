"""Russian Nihilist / Schooling 1896 Coordinate Addition Solver.

Implements the exact cryptographic device demonstrated by John Holt Schooling in
'Secrets in Cipher' (The Pall Mall Magazine, April 1896, Part IV, pp. 614-617)
which Elgar solved on his 'Cryptogram card' 15 months prior to Dorabella:

1. Two-Coordinate Representation:
   Each symbol is characterized by:
   - Band / Hump Count: H in {0, 1, 2} (or 1..3)
   - Angle / Orientation: D in {0, 1, ..., 7} (8 compass directions)

2. Keyword Coordinate Addition / Subtraction:
   A keyword K of length L (specifically L=6, matching the +5.08-sigma harmonic)
   contributes coordinate shifts:
   - delta_H = (H_ct - H_key[i % L]) mod 3
   - delta_D = (D_ct - D_key[i % L]) mod 8
   Plaintext letter is then looked up in the 24-letter geometric compass alphabet.

3. Simultaneous Dual-Corpus Evaluation:
   Evaluates both Dorabella (87 chars) and Liszt (18 chars).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence
from projects.dorabella.corpus import DORABELLA_AUTHENTIC_CONSENSUS
from projects.dorabella.elgar_lexicon import ElgarLexiconScorer
from projects.dorabella.liszt_corpus import LISZT_1886_WORDS, evaluate_dual_corpus
from projects.dorabella.symbols import DIRECTIONS

ALPHABET_24 = "ABCDEFGHIKLMNOPQRSTUVWXY"

# Williams / Consensus coordinate mapping: (Humps 1..3, Direction 0..7)
# Direction indices: 0:E, 1:NE, 2:N, 3:NW, 4:W, 5:SW, 6:S, 7:SE
CONSENSUS_COORDINATES: Dict[str, Tuple[int, int]] = {
    "A": (1, 4),  # 1 hump W
    "B": (3, 0),  # 3 humps E
    "C": (1, 2),  # 1 hump N
    "D": (2, 0),  # 2 humps E
    "E": (1, 0),  # 1 hump E
    "F": (2, 4),  # 2 humps W
    "G": (1, 6),  # 1 hump S
    "H": (2, 2),  # 2 humps N
    "I": (1, 1),  # 1 hump NE
    "J": (2, 1),  # 2 humps NE
    "K": (2, 6),  # 2 humps S
    "L": (2, 7),  # 2 humps SE
    "M": (2, 2),  # 2 humps N
    "N": (3, 2),  # 3 humps N
    "O": (1, 3),  # 1 hump NW
    "P": (2, 5),  # 2 humps SW
    "Q": (1, 7),  # 1 hump SE
    "R": (3, 7),  # 3 humps SE
    "S": (2, 3),  # 2 humps NW
    "T": (3, 6),  # 3 humps S
}


@dataclass
class NihilistTrialResult:
    keyword: str
    period: int
    mode: str  # 'subtract', 'add', 'direct'
    hump_mod: int
    angle_mod: int
    q_score: float
    elgar_score: float
    ioc: float
    plaintext: str
    liszt_plaintext: str
    matches: List[str]


class NihilistCoordinateSolver:
    def __init__(self, scorer: Optional[QuadgramScorer] = None) -> None:
        self.base_scorer = scorer or QuadgramScorer(language="english")
        self.elgar_scorer = ElgarLexiconScorer(self.base_scorer)
        # Precompute coordinate sequences
        self.dorabella_coords = [CONSENSUS_COORDINATES.get(c, (1, 0)) for c in DORABELLA_AUTHENTIC_CONSENSUS]
        self.liszt_coords = [
            [CONSENSUS_COORDINATES.get(c, (1, 0)) for c in word]
            for word in LISZT_1886_WORDS
        ]

    def build_geometric_grid(
        self,
        base_alphabet: str = ALPHABET_24,
        hump_first: bool = True,
    ) -> Dict[Tuple[int, int], str]:
        """Build coordinate to letter mapping (Hump 1..3, Direction 0..7)."""
        grid = {}
        idx = 0
        if hump_first:
            for h in [1, 2, 3]:
                for d in range(8):
                    grid[(h, d)] = base_alphabet[idx % len(base_alphabet)]
                    idx += 1
        else:
            for d in range(8):
                for h in [1, 2, 3]:
                    grid[(h, d)] = base_alphabet[idx % len(base_alphabet)]
                    idx += 1
        return grid

    def evaluate_keyword(
        self,
        keyword: str,
        mode: str = "subtract",
        grid: Optional[Dict[Tuple[int, int], str]] = None,
    ) -> NihilistTrialResult:
        """Apply Nihilist coordinate shift keyed by keyword coordinates."""
        if grid is None:
            grid = self.build_geometric_grid()

        clean_kw = "".join(c for c in keyword.upper() if c in ALPHABET_24)
        if not clean_kw:
            clean_kw = "EDWARD"
        L = len(clean_kw)

        # Invert grid to get letter coordinates
        letter_to_coord = {ch: coord for coord, ch in grid.items()}
        kw_coords = [letter_to_coord.get(c, (1, 0)) for c in clean_kw]

        # Decrypt Dorabella
        pt_chars = []
        for i, (h_c, d_c) in enumerate(self.dorabella_coords):
            h_k, d_k = kw_coords[i % L]
            if mode == "subtract":
                # Humps 1..3 (1-indexed)
                h_p = ((h_c - 1 - (h_k - 1)) % 3) + 1
                d_p = (d_c - d_k) % 8
            elif mode == "add":
                h_p = ((h_c - 1 + (h_k - 1)) % 3) + 1
                d_p = (d_c + d_k) % 8
            else:
                # Direct difference without wrap
                h_p = abs(h_c - h_k) + 1
                d_p = (d_c - d_k) % 8
            pt_chars.append(grid.get((h_p, d_p), "?"))

        pt = "".join(pt_chars)
        q = self.base_scorer.score_total(pt)
        elgar_score, matches = self.elgar_scorer.score_with_elgar_bonus(pt)
        ioc = calculate_index_of_coincidence(pt)

        # Decrypt Liszt
        liszt_pt_words = []
        l_idx = 0
        for word in self.liszt_coords:
            w_chars = []
            for h_c, d_c in word:
                h_k, d_k = kw_coords[l_idx % L]
                l_idx += 1
                if mode == "subtract":
                    h_p = ((h_c - 1 - (h_k - 1)) % 3) + 1
                    d_p = (d_c - d_k) % 8
                else:
                    h_p = ((h_c - 1 + (h_k - 1)) % 3) + 1
                    d_p = (d_c + d_k) % 8
                w_chars.append(grid.get((h_p, d_p), "?"))
            liszt_pt_words.append("".join(w_chars))
        liszt_pt = " ".join(liszt_pt_words) + "_"

        return NihilistTrialResult(
            keyword=clean_kw,
            period=L,
            mode=mode,
            hump_mod=3,
            angle_mod=8,
            q_score=q,
            elgar_score=elgar_score,
            ioc=ioc,
            plaintext=pt,
            liszt_plaintext=liszt_pt,
            matches=matches,
        )
