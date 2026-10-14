"""Tier 3 Completion Standard Audit for Kryptos K4.

Formalizes the CipherLab Blind Cryptanalysis Protocol completion standard:
- 'Cryptographically recovered'
- 'Plaintext known; decryption method unverified'
- 'Unsolved'
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class CryptanalyticVerdict(str, Enum):
    CRYPTOGRAPHICALLY_RECOVERED = "Cryptographically recovered"
    PLAINTEXT_KNOWN_METHOD_UNVERIFIED = "Plaintext known; decryption method unverified."
    UNSOLVED = "Unsolved."


@dataclass(frozen=True)
class CompletionAuditResult:
    verdict: CryptanalyticVerdict
    has_specified_method: bool
    has_specified_key: bool
    is_reproducible: bool
    explains_full_corpus: bool
    zero_ad_hoc_errata: bool
    independent_reproduced: bool
    beats_negative_controls: bool
    plaintext_known_from_archives: bool
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "checklist": {
                "method_and_key_explicitly_specified": self.has_specified_method and self.has_specified_key,
                "reproducible_decryption_procedure": self.is_reproducible,
                "consistent_with_complete_ciphertext": self.explains_full_corpus,
                "no_unexplained_ad_hoc_corrections": self.zero_ad_hoc_errata,
                "independent_verifier_reproduced": self.independent_reproduced,
                "distinguished_from_noise_controls": self.beats_negative_controls,
            },
            "archival_status": {
                "plaintext_known_from_archives": self.plaintext_known_from_archives,
            },
            "rationale": self.rationale,
        }


def evaluate_completion_standard(
    has_specified_method: bool = False,
    has_specified_key: bool = False,
    is_reproducible: bool = False,
    explains_full_corpus: bool = False,
    zero_ad_hoc_errata: bool = False,
    independent_reproduced: bool = False,
    beats_negative_controls: bool = False,
    plaintext_known_from_archives: bool = True,
) -> CompletionAuditResult:
    """Evaluate candidate solution state against CipherLab completion criteria."""
    all_crypto_criteria = (
        has_specified_method
        and has_specified_key
        and is_reproducible
        and explains_full_corpus
        and zero_ad_hoc_errata
        and independent_reproduced
        and beats_negative_controls
    )

    if all_crypto_criteria:
        verdict = CryptanalyticVerdict.CRYPTOGRAPHICALLY_RECOVERED
        rationale = (
            "All six cryptographic criteria met: complete mathematical method, verified key material, "
            "zero ad-hoc errata, full 97-character decryption reproduced independently, and statistical "
            "superiority over negative controls confirmed."
        )
    elif plaintext_known_from_archives:
        verdict = CryptanalyticVerdict.PLAINTEXT_KNOWN_METHOD_UNVERIFIED
        rationale = (
            "Plaintext recovered via archival discovery (Kobek & Byrne, Smithsonian Archives of American Art, "
            "September 2025; confirmed by Jim Sanborn), but the underlying cryptographic method and mathematical "
            "key remain unverified and unsolved."
        )
    else:
        verdict = CryptanalyticVerdict.UNSOLVED
        rationale = "Neither the mathematical method nor authenticated plaintext has been independently established."

    return CompletionAuditResult(
        verdict=verdict,
        has_specified_method=has_specified_method,
        has_specified_key=has_specified_key,
        is_reproducible=is_reproducible,
        explains_full_corpus=explains_full_corpus,
        zero_ad_hoc_errata=zero_ad_hoc_errata,
        independent_reproduced=independent_reproduced,
        beats_negative_controls=beats_negative_controls,
        plaintext_known_from_archives=plaintext_known_from_archives,
        rationale=rationale,
    )


if __name__ == "__main__":
    audit = evaluate_completion_standard()
    print("=" * 70)
    print("CIPHERLAB — KRYPTOS K4 CURRENT COMPLETION AUDIT")
    print("=" * 70)
    print(f"VERDICT:   {audit.verdict.value}")
    print(f"RATIONALE: {audit.rationale}")
    print("=" * 70)
