"""Cryptanalytic & Mathematical Falsification of Pseudohistoric Shugborough Theories.

Provides formal mathematical and information-theoretic refutations of:
1. The Holy Grail / Priory of Sion / Rennes-le-Château geometric map hypothesis.
2. Dave Ramsden's (2014) Polyalphabetic / Vigenère "Magdalen" decipherment.
3. George Edmunds's (2016) Admiral Anson Buried Treasure Coordinates hypothesis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class PolyalphabeticTrivialityProof:
    target_plaintext: str
    ciphertext: str
    derived_vigenere_key: str
    mathematical_implication: str


class ShugboroughPseudohistoryDebunker:
    """Rigorous mathematical refutation of unicity-violating theories."""

    CIPHERTEXT: str = "OUOSVAVV"

    @classmethod
    def prove_polyalphabetic_triviality(cls, target_word: str) -> PolyalphabeticTrivialityProof:
        """Prove that ANY 8-letter word can be 'deciphered' from OUOSVAVV.

        For any ciphertext C of length L and any arbitrary plaintext P of length L,
        the Vigenère equation C_i = (P_i + K_i) mod 26 always has a unique exact
        solution K_i = (C_i - P_i) mod 26.
        When key length == ciphertext length (or key is arbitrary), cryptanalytic
        claim of a 'decipherment' has ZERO discriminative power.
        """
        clean_target = "".join(c.upper() for c in target_word if c.isalpha())
        if len(clean_target) != len(cls.CIPHERTEXT):
            raise ValueError(f"Target word must be {len(cls.CIPHERTEXT)} letters, got {len(clean_target)}")

        key_chars: List[str] = []
        for c_char, p_char in zip(cls.CIPHERTEXT, clean_target):
            c_val = ord(c_char) - ord("A")
            p_val = ord(p_char) - ord("A")
            k_val = (c_val - p_val) % 26
            key_chars.append(chr(k_val + ord("A")))

        derived_key = "".join(key_chars)

        implication = (
            f"Because key length ({len(derived_key)}) equals ciphertext length ({len(cls.CIPHERTEXT)}), "
            f"Shannon's Perfect Secrecy theorem applies: for any arbitrary target '{clean_target}', "
            f"there exists an exact mathematical key '{derived_key}'. Therefore, Ramsden's (2014) "
            f"claim that 'OUOSVAVV' decrypts to 'MAGDALEN' is mathematically trivial and has zero "
            f"cryptographic validity."
        )

        return PolyalphabeticTrivialityProof(
            target_plaintext=clean_target,
            ciphertext=cls.CIPHERTEXT,
            derived_vigenere_key=derived_key,
            mathematical_implication=implication,
        )

    @classmethod
    def evaluate_geometric_pareidolia(
        cls,
        num_salient_points: int = 40,
        allowed_error_margin_degrees: float = 2.0,
    ) -> Dict[str, float]:
        """Demonstrate Ramsey-theoretic certainty of false geometric alignments in Poussin's relief.

        With N salient visual points (eyes, fingers, staff ends, tomb corners, tree forks):
        - Number of lines = N * (N - 1) / 2
        - Number of angle pairs = Lines * (Lines - 1) / 2
        By the Poisson point process, discovering a 'pentagram' or 'golden ratio angle'
        is mathematically guaranteed by chance alone.
        """
        num_lines = (num_salient_points * (num_salient_points - 1)) // 2
        num_triangles = (num_salient_points * (num_salient_points - 1) * (num_salient_points - 2)) // 6

        # Expected false positive alignments within ±error margin
        prob_angle_match = (2.0 * allowed_error_margin_degrees) / 360.0
        expected_matches = num_triangles * prob_angle_match

        return {
            "num_salient_points": num_salient_points,
            "possible_connecting_lines": num_lines,
            "possible_triangles": num_triangles,
            "expected_chance_alignments": round(expected_matches, 2),
            "ramsey_verdict": (
                f"With {num_salient_points} landmark points, there are {num_triangles:,} triangles. "
                f"Finding a 'sacred pentagram' or 'Grail triangle' is an inevitable mathematical "
                f"certainty of geometric Ramsey theory, not evidence of intentional design."
            ),
        }

    @classmethod
    def evaluate_anson_treasure_coordinates(cls) -> Dict[str, str]:
        """Falsify Edmunds (2016) buried treasure coordinate hypothesis."""
        return {
            "hypothesis": "Admiral Anson Buried Treasure Coordinates (Edmunds 2016)",
            "claim": "OUOSVAVV encodes latitude and longitude of an island with Spanish galleon treasure.",
            "mathematical_falsification": (
                "Degrees-of-Freedom Exploitation: 8 letters allow 26^8 ≈ 2.08 x 10^11 combinations. "
                "Any arbitrary 8-letter string can be mapped into valid latitude/longitude coordinates "
                "under ad hoc numerical substitution (e.g. A=1, B=2 or nautical minute offsets). "
                "Without a pre-specified, non-adjustable coordinate encoding algorithm published prior "
                "to inspection, the hypothesis is mathematically unfalsifiable and cryptanalytically null."
            ),
            "verdict": "REJECTED (Unfalsifiable degrees-of-freedom overfitting)",
        }


if __name__ == "__main__":
    debunker = ShugboroughPseudohistoryDebunker()

    # 1. Test Ramsden "Magdalen" triviality
    proof_magdalen = debunker.prove_polyalphabetic_triviality("MAGDALEN")
    print("=== RAMSDEN POLYALPHABETIC TRIVIALITY PROOF ===")
    print(f"Ciphertext: {proof_magdalen.ciphertext}")
    print(f"Target: {proof_magdalen.target_plaintext} -> Derived Key: {proof_magdalen.derived_vigenere_key}")
    print(f"Implication: {proof_magdalen.mathematical_implication}\n")

    # Arbitrary targets
    for target in ["VICTORIA", "SHERLOCK", "CLEOPATR"]:
        p = debunker.prove_polyalphabetic_triviality(target)
        print(f"Arbitrary Target: {p.target_plaintext:8s} -> Key: {p.derived_vigenere_key:8s}")

    # 2. Geometric pareidolia
    print("\n=== GEOMETRIC PAREIDOLIA PROOF ===")
    geom = debunker.evaluate_geometric_pareidolia(num_salient_points=45)
    for k, v in geom.items():
        print(f"{k}: {v}")

    # 3. Treasure coordinates
    print("\n=== ANSON TREASURE COORDINATES EVALUATION ===")
    treasure = debunker.evaluate_anson_treasure_coordinates()
    for k, v in treasure.items():
        print(f"{k}: {v}")
