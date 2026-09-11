"""Reference cryptanalytic benchmarks and competitive scoring targets for D'Agapeyeff.

Sourced from empirical findings published at https://dagapeyeffresearch.com (Tim Marland, 2026).
"""

from __future__ import annotations

from typing import Any, Dict

# Tim Marland's State-of-the-Art Benchmarks (March 2026)
MARLAND_BEST_TWO_SQUARE_Q = -692.13      # Vertical Two-Square simulated annealing (best in project)
MARLAND_BEST_CHI_SQ = 18.2               # Achieved with position 97 correction (04 -> 75)
MARLAND_ENGLISH_IOC_BENCHMARK = 0.0667   # Natural English benchmark
MARLAND_CIPHER_IOC = 0.0650              # Baseline IoC of 196 pairs
MARLAND_FALSE_ADFGX_Q = -101.71          # Debunked overfitting false positive (14% evaluated)

# English Acceptance Thresholds
TARGET_CHI_SQ_ACCEPT = 35.0              # Letter distribution match
TARGET_IOC_MIN = 0.060                   # Repetition index
TARGET_QUADGRAM_PER_CHAR = -3.8          # Length-normalized quadgram log-likelihood


def evaluate_against_competition(
    quadgram_total_score: float,
    chi_squared: float,
    ioc: float,
    num_chars_scored: int = 196,
) -> Dict[str, Any]:
    """Compare a candidate decryption attempt against Marland's project records."""
    beat_two_square = (quadgram_total_score > MARLAND_BEST_TWO_SQUARE_Q)
    beat_chi_sq = (chi_squared < MARLAND_BEST_CHI_SQ)
    is_full_eval = (num_chars_scored == 196)

    status = "SUB_BENCHMARK"
    if is_full_eval and beat_two_square and chi_squared < TARGET_CHI_SQ_ACCEPT:
        status = "BREAKTHROUGH_CANDIDATE"
    elif is_full_eval and beat_two_square:
        status = "BEAT_MARLAND_BASELINE"

    return {
        "candidate_quadgram": round(quadgram_total_score, 2),
        "marland_record_q": MARLAND_BEST_TWO_SQUARE_Q,
        "delta_q": round(quadgram_total_score - MARLAND_BEST_TWO_SQUARE_Q, 2),
        "candidate_chi_sq": round(chi_squared, 2),
        "marland_record_chi_sq": MARLAND_BEST_CHI_SQ,
        "beat_chi_squared_record": beat_chi_sq,
        "candidate_ioc": round(ioc, 4),
        "scored_all_196_positions": is_full_eval,
        "competition_status": status,
    }
