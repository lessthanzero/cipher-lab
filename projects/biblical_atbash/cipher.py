"""Classical Biblical Hebrew Cryptographic Transformations: Atbash, Albam, and Atbah.

Implements standard rabbinic and scribal substitution cipher systems:
1. Atbash (אתבש): Inversion across the 22-letter consonantal Hebrew alphabet.
   - Letter index i maps to 21 - i.
   - Prototypical Biblical instances:
       Jeremiah 25:26 & 51:41: ששך (Sheshach) <-> בבל (Babel)
       Jeremiah 51:1: לב קמי (Leb-kamai) <-> כשדים (Chaldeans / Kasdim)
2. Albam (אלבם): Split-half Caesar cipher.
   - Letter index i maps to (i + 11) mod 22.
3. Atbah (אטבח): Decimal arithmetic cipher based on gematria pairings summing to 10 or 100.
   - Single units: 1+9 (א-ט), 2+8 (ב-ח), 3+7 (ג-ז), 4+6 (ד-ו), 5 (ה, unpaired/identity).
   - Tens units: 10+90 (י-צ), 20+80 (כ-פ), 30+70 (ל-ע), 40+60 (מ-ס), 50 (נ, unpaired/identity).
   - Hundreds units: 100+400 (ק-ת), 200+300 (ר-ש).
"""

from __future__ import annotations

from typing import Dict, List, Optional

HEBREW_ALPHABET = (
    "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ",
    "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ק", "ר", "ש", "ת",
)

FINAL_TO_STANDARD = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

# 1. Atbash Mapping: i <-> 21 - i
ATBASH_MAP: dict[str, str] = {
    HEBREW_ALPHABET[i]: HEBREW_ALPHABET[21 - i]
    for i in range(22)
}

# 2. Albam Mapping: i <-> (i + 11) % 22
ALBAM_MAP: dict[str, str] = {
    HEBREW_ALPHABET[i]: HEBREW_ALPHABET[(i + 11) % 22]
    for i in range(22)
}

# 3. Atbah Mapping (Gematria sum-to-10 and sum-to-100)
ATBAH_MAP: dict[str, str] = {
    # Units (sum to 10)
    "א": "ט", "ט": "א",
    "ב": "ח", "ח": "ב",
    "ג": "ז", "ז": "ג",
    "ד": "ו", "ו": "ד",
    "ה": "ה",  # 5 is identity
    # Tens (sum to 100)
    "י": "צ", "צ": "י",
    "כ": "פ", "פ": "כ",
    "ל": "ע", "ע": "ל",
    "מ": "ס", "ס": "מ",
    "נ": "נ",  # 50 is identity
    # Hundreds (sum to 500)
    "ק": "ת", "ת": "ק",
    "ר": "ש", "ש": "ר",
}


def normalize_hebrew_word(word: str) -> str:
    """Strips vowels/cantillation and maps final letters to standard letters."""
    norm = []
    for ch in word:
        std = FINAL_TO_STANDARD.get(ch, ch)
        if std in ATBASH_MAP:
            norm.append(std)
    return "".join(norm)


def transform_atbash(text: str) -> str:
    """Applies Atbash cipher (self-inverse)."""
    return "".join(ATBASH_MAP.get(FINAL_TO_STANDARD.get(ch, ch), ch) for ch in text)


def transform_albam(text: str) -> str:
    """Applies Albam cipher (self-inverse)."""
    return "".join(ALBAM_MAP.get(FINAL_TO_STANDARD.get(ch, ch), ch) for ch in text)


def transform_atbah(text: str) -> str:
    """Applies Atbah cipher (self-inverse)."""
    return "".join(ATBAH_MAP.get(FINAL_TO_STANDARD.get(ch, ch), ch) for ch in text)
