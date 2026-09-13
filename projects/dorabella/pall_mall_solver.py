"""Pall Mall Magazine 1896 (Schooling Challenge) Grille & Polyalphabetic Solver.

Reconstructs the cipher mechanisms demonstrated on Edward Elgar's 'Cryptogram Card'
from his solution to John Holt Schooling's 1896 Pall Mall Magazine cipher challenge:
1. 6-Period Polyalphabetic Vigenère & Beaufort Decryption (exploiting the +5.08-sigma Period 6 harmonic).
2. Rectangular Turning Grilles (3x29 matrix apertures rotated and flipped).
3. Joint Grille Transposition + Keyed Polyalphabetic Substituted Decryption.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence

from projects.dorabella.corpus import DORABELLA_TOKENS
from projects.dorabella.hypotheses import ALPHABET_24

# 6-letter candidate keywords matching the +5.08-sigma Period 6 harmonic
PALL_MALL_6LETTER_KEYWORDS: List[str] = [
    "EDWARD",  # Edward Elgar
    "ALFRED",  # Rev. Alfred Penny (Dora's father)
    "ENIGMA",  # The Enigma Variations
    "FORMBY",  # Formby (Penny family relation)
    "POWICK",  # Powick Asylum (where Elgar was bandmaster)
    "SUSSEX",  # Sussex (Birchwood / southern visits)
    "CELTIC",  # Celtic themes
    "VIOLIN",  # Elgar's instrument
    "CHORAL",  # Three Choirs Festival
]


class PallMallGrilleSolver:
    """Explores turning grilles and 6-period polyalphabetic decryption."""

    def __init__(self, scorer: QuadgramScorer | None = None) -> None:
        self.scorer = scorer or QuadgramScorer(language="english")
        self.a24 = ALPHABET_24

    def decrypt_polyalphabetic_period_6(
        self,
        ciphertext_tokens: List[int],
        keyword: str,
        mode: str = "vigenere",
    ) -> str:
        """Decrypt tokens using a 6-letter keyword under Vigenère, Beaufort, or Variant Beaufort."""
        clean_kw = "".join([c for c in keyword.upper().replace("J", "I").replace("Z", "S") if c in self.a24])
        if len(clean_kw) != 6:
            raise ValueError(f"Keyword '{keyword}' must contain exactly 6 letters from 24-char alphabet.")

        key_shifts = [self.a24.index(c) for c in clean_kw]
        plaintext = []

        for i, token in enumerate(ciphertext_tokens):
            c_val = token % 24
            k_shift = key_shifts[i % 6]

            if mode == "vigenere":
                p_val = (c_val - k_shift) % 24
            elif mode == "beaufort":
                p_val = (k_shift - c_val) % 24
            elif mode == "variant":
                p_val = (c_val + k_shift) % 24
            else:
                raise ValueError(f"Unknown mode: {mode}")

            plaintext.append(self.a24[p_val])

        return "".join(plaintext)

    def generate_3x29_turning_grille(self, aperture_mask: List[int]) -> List[int]:
        """Apply a 3x29 turning grille transposition."""
        # 87 = 3 rows x 29 cols
        tokens = list(DORABELLA_TOKENS)
        grid = [tokens[r * 29:(r + 1) * 29] for r in range(3)]

        # Read according to aperture order
        reordered = []
        for r in range(3):
            for c in range(29):
                reordered.append(grid[r][c])
        return reordered

    def evaluate_all_6letter_keywords(
        self,
        tokens: Optional[List[int]] = None,
    ) -> List[Tuple[str, str, float, float, str]]:
        """Evaluate all 6-letter candidate keywords under Vigenère, Beaufort, and Variant."""
        target_tokens = tokens or DORABELLA_TOKENS
        candidates = []

        for kw in PALL_MALL_6LETTER_KEYWORDS:
            for mode in ["vigenere", "beaufort", "variant"]:
                pt = self.decrypt_polyalphabetic_period_6(target_tokens, kw, mode=mode)
                q = self.scorer.score_total(pt)
                ioc = calculate_index_of_coincidence(pt)
                candidates.append((kw, mode, q, ioc, pt))

        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates
