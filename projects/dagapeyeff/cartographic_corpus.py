"""1939 British Ordnance Survey & D'Agapeyeff Cartographic Corpus.

Curates authentic 1939 cartographic terminology, British Retriangulation references,
and Russian Nihilist cipher indicator vocabulary.
"""

from __future__ import annotations

# 1. 1939 British Ordnance Survey & Retriangulation Vocabulary
ORDNANCE_SURVEY_TERMS = [
    "ORDNANCESURVEY", "RETRIANGULATION", "TRIGPOINT", "BENCHMARK",
    "CASSINI", "PROJECTION", "EASTINGS", "NORTHINGS", "GRIDREFERENCE",
    "SHEETNUMBER", "CONTOURLINES", "TRUENORTH", "MAGNETICNORTH",
    "ONEINCHMAP", "POPULAR", "DEGREES", "MINUTES", "SECONDS",
    "TRIANGULATION", "STATION", "SURVEY", "MERIDIEN", "LATITUDE",
    "LONGITUDE", "COORDINATES", "SCALE", "ELEVATION", "COUNTRYSIDE",
    "ROADS", "RIVERS", "RAILWAYS", "HILLS", "VALLEYS", "VILLAGE",
]

# 2. Nihilist Cipher & Russian Emigre Cartographer Indicators
NIHILIST_INDICATOR_TERMS = [
    "NIHILIST", "NIHIL", "SCHUVALOF", "SCHUWALOW", "SHUVALOV", "CHOUVALOV",
    "KARTOGRAFIYA", "KARTOGRAFIJA", "TOPOGRAFIYA", "SEKRETNO", "SEKRET",
    "POPRIKAZU", "GENERALNYI", "SHTAB", "MOSKVA", "PETROGRAD", "ROSSIYA",
    "AGAPEYEFF", "AGAPYEV", "АГАПЕЕВ", "ШУВАЛОВ",
]

# 3. High-Diagnostic Cartographic Word Roots (length >= 4)
DIAGNOSTIC_ROOTS = {
    "ORDN": 4.0, "SURV": 3.5, "TRIG": 4.0, "GRID": 3.0, "MAPS": 3.0,
    "SHEE": 3.0, "CONT": 2.5, "NORT": 3.0, "EAST": 2.5, "WEST": 2.5,
    "SOUT": 2.5, "DEGR": 3.5, "MINU": 3.0, "SECO": 3.0, "SCAL": 3.0,
    "LATI": 3.5, "LONG": 3.5, "COOR": 3.5, "STAT": 2.5, "ELEV": 3.0,
    "NIHI": 5.0, "IHIL": 5.0, "HILI": 5.0, "ILIS": 5.0, "LIST": 4.0,
    "SCHU": 4.5, "UVAL": 4.5, "VALO": 4.0, "ALOF": 4.5, "AGAP": 4.5,
    "KART": 4.0, "SEKR": 4.0, "PRIK": 4.0, "SHTA": 4.0,
}


def calculate_cartographic_lexical_bonus(text: str) -> float:
    """Calculate log-odds bonus for emergent cartographic and Nihilist lexical matches."""
    clean = "".join(c.upper() for c in text if c.isalpha())
    if len(clean) < 4:
        return 0.0

    bonus = 0.0
    
    # 1. Exact term matches
    for term in ORDNANCE_SURVEY_TERMS:
        if term in clean:
            bonus += 15.0 * (len(term) / 4.0)

    for term in NIHILIST_INDICATOR_TERMS:
        if term in clean:
            bonus += 25.0 * (len(term) / 4.0)

    # 2. Sub-root / n-gram frequency bonus
    for i in range(len(clean) - 3):
        q = clean[i : i + 4]
        if q in DIAGNOSTIC_ROOTS:
            bonus += DIAGNOSTIC_ROOTS[q]

    return bonus
