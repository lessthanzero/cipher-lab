"""Hypothesis generators, fractionation decoders, and error-slip operators for D'Agapeyeff."""

from __future__ import annotations

from cipher_lab.solvers import ColumnarTransposition, PolybiusCheckerboard


def decode_polybius_fractionation(
    digits: str,
    key_alphabet: str = "ABCDEFGHIKLMNOPQRSTUVWXYZ",
    row_offset: int = 1,
) -> str:
    """Decode a string of digits into characters using a Polybius 5x5 square.
    
    Pairs are treated as (row, col).
    """
    checkerboard = PolybiusCheckerboard(key_alphabet=key_alphabet, size=5)
    chars = []
    for i in range(0, len(digits) - 1, 2):
        r = int(digits[i]) - row_offset + 1
        c = int(digits[i+1]) - row_offset + 1
        # Wrap or modulo into 1-5 if coordinates range 1-9
        r = ((r - 1) % 5) + 1
        c = ((c - 1) % 5) + 1
        chars.append(checkerboard.coord_to_char.get((r, c), "?"))
    return "".join(chars)


def apply_columnar_transposition(digits: str, col_order: list[int]) -> str:
    """Transpose digit stream using columnar transposition."""
    return ColumnarTransposition.decrypt(digits, col_order)


def apply_error_slip(digits: str, slip_index: int, error_type: str = "delete") -> str:
    """Model D'Agapeyeff's clerical slip hypothesis.
    
    error_type:
    - 'delete': Encipherer omitted one digit.
    - 'swap': Encipherer swapped two adjacent digits.
    - 'shift': Encipherer miscalculated one coordinate by +/- 1.
    """
    if error_type == "delete" and 0 <= slip_index < len(digits):
        return digits[:slip_index] + digits[slip_index + 1:]
    elif error_type == "swap" and 0 <= slip_index < len(digits) - 1:
        chars = list(digits)
        chars[slip_index], chars[slip_index + 1] = chars[slip_index + 1], chars[slip_index]
        return "".join(chars)
    return digits
