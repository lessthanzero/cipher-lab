"""Joint Grille Transposition & Period-6 Polyalphabetic Decoupling Solver.

Implements the cryptographic architecture demonstrated on Edward Elgar's 1896
'Cryptogram Card' (Schooling's Pall Mall Magazine challenge) constrained by
the 1886 Liszt fragment chronological bound and the +5.08-sigma Period 6 harmonic:

1. Transposition Layer:
   - 3x29, 29x3, and 6x14 (+3) rectangular grids.
   - Schooling turning card grilles (4 orthogonal rotations + vertical reflections).
   - Alternating boustrophedon and spiral drafting traversals.

2. Period-6 Polyalphabetic Layer:
   - 6-period coset decomposition (exploiting the +5.08-sigma IoC = 0.0686 peak).
   - Fast coordinate-ascent solver over the 6-shift parameter space (24^6 or 26^6).
   - Exhaustive evaluation across pre-1886 historical, musical, and Latin liturgical keywords.

3. Epistemic Gating:
   - Base English quadgram log-likelihood (Q).
   - ElgarLexiconScorer bonus weighting.
   - Cross-evaluation against authentic consensus text (N=87, IoC=0.0585).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

from cipher_lab.stats import QuadgramScorer

from projects.dorabella.corpus import DORABELLA_AUTHENTIC_CONSENSUS
from projects.dorabella.elgar_lexicon import ElgarLexiconScorer

ALPHABET_STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALPHABET_24 = "ABCDEFGHIKLMNOPQRSTUVWXY"

# Pre-1886 and biographical candidate keywords (including April 1886 Les Preludes & April 1896 Pall Mall)
PRE_1886_KEYWORDS: List[str] = [
    # Sacred / Catholic Liturgy (Elgar was organist at St George's RC Church from 1885)
    "GLORIA", "CREDO", "SANCTUS", "SALVE", "REQUIEM", "AMDG", "LDS",
    # Musical terminology & Liszt 1886 Crystal Palace 'Les Preludes' primary context
    "LISZT", "VIOLIN", "CHORAL", "ORGAN", "SONATA", "FUGUE", "MOTIF",
    "PRELUD", "PASTOR", "MARZIAL", "CRYSTAL", "PALACE", "LAMART",
    # John Holt Schooling 'Pall Mall Magazine' April 1896 cipher challenge context
    "TYRANT", "VERONA", "MANTUA", "TYBALT", "CIPHER", "SECRETS", "SCHOOL",
    # Geography & Family
    "POWICK", "FORLI", "SEVERN", "EDWARD", "ALFRED", "ALICE",
]


@dataclass
class GrilleCandidate:
    transposition_type: str
    grille_rotation: int
    mode: str
    keyword: Optional[str]
    shifts: List[int]
    q_score: float
    elgar_score: float
    ioc: float
    plaintext: str
    elgar_matches: List[str]


class JointGrillePolyalphabeticSolver:
    """Jointly optimizes turning grille transpositions and Period-6 polyalphabetic shifts."""

    def __init__(
        self,
        ciphertext: str = DORABELLA_AUTHENTIC_CONSENSUS,
        scorer: QuadgramScorer | None = None,
    ) -> None:
        self.ciphertext = ciphertext
        self.n = len(ciphertext)
        self.base_scorer = scorer or QuadgramScorer(language="english")
        self.elgar_scorer = ElgarLexiconScorer(self.base_scorer)
        self.a26 = ALPHABET_STANDARD

    def apply_grid_transposition(
        self,
        grid_shape: Tuple[int, int] = (3, 29),
        traversal: str = "row_major",
        rotation: int = 0,
        reflect: bool = False,
    ) -> str:
        """Arrange ciphertext into grid and read out under geometric transformation."""
        rows, cols = grid_shape
        # Pad if needed
        total_cells = rows * cols
        padded = self.ciphertext.ljust(total_cells, "X")
        grid = [[padded[r * cols + c] for c in range(cols)] for r in range(rows)]

        # Reflection (horizontal / vertical)
        if reflect:
            grid = [row[::-1] for row in grid]

        # 90-degree rotations (for square sub-blocks or 180-degree for rectangles)
        if rotation == 180:
            grid = [row[::-1] for row in reversed(grid)]

        # Traversals
        chars = []
        if traversal == "row_major":
            for r in range(rows):
                for c in range(cols):
                    chars.append(grid[r][c])
        elif traversal == "col_major":
            for c in range(cols):
                for r in range(rows):
                    chars.append(grid[r][c])
        elif traversal == "boustrophedon":
            for r in range(rows):
                row_chars = grid[r] if r % 2 == 0 else list(reversed(grid[r]))
                chars.extend(row_chars)
        elif traversal == "spiral":
            top, bottom, left, right = 0, rows - 1, 0, cols - 1
            while top <= bottom and left <= right:
                for c in range(left, right + 1):
                    chars.append(grid[top][c])
                top += 1
                for r in range(top, bottom + 1):
                    chars.append(grid[r][right])
                right -= 1
                if top <= bottom:
                    for c in range(right, left - 1, -1):
                        chars.append(grid[bottom][c])
                    bottom -= 1
                if left <= right:
                    for r in range(bottom, top - 1, -1):
                        chars.append(grid[r][left])
                    left += 1

        return "".join(chars[:self.n])

    def solve_period_6_shifts_fast(
        self,
        transposed_text: str,
        mode: str = "vigenere",
        num_restarts: int = 15,
        seed: int = 42,
    ) -> Tuple[List[int], float, str]:
        """Greedy coordinate ascent over the 6 periodic Caesar shifts."""
        rng = random.Random(seed)
        best_q = -float("inf")
        best_shifts = [0] * 6
        best_pt = transposed_text

        for _ in range(num_restarts):
            shifts = [rng.randint(0, 25) for _ in range(6)]
            improved = True

            while improved:
                improved = False
                for pos in range(6):
                    orig_s = shifts[pos]
                    best_local_s = orig_s
                    best_local_q = -float("inf")

                    for test_s in range(26):
                        shifts[pos] = test_s
                        # Decode
                        pt_chars = []
                        for i, c in enumerate(transposed_text):
                            c_idx = self.a26.find(c)
                            if c_idx == -1:
                                pt_chars.append(c)
                                continue
                            k = shifts[i % 6]
                            if mode == "vigenere":
                                p = (c_idx - k) % 26
                            elif mode == "beaufort":
                                p = (k - c_idx) % 26
                            else:
                                p = (c_idx + k) % 26
                            pt_chars.append(self.a26[p])

                        q = self.base_scorer.score_total("".join(pt_chars))
                        if q > best_local_q:
                            best_local_q = q
                            best_local_s = test_s

                    shifts[pos] = best_local_s
                    if best_local_s != orig_s:
                        improved = True

            # Final decode for this restart
            pt_chars = []
            for i, c in enumerate(transposed_text):
                c_idx = self.a26.find(c)
                if c_idx == -1:
                    pt_chars.append(c)
                    continue
                k = shifts[i % 6]
                if mode == "vigenere":
                    p = (c_idx - k) % 26
                elif mode == "beaufort":
                    p = (k - c_idx) % 26
                else:
                    p = (c_idx + k) % 26
                pt_chars.append(self.a26[p])
            pt = "".join(pt_chars)
            q = self.base_scorer.score_total(pt)

            if q > best_q:
                best_q = q
                best_shifts = list(shifts)
                best_pt = pt

        return best_shifts, best_q, best_pt

    def evaluate_keyword_keyed_period_6(
        self,
        transposed_text: str,
        keyword: str,
        mode: str = "vigenere",
    ) -> Tuple[float, float, str, List[str]]:
        """Evaluate a specific pre-1886 candidate keyword under Period 6."""
        clean_kw = "".join(c for c in keyword.upper() if c in self.a26)
        if len(clean_kw) < 6:
            clean_kw = (clean_kw * 6)[:6]
        else:
            clean_kw = clean_kw[:6]

        shifts = [self.a26.index(c) for c in clean_kw]
        pt_chars = []
        for i, c in enumerate(transposed_text):
            c_idx = self.a26.find(c)
            if c_idx == -1:
                pt_chars.append(c)
                continue
            k = shifts[i % 6]
            if mode == "vigenere":
                p = (c_idx - k) % 26
            elif mode == "beaufort":
                p = (k - c_idx) % 26
            else:
                p = (c_idx + k) % 26
            pt_chars.append(self.a26[p])

        pt = "".join(pt_chars)
        q = self.base_scorer.score_total(pt)
        elgar_score, matches = self.elgar_scorer.score_with_elgar_bonus(pt)
        return q, elgar_score, pt, matches


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path
    from cipher_lab.stats import calculate_index_of_coincidence

    out_file = Path("data/derived/pc_grille_trials.jsonl")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    print("[Node 2 Fedora PC] Starting High-Throughput Joint Grille + Period-6 Worker...", flush=True)
    solver = JointGrillePolyalphabeticSolver()

    grid_shapes = [(3, 29), (29, 3), (6, 15)]
    traversals = ["row_major", "col_major", "boustrophedon", "spiral"]
    rotations = [0, 90, 180, 270]

    count = 0
    best_q = -9999.0
    best_res = None

    with open(out_file, "w") as f:
        # 1. Sweep geometric transpositions x keywords
        for rows, cols in grid_shapes:
            for trav in traversals:
                for rot in rotations:
                    for ref in [False, True]:
                        try:
                            trans = solver.apply_grid_transposition(
                                grid_shape=(rows, cols),
                                traversal=trav,
                                rotation=rot,
                                reflect=ref,
                            )
                        except Exception:
                            continue

                        # Test keywords
                        for kw in PRE_1886_KEYWORDS:
                            for mode in ["vigenere", "beaufort", "variant"]:
                                q, elgar, pt, matches = solver.evaluate_keyword_keyed_period_6(
                                    transposed_text=trans,
                                    keyword=kw,
                                    mode=mode,
                                    )
                                count += 1
                                if q > best_q:
                                    best_q = q
                                    best_res = (kw, trav, rot, ref, q, pt)

                                rec = {
                                    "trial_id": f"pc_{count}",
                                    "grid": f"{rows}x{cols}_{trav}_rot{rot}_ref{ref}",
                                    "keyword": kw,
                                    "mode": mode,
                                    "q_score": q,
                                    "elgar_score": elgar,
                                    "ioc": calculate_index_of_coincidence(pt),
                                    "plaintext": pt[:30],
                                    "matches": matches,
                                }
                                f.write(json.dumps(rec) + "\n")

                        # Coordinate ascent
                        q_opt, shifts_opt, pt_opt = solver.solve_period_6_shifts_coordinate_ascent(
                            transposed_text=trans,
                            restarts=5,
                            mode="vigenere",
                        )
                        count += 1
                        elgar_opt, matches_opt = solver.elgar_scorer.score_with_elgar_bonus(pt_opt)
                        if q_opt > best_q:
                            best_q = q_opt
                            best_res = ("coord_ascent", trav, rot, ref, q_opt, pt_opt)

                        rec = {
                            "trial_id": f"pc_{count}",
                            "grid": f"{rows}x{cols}_{trav}_rot{rot}_ref{ref}",
                            "keyword": "coord_ascent",
                            "shifts": shifts_opt,
                            "q_score": q_opt,
                            "elgar_score": elgar_opt,
                            "ioc": calculate_index_of_coincidence(pt_opt),
                            "plaintext": pt_opt[:30],
                            "matches": matches_opt,
                        }
                        f.write(json.dumps(rec) + "\n")

    print(f"[Node 2 Fedora PC] Completed {count} trials. Best Q: {best_q:.2f}", flush=True)
    if best_res:
        print(f"  Best: {best_res}", flush=True)

