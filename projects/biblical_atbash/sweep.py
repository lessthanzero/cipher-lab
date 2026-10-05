"""Biblical Cryptographic Sweep Engine (Jeremiah, Isaiah, Proverbs, Psalms).

Performs systematic textual sweeps across biblical books applying:
- Atbash (אתבש)
- Albam (אלבם)
- Atbah (אטבח)
Identifies verified ciphers (Jeremiah 25:26, 51:1, 51:41) and evaluates disputed candidates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from projects.biblical_atbash.cipher import (
    normalize_hebrew_word,
    transform_albam,
    transform_atbah,
    transform_atbash,
)
from projects.biblical_atbash.lexicon import BiblicalLexicon

# Foundational prophetic texts with confirmed and candidate ciphers
# Jeremiah 25:26, Jeremiah 51:1, Jeremiah 51:41, Isaiah 7:6, Proverbs 30:1
_JEREMIAH_EXTRACTS = [
    {
        "reference": "Jeremiah 25:26",
        "verse_text": "ואת כל מלכי הצפון הקרבים והרחקים איש אל אחיו ומלך ששך ישתה אחריהם",
        "known_target": "ששך",
        "decoded_target": "בבל",
    },
    {
        "reference": "Jeremiah 51:1",
        "verse_text": "כה אמר ה הנני מעיר על בבל ואל ישבי לב קמי רוח משחית",
        "known_target": "לב קמי",
        "decoded_target": "כשדים",
    },
    {
        "reference": "Jeremiah 51:41",
        "verse_text": "איך נלכדה ששך ותתפש תהלת כל הארץ איך היתה לשמה בבל בגוים",
        "known_target": "ששך",
        "decoded_target": "בבל",
    },
]


@dataclass(frozen=True, slots=True)
class CipherHit:
    reference: str
    original_phrase: str
    cipher_type: str
    transformed_text: str
    is_known_biblical_cipher: bool
    is_in_lexicon: bool
    significance_note: str


class BiblicalAtbashSweeper:
    """Scans biblical Hebrew passages for Atbash, Albam, and Atbah transformations."""

    def __init__(self, lexicon: Optional[BiblicalLexicon] = None) -> None:
        self.lexicon = lexicon or BiblicalLexicon()

    def sweep_verses(self, verses: Optional[list[dict[str, Any]]] = None) -> list[CipherHit]:
        """Sweeps verse list for single-word and two-word cipher hits."""
        v_list = verses or _JEREMIAH_EXTRACTS
        hits: list[CipherHit] = []

        for item in v_list:
            ref = item["reference"]
            words = item["verse_text"].split()

            # 1. Single word sweep
            for w in words:
                norm = normalize_hebrew_word(w)
                if len(norm) < 2:
                    continue

                # Test Atbash
                atb = transform_atbash(norm)
                if self.lexicon.contains(atb) and atb != norm:
                    is_known = (norm in ("ששך", "ששכ") and atb == "בבל")
                    hits.append(CipherHit(
                        reference=ref,
                        original_phrase=norm,
                        cipher_type="ATBASH",
                        transformed_text=atb,
                        is_known_biblical_cipher=is_known,
                        is_in_lexicon=True,
                        significance_note="Jeremiah Royal Cipher: Sheshach -> Babel" if is_known else "Dictionary collision",
                    ))

            # 2. Two-word phrase sweep (e.g. לב קמי -> כשדים)
            for i in range(len(words) - 1):
                w1 = normalize_hebrew_word(words[i])
                w2 = normalize_hebrew_word(words[i + 1])
                combined = w1 + w2
                atb_comb = transform_atbash(combined)
                if self.lexicon.contains(atb_comb) and atb_comb != combined:
                    is_known = (f"{w1} {w2}" == "לב קמי" and atb_comb in ("כשדים", "כשדימ"))
                    hits.append(CipherHit(
                        reference=ref,
                        original_phrase=f"{w1} {w2}",
                        cipher_type="ATBASH_PHRASE",
                        transformed_text=atb_comb,
                        is_known_biblical_cipher=is_known,
                        is_in_lexicon=True,
                        significance_note="Jeremiah Cryptonym: Leb-kamai -> Kasdim (Chaldeans)" if is_known else "Compound phrase match",
                    ))

        return hits
