"""Curated Classical Biblical Hebrew Lexicon & Proper Noun Dictionary.

Contains standard Biblical Hebrew roots, lemmas, and attested geographic/proper names:
- Standard toponyms (בבל Babel, כשדים Chaldeans, ירושלים Jerusalem, מצרים Egypt, etc.)
- Core Biblical Hebrew nouns, verbs, and grammatical morphemes.
"""

from __future__ import annotations

from typing import Set

from projects.biblical_atbash.cipher import normalize_hebrew_word

# Foundational Biblical Hebrew lexicon (nouns, verbs, proper names, toponyms)
# Compiled from Brown-Driver-Briggs (BDB) and Koehler-Baumgartner (HALOT)
_BIBLICAL_HEBREW_LEMMAS = {
    # Toponyms & Nations
    "בבל", "כשדים", "מצרים", "אשור", "פרס", "יון", "צידון", "צור", "עזה", "אדום",
    "מואב", "עמון", "ארם", "שומרון", "ירושלם", "יהודה", "ישראל", "גלעד", "בשן",
    "לבנון", "חרמון", "ירדן", "כינרת", "סיני", "חורב", "שילה", "חברון", "ביתאל",

    # Key Proper Names
    "משה", "אהרן", "דוד", "שלמה", "אברהם", "יצחק", "יעקב", "יוסף", "יהושע", "שמואל",
    "שאול", "אליהו", "אלישע", "ישעיהו", "ירמיהו", "יחזקאל", "דניאל", "הושע", "עמוס",
    "מיכה", "צדקיהו", "נבוכדנאצר", "כורש", "אחשוורוש", "המן", "מרדכי", "אסתר",

    # High-frequency Biblical Nouns & Verbs
    "אב", "אם", "אח", "אחות", "בן", "בת", "איש", "אשה", "אדם", "אל", "אלהים",
    "אדון", "מלך", "שר", "כהן", "נביא", "שופט", "עבד", "אדון", "גוי", "עם",
    "עיר", "בית", "ארץ", "שמים", "ים", "נהר", "הר", "גבעה", "מדבר", "שדה",
    "עץ", "פרי", "זרע", "לחם", "מים", "יין", "שמן", "דם", "בשר", "עצם",
    "ראש", "עין", "אוזן", "פה", "לשון", "יד", "רגל", "לב", "נפש", "רוח",
    "חיים", "מות", "אור", "חשך", "יום", "לילה", "בקר", "ערב", "חדש", "שנה",
    "עת", "שלום", "מלחמה", "חרב", "קשת", "חנית", "מגן", "חומה", "שער", "דרך",
    "משפט", "צדקה", "חסד", "אמת", "ברית", "תורה", "מצוה", "חוק", "ספר", "דבר",
    "קול", "שם", "כבוד", "קודש", "עולם", "טוב", "רע", "גדול", "קטן", "קדוש",

    # Verbs (3-letter root consonants)
    "אמר", "דבר", "עשה", "ראה", "שמע", "הלך", "בוא", "יצא", "ישב", "נתן",
    "לקח", "ידע", "מצא", "עלה", "ירד", "שלח", "קרא", "עמד", "נפל", "קם",
    "כתב", "שמר", "זכר", "שפט", "מלך", "עבד", "אהב", "שנא", "ירא", "ברך",
    "כרת", "בנה", "חרב", "שרף", "שבר", "אסף", "פתח", "סגר", "חטא", "כפר",
}


class BiblicalLexicon:
    """Manages normalized consonantal dictionary for Hebrew cryptanalysis."""

    def __init__(self, additional_words: Set[str] | None = None) -> None:
        self.words: set[str] = set()
        for w in _BIBLICAL_HEBREW_LEMMAS:
            norm = normalize_hebrew_word(w)
            if norm:
                self.words.add(norm)
        if additional_words:
            for w in additional_words:
                norm = normalize_hebrew_word(w)
                if norm:
                    self.words.add(norm)

    def contains(self, word: str) -> bool:
        """Checks if a normalized word exists in the biblical lexicon."""
        return normalize_hebrew_word(word) in self.words

    def __len__(self) -> int:
        return len(self.words)
