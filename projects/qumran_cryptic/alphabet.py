"""Qumran Cryptic Scripts: Alphabet & Character Mappings (Cryptic A, B, C).

Based on epigraphic transcriptions by J.T. Milik (1956) and Stephen Pfann (2000):
- Cryptic A: 22-letter monoalphabetic substitution cipher for standard square Hebrew/Aramaic.
- Used in 4Q249 (papCryptA Midrash Sefer Moshe), 4Q313, 4Q317 (Lunisolar Calendar).
- Cryptic B & C: Fragmentary secondary esoteric sectarian scripts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Standard 22 consonantal Hebrew letters
HEBREW_ALPHABET = (
    "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ",
    "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ק", "ר", "ש", "ת",
)

HEBREW_LETTER_NAMES = {
    "א": "Alef", "ב": "Bet", "ג": "Gimel", "ד": "Dalet", "ה": "He",
    "ו": "Vav", "ז": "Zayin", "ח": "Het", "ט": "Tet", "י": "Yod",
    "כ": "Kaf", "ל": "Lamed", "מ": "Mem", "נ": "Nun", "ס": "Samekh",
    "ע": "Ayin", "פ": "Pe", "צ": "Tsade", "ק": "Qof", "ר": "Resh",
    "ש": "Shin", "ת": "Tav",
}

# Final forms mapping to standard forms
FINAL_TO_STANDARD = {
    "ך": "כ",
    "ם": "מ",
    "ן": "נ",
    "ף": "פ",
    "ץ": "צ",
}

# Cryptic A Character Symbolic Tokens (Stephen Pfann 2000 standard notation)
CRYPTIC_A_TOKENS = (
    "cA_alf", "cA_bet", "cA_gml", "cA_dlt", "cA_he", "cA_vav", "cA_zayn",
    "cA_het", "cA_tet", "cA_yod", "cA_kaf", "cA_lmd", "cA_mem", "cA_nun",
    "cA_smk", "cA_ayn", "cA_pe", "cA_tsd", "cA_qof", "cA_rsh", "cA_shn", "cA_tav",
)

# Cryptic A Unicode/ASCII Shorthand representation for high-density analysis
CRYPTIC_A_ASCII = (
    "α", "β", "γ", "δ", "ε", "ϝ", "ζ",
    "η", "θ", "ι", "κ", "λ", "μ", "ν",
    "ξ", "ο", "π", "ψ", "ϙ", "ρ", "σ", "τ",
)

# Bijection Maps
HEBREW_TO_CRYPTIC_A: dict[str, str] = dict(zip(HEBREW_ALPHABET, CRYPTIC_A_TOKENS))
CRYPTIC_A_TO_HEBREW: dict[str, str] = {v: k for k, v in HEBREW_TO_CRYPTIC_A.items()}

HEBREW_TO_CRYPTIC_A_ASCII: dict[str, str] = dict(zip(HEBREW_ALPHABET, CRYPTIC_A_ASCII))
CRYPTIC_A_ASCII_TO_HEBREW: dict[str, str] = {v: k for k, v in HEBREW_TO_CRYPTIC_A_ASCII.items()}


def normalize_hebrew_text(text: str) -> str:
    """Normalizes Hebrew text: strips niqqud, converts final forms, retains 22 consonants and spaces."""
    normalized = []
    for ch in text:
        # Check final form
        std = FINAL_TO_STANDARD.get(ch, ch)
        if std in HEBREW_ALPHABET:
            normalized.append(std)
        elif ch in (" ", "\n", "\t"):
            normalized.append(" ")
    # Collapse multiple spaces
    return " ".join("".join(normalized).split())


def encode_cryptic_a(hebrew_text: str, format_mode: str = "tokens") -> list[str] | str:
    """Encodes normalized Hebrew text into Cryptic A characters."""
    norm = normalize_hebrew_text(hebrew_text)
    if format_mode == "ascii":
        return "".join(HEBREW_TO_CRYPTIC_A_ASCII.get(ch, ch) for ch in norm)
    tokens = []
    for word in norm.split():
        word_tokens = [HEBREW_TO_CRYPTIC_A[ch] for ch in word if ch in HEBREW_TO_CRYPTIC_A]
        if word_tokens:
            tokens.append(word_tokens)
    return tokens


def decode_cryptic_a(cryptic_tokens: list[str] | str) -> str:
    """Decodes Cryptic A tokens or ASCII shorthand back into standard consonantal Hebrew."""
    if isinstance(cryptic_tokens, str):
        # ASCII shorthand
        return "".join(CRYPTIC_A_ASCII_TO_HEBREW.get(ch, ch) for ch in cryptic_tokens)
    # List of tokens
    return "".join(CRYPTIC_A_TO_HEBREW.get(tok, "?") for tok in cryptic_tokens)
