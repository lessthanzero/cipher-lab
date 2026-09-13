"""Authentic 1886 Liszt Fragment Corpus & Dual-Corpus Cross-Validation.

Historical Provenance:
- Source: Crystal Palace Nineteenth Saturday Concert Programme, April 1886, page 546.
- Work: Franz Liszt's Symphonic Poem No. 3, 'Les Préludes' (S.97).
- Analyst/Annotator: Programme notes by Charles Ainslie Barry [C. A. B.].
- Physical Inscription: Edward Elgar drew a vertical bracket in the left margin
  encompassing Section No. 5 ('Allegro ma non troppo', development of 1st subject)
  and Section No. 6 ('Allegretto pastorale' with harp & horn 'Arpa. Corno.',
  combined with the 'second subject').
- Layout: 18 semicircular glyphs grouped into 4 distinct words (lengths 3, 6, 3, 6),
  terminated by a trailing underscore '_'.

Epistemic Significance:
1. Chronological Negative Control: Pinned to April 1886, 11 years prior to Dorabella (July 1897).
   Dora Penny was an 11-year-old schoolgirl in Melanesia/England whom Elgar had never met.
   All personal/biographical terms post-1886 (DORA, PENNY, WOLVERHAMPTON, ENIGMA) are falsified
   as base alphabet keys.
2. Script Identity: Employs the identical 1, 2, and 3-hump semicircular geometry in 8 compass
   orientations as Dorabella.
3. Dual-Corpus Validation: Any true decryption key K for the Elgar semicircular alphabet must
   yield coherent plaintexts on both the 1886 Liszt fragment and the 1897 Dorabella cipher.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Authentic 1886 Liszt Fragment Transcriptions
# Word 1 (3 chars): B [M3-up/down] K (3 humps right, 3 humps down, 2 humps up)
# Word 2 (6 chars): 1 hump up, 2 humps up, 2 humps up, 1 hump down, 1 hump NE, 2 humps down
# Word 3 (3 chars): 3 humps down, 1 hump down, 1 hump up
# Word 4 (6 chars): 2 humps up, 2 humps down, 3 humps right, 2 humps up, 1 hump down, 1 hump down
# Underscore: '_'

LISZT_1886_WORDS: List[str] = [
    "BMK",          # Word 1 (3 glyphs)
    "GKKOIM",       # Word 2 (6 glyphs)
    "MCG",          # Word 3 (3 glyphs)
    "KMBKCC",       # Word 4 (6 glyphs)
]

LISZT_1886_RAW = "".join(LISZT_1886_WORDS)  # 18 glyphs
LISZT_1886_WORD_LENGTHS = [3, 6, 3, 6]
LISZT_HAS_TRAILING_UNDERSCORE = True


@dataclass(frozen=True)
class LisztFragmentMetadata:
    date: str = "1886-04-10"
    venue: str = "Crystal Palace, Sydenham, London"
    concert: str = "Nineteenth Saturday Concert (30th Season)"
    page: int = 546
    composer: str = "Franz Liszt"
    piece: str = "Les Préludes, Symphonic Poem No. 3 (S.97)"
    programme_annotator: str = "Charles Ainslie Barry [C. A. B.]"
    adjacent_sections: Tuple[str, ...] = (
        "No. 5. Allegro ma non troppo (working out section, 1st subject)",
        "No. 6. Allegretto pastorale (Arpa. Corno., combined with 2nd subject)",
    )
    glyph_count: int = 18
    word_lengths: Tuple[int, ...] = (3, 6, 3, 6)
    has_underscore: bool = True


LISZT_METADATA = LisztFragmentMetadata()


def evaluate_dual_corpus(
    key_mapping: Dict[str, str],
    dorabella_ciphertext: str,
    liszt_words: Optional[List[str]] = None,
) -> Dict[str, object]:
    """Decode both Dorabella and Liszt using candidate key mapping and compute dual fitness."""
    if liszt_words is None:
        liszt_words = LISZT_1886_WORDS

    # Decode Dorabella
    dorabella_pt = "".join(key_mapping.get(c, "?") for c in dorabella_ciphertext)

    # Decode Liszt words
    liszt_decoded_words = [
        "".join(key_mapping.get(c, "?") for c in w)
        for w in liszt_words
    ]
    liszt_pt = " ".join(liszt_decoded_words) + "_"

    return {
        "dorabella_plaintext": dorabella_pt,
        "liszt_plaintext": liszt_pt,
        "liszt_words": liszt_decoded_words,
        "key_coverage_dorabella": sum(1 for c in dorabella_ciphertext if c in key_mapping) / len(dorabella_ciphertext),
        "key_coverage_liszt": sum(1 for w in liszt_words for c in w if c in key_mapping) / 18,
    }
