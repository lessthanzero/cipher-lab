"""Systematic Clock-Face & Compass Geometric Alphabet Solver.

Evaluates deterministic geometric mappings between Elgar's 24 semicircular symbols
(3 hump counts x 8 compass directions) and the 24-letter classical alphabet:
1. Concentric Bands (Band 1 = humps 1, Band 2 = humps 2, Band 3 = humps 3)
2. Radial Spokes (Spoke i has humps 1, 2, 3)
3. 8 starting angles (N, NE, E, SE, S, SW, W, NW) x 2 traversal directions (CW, CCW)
4. Keyed alphabets from pre-1886 and Pall Mall keywords
5. Simultaneous dual-corpus evaluation against Liszt (1886) and Dorabella (1897)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence
from projects.dorabella.corpus import DORABELLA_AUTHENTIC_CONSENSUS
from projects.dorabella.elgar_lexicon import ElgarLexiconScorer
from projects.dorabella.liszt_corpus import LISZT_1886_WORDS, evaluate_dual_corpus
from projects.dorabella.symbols import DIRECTIONS, SYMBOL_CATALOG

ALPHABET_24 = "ABCDEFGHIKLMNOPQRSTUVWXY"

KEYWORDS = [
    "",  # Straight alphabetical
    "EDWARD", "ELGAR", "WORCESTER", "MALVERN",
    "LISZT", "VIOLIN", "ORGAN", "CHORAL",
    "PRELUDE", "PASTORAL", "MARZIALE",
    "AMDG", "CREDO", "SANCTUS", "GLORIA",
    "TYRANT", "CIPHER", "SECRETS",
]

DIRS_8 = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]


def make_keyed_alphabet(kw: str) -> str:
    seen = set()
    clean = []
    for c in kw.upper():
        if c == "J":
            c = "I"
        if c == "V":
            c = "U"
        if c == "Z":
            c = "S"
        if c in ALPHABET_24 and c not in seen:
            seen.add(c)
            clean.append(c)
    for c in ALPHABET_24:
        if c not in seen:
            clean.append(c)
    return "".join(clean)


@dataclass
class GeometricKeyResult:
    layout_type: str        # 'concentric' or 'radial'
    start_dir: str          # starting compass direction
    direction: str          # 'CW' or 'CCW'
    keyword: str
    dorabella_q: float
    dorabella_elgar: float
    dorabella_ioc: float
    dorabella_pt: str
    liszt_pt: str
    liszt_words: List[str]
    elgar_matches: List[str]


class GeometricClockSolver:
    def __init__(self, scorer: Optional[QuadgramScorer] = None) -> None:
        self.base_scorer = scorer or QuadgramScorer(language="english")
        self.elgar_scorer = ElgarLexiconScorer(self.base_scorer)

    def generate_key(
        self,
        layout_type: str = "concentric",
        start_dir: str = "N",
        direction: str = "CW",
        keyword: str = "",
    ) -> Dict[str, str]:
        """Generate symbol-to-letter dictionary for a specific geometric configuration."""
        alpha = make_keyed_alphabet(keyword)
        assert len(alpha) == 24

        # Ordered compass directions
        idx0 = DIRS_8.index(start_dir)
        if direction == "CW":
            # CW in compass: E -> SE -> S -> SW -> W -> NW -> N -> NE
            # Our DIRS_8 is E(0), NE(1), N(2), NW(3), W(4), SW(5), S(6), SE(7)
            # CCW in angle = CW in compass
            ordered_dirs = [DIRS_8[(idx0 - i) % 8] for i in range(8)]
        else:
            ordered_dirs = [DIRS_8[(idx0 + i) % 8] for i in range(8)]

        symbol_map = {}
        # In Williams / consensus alphabet:
        # We need mapping from the 20 consensus letters (or token IDs) to plaintext letters
        # Let's map from (humps, dir) -> letter
        geom_map = {}
        if layout_type == "concentric":
            # Ring 1 (hump 1), Ring 2 (hump 2), Ring 3 (hump 3)
            letter_idx = 0
            for humps in [1, 2, 3]:
                for d in ordered_dirs:
                    geom_map[(humps, d)] = alpha[letter_idx]
                    letter_idx += 1
        else:
            # Radial spokes
            letter_idx = 0
            for d in ordered_dirs:
                for humps in [1, 2, 3]:
                    geom_map[(humps, d)] = alpha[letter_idx]
                    letter_idx += 1

        # Now map consensus characters to letters
        # Using the standard consensus symbol correspondence:
        # A: 1 hump W (180)
        # B: 3 humps E (0)
        # C: 1 hump N (90)
        # D: 2 humps E (0)
        # E: 1 hump E (0)
        # F: 2 humps W (180)
        # G: 1 hump S (270)
        # H: 2 humps N (90)
        # I: 1 hump NE (45)
        # J: 2 humps NE (45)
        # K: 2 humps S (270)
        # L: 2 humps SE (315)
        # M: 2 humps N (90)
        # N: 3 humps N (90)
        # O: 1 hump NW (135)
        # P: 2 humps SW (225)
        # Q: 1 hump SE (315)
        # R: 3 humps SE (315)
        # S: 2 humps NW (135)
        # T: 3 humps S (270)
        consensus_geom = {
            "A": (1, "W"),
            "B": (3, "E"),
            "C": (1, "N"),
            "D": (2, "E"),
            "E": (1, "E"),
            "F": (2, "W"),
            "G": (1, "S"),
            "H": (2, "N"),
            "I": (1, "NE"),
            "J": (2, "NE"),
            "K": (2, "S"),
            "L": (2, "SE"),
            "M": (2, "N"),
            "N": (3, "N"),
            "O": (1, "NW"),
            "P": (2, "SW"),
            "Q": (1, "SE"),
            "R": (3, "SE"),
            "S": (2, "NW"),
            "T": (3, "S"),
        }

        key = {}
        for char, (h, d) in consensus_geom.items():
            key[char] = geom_map.get((h, d), "?")

        return key

    def sweep_all_geometries(self) -> List[GeometricKeyResult]:
        """Exhaustively evaluate all geometric clock-face hypotheses."""
        results = []
        for layout in ["concentric", "radial"]:
            for start_d in DIRS_8:
                for direction in ["CW", "CCW"]:
                    for kw in KEYWORDS:
                        key = self.generate_key(
                            layout_type=layout,
                            start_dir=start_d,
                            direction=direction,
                            keyword=kw,
                        )
                        eval_res = evaluate_dual_corpus(
                            key_mapping=key,
                            dorabella_ciphertext=DORABELLA_AUTHENTIC_CONSENSUS,
                        )
                        d_pt = eval_res["dorabella_plaintext"]
                        l_pt = eval_res["liszt_plaintext"]
                        l_words = eval_res["liszt_words"]

                        q = self.base_scorer.score_total(d_pt)
                        elgar_score, matches = self.elgar_scorer.score_with_elgar_bonus(d_pt)
                        ioc = calculate_index_of_coincidence(d_pt)

                        res = GeometricKeyResult(
                            layout_type=layout,
                            start_dir=start_d,
                            direction=direction,
                            keyword=kw,
                            dorabella_q=q,
                            dorabella_elgar=elgar_score,
                            dorabella_ioc=ioc,
                            dorabella_pt=d_pt,
                            liszt_pt=l_pt,
                            liszt_words=l_words,
                            elgar_matches=matches,
                        )
                        results.append(res)
        return results


if __name__ == "__main__":
    solver = GeometricClockSolver()
    print("Sweeping all geometric clock-face configurations...")
    results = solver.sweep_all_geometries()
    print(f"Total configurations tested: {len(results)}")

    # Sort by Dorabella Elgar Score
    results.sort(key=lambda r: r.dorabella_elgar, reverse=True)

    print("\n" + "=" * 80)
    print("TOP 5 GEOMETRIC CONFIGURATIONS (BY DORABELLA ELGAR SCORE):")
    print("=" * 80)
    for r in results[:5]:
        print(f"[{r.layout_type} | Start: {r.start_dir} | Dir: {r.direction} | Key: '{r.keyword}']")
        print(f"  Dorabella Q: {r.dorabella_q:.1f} | Elgar Score: {r.dorabella_elgar:.1f} | IoC: {r.dorabella_ioc:.4f}")
        print(f"  Matches: {r.elgar_matches}")
        print(f"  Dorabella Plaintext: {r.dorabella_pt[:40]}...")
        print(f"  Liszt Plaintext:     {r.liszt_pt}")
        print("-" * 60)
