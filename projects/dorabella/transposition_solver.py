"""Transposition & Pall Mall Grille Solver for Dorabella Cipher.

Explores transposition architectures inspired by Elgar's solution to the
1896 Pall Mall Magazine cryptographic contest (Schooling's Challenge):
- Rectangular matrix factorization: 87 = 3 x 29 or 29 x 3.
- Boustrophedon / serpentine row reading.
- Columnar transposition keyed by holistic 1897 keywords (MALVERN, JUBILEE, DORABELLA, FORLI).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence

from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.symbols import decode_tokens


class DorabellaTranspositionSolver:
    """Explores transposition permutations prior to or following symbol decoding."""

    def __init__(self, tokens: List[int] | None = None) -> None:
        self.tokens = tokens or DORABELLA_TOKENS
        self.n = len(self.tokens)

    def vertical_columnar_read_3x29(self) -> List[int]:
        """Read 3x29 matrix vertically down columns."""
        # 3 rows, 29 columns
        grid = [self.tokens[r * 29:(r + 1) * 29] for r in range(3)]
        reordered = []
        for c in range(29):
            for r in range(3):
                reordered.append(grid[r][c])
        return reordered

    def boustrophedon_read(self) -> List[int]:
        """Read lines alternating left-to-right and right-to-left."""
        from projects.dorabella.corpus import LINE_1_TOKENS, LINE_2_TOKENS, LINE_3_TOKENS
        # Line 1: L->R, Line 2: R->L, Line 3: L->R
        return list(LINE_1_TOKENS) + list(reversed(LINE_2_TOKENS)) + list(LINE_3_TOKENS)

    def columnar_keyword_transposition(self, keyword: str) -> List[int]:
        """Apply columnar transposition under keyword ranking (e.g. MALVERN)."""
        k_len = len(keyword)
        # Pad tokens to multiple of k_len if needed
        rows = (self.n + k_len - 1) // k_len
        padded = list(self.tokens) + [0] * (rows * k_len - self.n)

        # Build grid
        grid = [padded[r * k_len:(r + 1) * k_len] for r in range(rows)]

        # Keyword alphabetical ordering
        key_order = sorted(range(k_len), key=lambda i: (keyword[i], i))

        reordered = []
        for col in key_order:
            for r in range(rows):
                idx = r * k_len + col
                if idx < self.n:
                    reordered.append(grid[r][col])
        return reordered

    def evaluate_transposition_candidates(
        self,
        mapping: Dict[int, str],
        scorer: QuadgramScorer,
        keywords: List[str],
    ) -> List[Tuple[str, float, float, str]]:
        """Evaluate structural transposition variants decoded with candidate mapping."""
        candidates = []

        # 1. Baseline untransposed
        pt_base = decode_tokens(self.tokens, mapping)
        q_base = scorer.score_total(pt_base)
        ioc_base = calculate_index_of_coincidence(pt_base)
        candidates.append(("untransposed", q_base, ioc_base, pt_base))

        # 2. 3x29 vertical read
        t_vert = self.vertical_columnar_read_3x29()
        pt_vert = decode_tokens(t_vert, mapping)
        q_vert = scorer.score_total(pt_vert)
        ioc_vert = calculate_index_of_coincidence(pt_vert)
        candidates.append(("vertical_3x29", q_vert, ioc_vert, pt_vert))

        # 3. Boustrophedon
        t_boust = self.boustrophedon_read()
        pt_boust = decode_tokens(t_boust, mapping)
        q_boust = scorer.score_total(pt_boust)
        ioc_boust = calculate_index_of_coincidence(pt_boust)
        candidates.append(("boustrophedon", q_boust, ioc_boust, pt_boust))

        # 4. Keyword transpositions
        for kw in keywords:
            t_kw = self.columnar_keyword_transposition(kw)
            pt_kw = decode_tokens(t_kw, mapping)
            q_kw = scorer.score_total(pt_kw)
            ioc_kw = calculate_index_of_coincidence(pt_kw)
            candidates.append((f"columnar_{kw}", q_kw, ioc_kw, pt_kw))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
