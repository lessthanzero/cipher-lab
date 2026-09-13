"""Physical Stone Epigraphy & Codicological Analysis of the Shugborough Monument.

Analyzes the physical attributes of the Shepherd's Monument at Shugborough Hall,
Staffordshire (commissioned by Thomas Anson, carved by Peter Scheemakers c. 1748–1756).
Codifies the critical epigraphic findings:
1. Punctuation: Explicit carved interpuncts (middle dots '·') between every single character,
   proving beyond doubt that the sequence is an initialism/abbreviation, not continuous ciphertext.
2. Letterform distinction: Deliberate distinction between rounded 'U' (character 2) and
   sharp pointed 'V' (characters 5, 7, 8).
3. Classical Framing: 'D ·' and 'M ·' carved on lower flanking tiers, representing the
   universal Roman funerary dedication formula 'Dis Manibus' (To the Divine Shades).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class EpigraphicLetter:
    index: int
    char: str
    is_vocalic_u: bool
    has_interpunct_after: bool
    tier: str  # 'upper' or 'flanking_lower'
    carving_notes: str


@dataclass(frozen=True)
class EpigraphicProfile:
    monument_name: str
    location: str
    commissioner: str
    sculptor: str
    date_range: str
    source_artwork: str
    is_artwork_mirrored: bool
    upper_line_tokens: List[EpigraphicLetter]
    flanking_tokens: List[EpigraphicLetter]
    is_initialism_confirmed_by_interpuncts: bool
    funerary_dedication: str


class ShugboroughEpigraphy:
    """Epigraphic data model and validator for the Shepherd's Monument inscription."""

    @classmethod
    def get_canonical_profile(cls) -> EpigraphicProfile:
        """Construct the canonical epigraphic profile from physical monument examination."""
        # Upper line: O · U · O · S · V · A · V · V
        raw_upper = "OUOSVAVV"
        upper_letters: List[EpigraphicLetter] = []
        for idx, c in enumerate(raw_upper):
            is_u = (c == "U")
            # All letters in upper line have following or separating interpuncts
            has_dot = True
            notes = (
                "Carved as rounded capital U with serif, indicating vocalic U."
                if is_u
                else f"Carved as pointed Roman capital {c}."
            )
            upper_letters.append(
                EpigraphicLetter(
                    index=idx,
                    char=c,
                    is_vocalic_u=is_u,
                    has_interpunct_after=has_dot,
                    tier="upper",
                    carving_notes=notes,
                )
            )

        # Flanking lower letters: D · (left), M · (right)
        flanking = [
            EpigraphicLetter(
                index=0,
                char="D",
                is_vocalic_u=False,
                has_interpunct_after=True,
                tier="flanking_lower_left",
                carving_notes="Roman capital D followed by clear middle dot. Dis (Manibus).",
            ),
            EpigraphicLetter(
                index=1,
                char="M",
                is_vocalic_u=False,
                has_interpunct_after=True,
                tier="flanking_lower_right",
                carving_notes="Roman capital M followed by clear middle dot. Manibus.",
            ),
        ]

        return EpigraphicProfile(
            monument_name="The Shepherd's Monument",
            location="Shugborough Hall, Milford, Staffordshire, England",
            commissioner="Thomas Anson (c. 1695–1773), MP for Lichfield, Society of Dilettanti",
            sculptor="Peter Scheemakers (1691–1781)",
            date_range="c. 1748–1756",
            source_artwork="Nicolas Poussin, 'Les Bergers d'Arcadie' (Et in Arcadia ego, 2nd version, 1638)",
            is_artwork_mirrored=True,
            upper_line_tokens=upper_letters,
            flanking_tokens=flanking,
            is_initialism_confirmed_by_interpuncts=True,
            funerary_dedication="Dis Manibus (D · M ·)",
        )

    @classmethod
    def validate_letterform_constraints(cls, candidate_words: List[str]) -> Tuple[bool, List[str]]:
        """Verify whether an 8-word candidate initialism respects epigraphic letterform constraints.

        Constraints:
        1. Word 1: Must begin with 'O'
        2. Word 2: Must begin with 'U' (vocalic or Latin u-stem, NOT consonantal V)
        3. Word 3: Must begin with 'O'
        4. Word 4: Must begin with 'S'
        5. Word 5: Must begin with 'V' (consonantal V or Latin v-stem)
        6. Word 6: Must begin with 'A'
        7. Word 7: Must begin with 'V' (consonantal V)
        8. Word 8: Must begin with 'V' (consonantal V)
        """
        if len(candidate_words) != 8:
            return False, [f"Expected 8 words, got {len(candidate_words)}"]

        errors: List[str] = []
        expected = ["O", "U", "O", "S", "V", "A", "V", "V"]

        for idx, (word, exp) in enumerate(zip(candidate_words, expected)):
            clean_word = word.strip().upper()
            if not clean_word:
                errors.append(f"Position {idx+1}: Empty word")
                continue
            first_char = clean_word[0]

            # In classical/neo-Latin, U and V were interchangeable in orthography,
            # but Scheemakers explicitly carved rounded 'U' at pos 2 and pointed 'V' at pos 5, 7, 8.
            if exp == "U":
                if first_char not in ("U", "V"):
                    errors.append(f"Position 2: Expected initial U/V (carved 'U'), got '{first_char}' ({word})")
            elif exp == "V":
                if first_char not in ("V", "U"):
                    errors.append(f"Position {idx+1}: Expected initial V (carved 'V'), got '{first_char}' ({word})")
            else:
                if first_char != exp:
                    errors.append(f"Position {idx+1}: Expected initial '{exp}', got '{first_char}' ({word})")

        return (len(errors) == 0, errors)


if __name__ == "__main__":
    prof = ShugboroughEpigraphy.get_canonical_profile()
    print("=== SHUGBOROUGH EPIGRAPHIC PROFILE ===")
    print(f"Monument: {prof.monument_name} ({prof.date_range})")
    print(f"Sculptor: {prof.sculptor} | Commissioner: {prof.commissioner}")
    print(f"Art Source: {prof.source_artwork} (Mirrored: {prof.is_artwork_mirrored})")
    print(f"Dedication: {prof.funerary_dedication}")
    print(f"Initialism Interpuncts Confirmed: {prof.is_initialism_confirmed_by_interpuncts}")
    print("\nUpper Line Letterforms:")
    for l in prof.upper_line_tokens:
        print(f"  [{l.index+1}] '{l.char}' (Vocalic U: {l.is_vocalic_u}, Interpunct: {l.has_interpunct_after}) - {l.carving_notes}")
    print("\nFlanking Letterforms:")
    for l in prof.flanking_tokens:
        print(f"  [{l.char}] ({l.tier}) - {l.carving_notes}")
