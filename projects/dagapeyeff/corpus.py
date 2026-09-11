"""Canonical corpus transcription and exact structural representations for the D'Agapeyeff Cipher.

Verified against Page 144 of the First Edition of Codes and Ciphers (Oxford University Press, 1939).
"""

from __future__ import annotations

import collections
from typing import Any, Dict, List

# Exact 395 digits from Page 144 of Codes and Ciphers (1939)
# 79 groups of five digits: 7 lines of 10 groups (50 digits) + 1 line of 9 groups (45 digits)
RAW_395_DIGITS = (
    "75628285916291648164917485846474748284838163818174"
    "74826264758382849175746583757575936365658163817585"
    "75756462829285746382757483816581848564856485856382"
    "72628362818172816463758281648363828581636363047481"
    "91918463858465648565629462628591859174917275646575"
    "71658362647481828462826491819365626484849183857491"
    "81657274838385828364627262656283759272638282727283"
    "828584758281837284628283758164757485816292000"
)

# Trailing null/padding digits
NULL_PADDING = "000"

# 196 pairs consume 392 digits
PAYLOAD_DIGITS = RAW_395_DIGITS[:392]

# Allowed digit sets
ROW_DIGITS = {"6", "7", "8", "9", "0"}
COL_DIGITS = {"1", "2", "3", "4", "5"}


def get_raw_digits() -> str:
    """Return the complete 395-digit string."""
    return RAW_395_DIGITS


def get_payload_digits() -> str:
    """Return the 392 payload digits (excluding trailing 000)."""
    return PAYLOAD_DIGITS


def get_digit_pairs() -> List[str]:
    """Return the 196 consecutive two-digit pairs."""
    return [PAYLOAD_DIGITS[i : i + 2] for i in range(0, len(PAYLOAD_DIGITS), 2)]


def get_14x14_pair_grid() -> List[List[str]]:
    """Return the 196 pairs arranged into a 14x14 grid."""
    pairs = get_digit_pairs()
    return [pairs[r * 14 : (r + 1) * 14] for r in range(14)]


def get_14th_column_pairs() -> List[str]:
    """Return the 14 pairs located in the 14th column of the 14x14 grid."""
    grid = get_14x14_pair_grid()
    return [row[13] for row in grid]


def get_stripped_14x13_pairs() -> List[str]:
    """Return the 182 pairs obtained by removing the 14th column."""
    grid = get_14x14_pair_grid()
    res = []
    for row in grid:
        res.extend(row[:13])
    return res


def get_pair_frequencies() -> Dict[str, int]:
    """Calculate frequencies of the 196 pairs."""
    return dict(collections.Counter(get_digit_pairs()))


def verify_pair_structure() -> Dict[str, Any]:
    """Verify that all pairs satisfy row-in-{6,7,8,9,0} and col-in-{1,2,3,4,5}."""
    pairs = get_digit_pairs()
    valid_count = 0
    anomalies = []
    for idx, pair in enumerate(pairs):
        r, c = pair[0], pair[1]
        if r in ROW_DIGITS and c in COL_DIGITS:
            valid_count += 1
        else:
            anomalies.append((idx, pair))
    return {
        "total_pairs": len(pairs),
        "valid_polybius_pairs": valid_count,
        "valid_pct": round((valid_count / len(pairs)) * 100, 2),
        "anomalies": anomalies,
    }
