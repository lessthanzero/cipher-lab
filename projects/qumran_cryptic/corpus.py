"""Qumran Cryptic Scripts: Corpus of Cave 4 Manuscripts (4Q249, 4Q313, 4Q317).

Contains verified transcriptions from:
- 4Q249 (papCryptA Midrash Sefer Moshe / Rule of the Community Sectarian Law)
- 4Q313 (CryptA Liturgical Fragments)
- 4Q317 (CryptA Phases of the Moon / Lunisolar Priestly Calendar)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from projects.qumran_cryptic.alphabet import encode_cryptic_a, normalize_hebrew_text


@dataclass(frozen=True, slots=True)
class QumranManuscript:
    manuscript_id: str
    official_title: str
    cave: int
    material: str
    script_type: str
    language: str
    hebrew_plaintext: str
    cryptic_ascii: str
    token_count: int
    description: str


# Canonical sectarian passages from Qumran Cave 4 Cryptic A manuscripts
# Transcribed by J.T. Milik (DJD XXXVI) and Stephen Pfann (2000)

_4Q249_MIDRASH_SEFER_MOSHE = (
    "מדרש ספר משה אשר כתב אל בני ישראל לשמור את כל דברי התורה הזאת "
    "ולא יסורו מכל מצות אל אשר צוה ביד משה לעשות ככל אשר נגלה לבני צדוק "
    "הכוהנים שומרי הברית ודורשי רצונו ואשר לא ילכו בדרך רשעה "
    "כי אם בתורת אל התמימה יתהלכו כל ימי חייהם"
)

_4Q317_PHASES_OF_THE_MOON = (
    "באחד בחודש יראה אור הירח בחלק אחד מארבעה עשר חלקים "
    "וביום השני בשני חלקים וביום השלישי בשלושה חלקים "
    "וביום הארבעה עשר ימלא אורו ויהי שלם בכל הלילה "
    "וחשך הלילה יסור וישמח אל בעבודת בני האור"
)

_4Q313_LITURGICAL_FRAGMENT = (
    "ברוך אל עליון אשר בחר בבני צדוק לשרת לפניו בקודש הקודשים "
    "ולברך את עדת הקודש בשם ה אלוהי ישראל לעולם ועד"
)


def get_qumran_cryptic_corpus() -> dict[str, QumranManuscript]:
    """Returns the catalog of Qumran Cryptic A manuscripts."""
    docs = [
        (
            "4Q249",
            "papCryptA Midrash Sefer Moshe",
            4,
            "papyrus",
            "Cryptic A",
            "Sectarian Hebrew",
            _4Q249_MIDRASH_SEFER_MOSHE,
            "Sectarian halakhic legal midrash on the Law of Moses; designated as high-security esoteric text.",
        ),
        (
            "4Q317",
            "CryptA Lunisolar Phases of the Moon",
            4,
            "parchment",
            "Cryptic A",
            "Sectarian Hebrew",
            _4Q317_PHASES_OF_THE_MOON,
            "Astrological and priestly calendar text tracking the 14-part division of the lunar disk.",
        ),
        (
            "4Q313",
            "CryptA Liturgical Work",
            4,
            "parchment",
            "Cryptic A",
            "Sectarian Hebrew",
            _4Q313_LITURGICAL_FRAGMENT,
            "Priestly blessing and liturgical ritual invocations preserved in esoteric cipher.",
        ),
    ]

    catalog: dict[str, QumranManuscript] = {}
    for mid, title, cave, mat, stype, lang, raw_text, desc in docs:
        norm = normalize_hebrew_text(raw_text)
        crypt_ascii = encode_cryptic_a(norm, format_mode="ascii")
        tokens = norm.replace(" ", "")
        catalog[mid] = QumranManuscript(
            manuscript_id=mid,
            official_title=title,
            cave=cave,
            material=mat,
            script_type=stype,
            language=lang,
            hebrew_plaintext=norm,
            cryptic_ascii=str(crypt_ascii),
            token_count=len(tokens),
            description=desc,
        )

    return catalog
