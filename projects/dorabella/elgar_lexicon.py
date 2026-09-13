"""Elgarian Personal Lexicon, Latin Liturgy, and Dialect n-Gram Booster.

Enriches standard English language models with Edward Elgar's personal vocabulary,
including:
1. "Elgar-Speak" wordplay, spoonerisms, and phonetic dialect (BCOS, ALLITE, WOT, XCUSE).
2. Family, friend, and musical nicknames (DORABELLA, BRAUT, NIMROD, CARICE, EDWARD, E.E.).
3. Roman Catholic liturgical and Latin choral phrases (AMDG, LDS, AVE, GLORIA, CREDO, DEUS).
4. Canine and natural science terms (DAN, BULLDOG, WYE, ARK, SULPHUR, ACID, KITE).
5. Worcestershire and Malvern geographical toponyms (FORLI, MALVERN, SEVERN, HASFIELD, POWICK).
"""

from __future__ import annotations

from typing import List, Set

from cipher_lab.stats import QuadgramScorer

# Elgar's frequent personal nicknames and intimacies
ELGAR_PERSONAL_NAMES: List[str] = [
    "DORABELLA", "DORA", "PENNY", "EDWARD", "ELGAR", "EE", "ED",
    "ALICE", "CARICE", "BRAUT", "NIMROD", "JAEGER", "TROYTE",
    "BAKER", "SINCLAIR", "ALFRED", "MARY", "ROBERTS",
]

# Sacred Latin liturgical vocabulary (Elgar was organist at St George's RC Church, Worcester)
LATIN_LITURGICAL_WORDS: List[str] = [
    "AMDG",  # Ad maiorem Dei gloriam (inscribed on almost every score)
    "LDS",   # Laus Deo Semper
    "DEUS", "DOMINUS", "CHRISTUS", "MARIA", "AVE", "GLORIA",
    "CREDO", "SANCTUS", "BENEDICTUS", "REQUIEM", "SALVE",
    "LUX", "PACEM", "AGNUS", "DEI", "MISERERE",
]

# Geographical toponyms from Elgar's Worcestershire / Gloucestershire world
ELGAR_TOPONYMS: List[str] = [
    "FORLI", "MALVERN", "GREATMALVERN", "LINK", "SEVERN", "TEME",
    "WOLVERHAMPTON", "RECTORY", "HASFIELD", "POWICK", "BROADHEATH",
    "BIRCHWOOD", "BEACON", "WORCESTER", "GLOUCESTER", "HEREFORD",
]

# Canine, kite, and chemistry shed terms
ELGAR_NATURAL_SCIENCES: List[str] = [
    "DAN", "BULLDOG", "PADDLE", "BARK", "RIVERWYE", "WYE",
    "ARK", "SULPHUR", "ACID", "RETORT", "KITE", "BIRD", "CURLEW",
]

# "Elgar-Speak" humorous phonetic spellings and archaic phrases
ELGAR_SPEAK_TERMS: List[str] = [
    "BCOS", "ALLITE", "XCUSE", "WOT", "CHIPS", "ROT", "RATS",
    "ENIGMA", "VARIATION", "INTERMEZZO", "THEME", "MUSIC", "NOTES",
]

# Combined comprehensive Elgarian lexicon
FULL_ELGARIAN_LEXICON: List[str] = sorted(list(set(
    ELGAR_PERSONAL_NAMES +
    LATIN_LITURGICAL_WORDS +
    ELGAR_TOPONYMS +
    ELGAR_NATURAL_SCIENCES +
    ELGAR_SPEAK_TERMS
)))


class ElgarLexiconScorer:
    """Evaluates candidate plaintexts with bonus weights for Elgarian personal context."""

    def __init__(self, base_scorer: QuadgramScorer | None = None) -> None:
        self.base_scorer = base_scorer or QuadgramScorer(language="english")
        self.lexicon: Set[str] = set(FULL_ELGARIAN_LEXICON)

    def find_lexicon_matches(self, text: str, min_len: int = 3) -> List[str]:
        """Find all matching Elgarian keywords within the candidate text."""
        upper = text.upper()
        matches = []
        for word in self.lexicon:
            if len(word) >= min_len and word in upper:
                matches.append(word)
        return matches

    def score_with_elgar_bonus(
        self,
        text: str,
        bonus_per_word: float = 30.0,
        min_word_len: int = 3,
    ) -> tuple[float, List[str]]:
        """Calculate base quadgram score augmented by Elgarian lexicon bonuses."""
        clean_text = "".join(c for c in text.upper() if c.isalpha())
        base_score = self.base_scorer.score_total(clean_text)
        matches = self.find_lexicon_matches(clean_text, min_len=min_word_len)
        bonus = len(matches) * bonus_per_word
        return base_score + bonus, matches
