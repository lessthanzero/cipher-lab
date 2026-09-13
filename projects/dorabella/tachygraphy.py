"""Tachygraphic & Shorthand Analysis for the Dorabella Cipher (1897).

Tests the hypothesis that Edward Elgar's semicircular strokes derive from 19th-century
British shorthand systems (Samuel Taylor's Universal Stenography or Isaac Pitman's Phonography).
In geometric tachygraphy:
- Curves facing 8 orientations represent basic consonant strokes (P/B, T/D, CH/J, K/G, F/V, TH, S/Z, SH/ZH).
- 1, 2, or 3 humps represent consonant gemination, attached vowels, or word-ending affixes (-ING, -TION, -MENT).
"""

from __future__ import annotations

from typing import Dict, Tuple

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence

from projects.dorabella.corpus import DORABELLA_TOKENS

# Samuel Taylor's Universal Stenography (1786, widely used in Victorian England)
# 8 orientations of curves:
TAYLOR_CONSONANT_MAP: Dict[int, str] = {
    0: "T",   # East horizontal curve
    1: "R",   # North-East diagonal curve
    2: "P",   # North vertical curve
    3: "CH",  # North-West diagonal curve
    4: "K",   # West horizontal curve
    5: "M",   # South-West diagonal curve
    6: "F",   # South vertical curve
    7: "S",   # South-East diagonal curve
}

# Isaac Pitman Phonography (1837) curve orientations:
PITMAN_CONSONANT_MAP: Dict[int, str] = {
    0: "N",   # Horizontal arc open down
    1: "R",   # Upward right curve
    2: "T",   # Vertical stroke
    3: "CH",  # Downward left stroke
    4: "M",   # Horizontal arc open up
    5: "L",   # Upward left curve
    6: "F",   # Downward right curve
    7: "S",   # Vertical arc open left
}

# Suffix expansions based on hump count
HUMP_SUFFIX_MAP: Dict[int, str] = {
    1: "",        # Base consonant
    2: "E",       # Consonant + common vowel
    3: "ING",     # Consonant + continuous participle affix
}


class TachygraphicEvaluator:
    """Evaluates shorthand and phonographic reconstructions of Dorabella."""

    def __init__(self, scorer: QuadgramScorer | None = None) -> None:
        self.scorer = scorer or QuadgramScorer(language="english")
        self.tokens = DORABELLA_TOKENS

    def decode_taylor_stenography(self) -> str:
        """Decode tokens using Taylor shorthand curve-to-consonant mapping."""
        decoded = []
        for t in self.tokens:
            ori = t % 8
            humps = (t // 8) + 1
            base = TAYLOR_CONSONANT_MAP.get(ori, "X")
            suffix = HUMP_SUFFIX_MAP.get(humps, "")
            decoded.append(base + suffix)
        return "".join(decoded)

    def decode_pitman_phonography(self) -> str:
        """Decode tokens using Pitman phonography curve-to-consonant mapping."""
        decoded = []
        for t in self.tokens:
            ori = t % 8
            humps = (t // 8) + 1
            base = PITMAN_CONSONANT_MAP.get(ori, "X")
            suffix = HUMP_SUFFIX_MAP.get(humps, "")
            decoded.append(base + suffix)
        return "".join(decoded)

    def evaluate_tachygraphic_hypotheses(self) -> Dict[str, Tuple[float, float, str]]:
        """Evaluate both Taylor and Pitman models against quadgram statistics."""
        results = {}
        for name, text in [
            ("H_shorthand_taylor", self.decode_taylor_stenography()),
            ("H_shorthand_pitman", self.decode_pitman_phonography()),
        ]:
            clean_text = "".join(c for c in text.upper() if c.isalpha())
            q = self.scorer.score_total(clean_text)
            ioc = calculate_index_of_coincidence(clean_text)
            results[name] = (q, ioc, clean_text)
        return results
