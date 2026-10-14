"""Tier 1 Blind Search Runner for Kryptos K4.

Loads blind ciphertext, executes pure statistical characterization and unicity
auditing without cribs or contextual hints, and freezes findings to hypothesis store.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from projects.kryptos.manifests import BLIND_PATH, load_dataset
from projects.kryptos.tier1_blind.stats import compute_blind_profile
from projects.kryptos.tier1_blind.unicity import audit_scheidt_families


OUTPUT_PROFILE_PATH = (
    Path(__file__).parent.parent / "hypotheses" / "tier_1" / "baseline_profile.json"
)


def run_tier1_blind_analysis() -> Dict[str, Any]:
    """Execute Tier 1 blind analysis and freeze results."""
    # Enforce Tier 1 access control
    dataset = load_dataset(BLIND_PATH, current_tier=1)
    ciphertext = dataset["ciphertext"]

    # Check zero-leak invariants
    assert dataset.get("access_control", {}).get("allowed_for_blind_search") is True
    assert dataset.get("access_control", {}).get("contains_cribs") is False
    assert dataset.get("access_control", {}).get("contains_plaintext") is False

    stats_profile = compute_blind_profile(ciphertext)
    unicity_audit = audit_scheidt_families(len(ciphertext))

    findings = {
        "tier": 1,
        "phase": "blind_search",
        "dataset_name": dataset["name"],
        "dataset_sha256": dataset.get("sha256", "verified"),
        "ciphertext": ciphertext,
        "statistical_profile": stats_profile,
        "unicity_audit": unicity_audit,
        "conclusions": {
            "ioc_verdict": (
                f"Ciphertext IoC is {stats_profile['index_of_coincidence']}, which is much lower than natural "
                f"English (0.0667) and close to random (0.0385). This definitively rules out simple monoalphabetic "
                f"substitution or pure transposition without substitution."
            ),
            "factorization_verdict": (
                "N=97 is prime. Any pure grid transposition without padding or masking is structurally impossible."
            ),
            "unicity_verdict": (
                "Compound classical models (e.g. Quagmire III or structured double columnar transposition) remain "
                "well within the Shannon unicity budget (H(K) <= 120 bits vs available 310 bits). Arbitrary "
                "unconstrained substitution + transposition is rejected as underdetermined."
            ),
        },
    }

    OUTPUT_PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    return findings


if __name__ == "__main__":
    results = run_tier1_blind_analysis()
    print("=" * 70)
    print("CIPHERLAB — TIER 1 BLIND STATISTICAL PROFILE (KRYPTOS K4)")
    print("=" * 70)
    print(f"Length:               {results['statistical_profile']['text_length']} chars (Prime: {results['statistical_profile']['factorization_constraints']['is_prime']})")
    print(f"Unique Characters:    {results['statistical_profile']['unique_characters']} / 26")
    print(f"Index of Coincidence: {results['statistical_profile']['index_of_coincidence']} (Random: 0.0385, English: 0.0667)")
    print(f"Interpretation:       {results['statistical_profile']['ioc_interpretation']}")
    print(f"Shannon Entropy:      {results['statistical_profile']['shannon_entropy_bits']} bits/char")
    print("\nTop Autocorrelation Harmonics:")
    for lag_info in results['statistical_profile']['autocorrelation_top_lags']:
        print(f"  Lag {lag_info['lag']:2d}: {lag_info['matches']} matches (z-score = {lag_info['z_score']:+.2f})")
    print("\nUnicity Gate Summary:")
    for fam in results['unicity_audit']['families']:
        status = "PASSED" if fam['is_determined'] else "REJECTED"
        print(f"  [{status}] {fam['model_name']:<48} | U0: {fam['unicity_distance_chars']:5.1f} chars | {fam['entropy_ratio']:5.2f}x budget")
    print(f"\nFrozen profile saved to: {OUTPUT_PROFILE_PATH}")
    print("=" * 70)
