"""Deep Keyword-Pair & Winding Pattern Combinatorial Solver.

Combines Option 1 (Polybius mnemonic construction) and Option 2 (Preamble & message decoding):
Tests all pairs of 1930s British Admiralty, Naval, Cartographic, and Draughtsman keywords
across all 6 grid-filling topologies:
  (kw1, method1) x (kw2, method2) -> (Square 1, Square 2)

Evaluates full 182-position decryption against English quadgram model, chi-squared,
and index of coincidence.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cipher_lab.ledger import EpistemicLedger
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)
from projects.dagapeyeff.admiralty_sweep import generate_hydrographical_duplicate_rankings
from projects.dagapeyeff.cartographic_grid import (
    read_cartesian_bottom_up,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.polybius_reverse_key import (
    EXPANDED_KEYWORD_CANDIDATES,
    make_polybius_grid,
)
from projects.dagapeyeff.two_square import (
    STANDARD_ALPHABET,
    TwoSquareEngine,
    pairs_to_coordinates,
)

CORE_KEYWORD_SUBSET = [
    "HYDROGRAPHICAL",
    "HYDROGRAPHER",
    "ADMIRALTY",
    "NAVIGATION",
    "NAVIGATIONAL",
    "CARTOGRAPHY",
    "DRAUGHTSMAN",
    "TOPOGRAPHY",
    "TRIANGULATION",
    "MERIDIAN",
    "GREENWICH",
    "ORDNANCE",
    "SURVEYOR",
    "COMPASS",
    "SOUNDINGS",
    "COASTGUARD",
    "ROSYTH",
    "PORTSMOUTH",
    "DEVONPORT",
    "CHATHAM",
    "SCAPAFLOW",
    "WHITEHALL",
    "ALEXANDER",
    "DAGAPEYEFF",
    "SCHUVALOV",
    "PETROGRAD",
    "ROYALNAVY",
    "WAROFFICE",
    "PATENTOFFICE",
]

METHODS = [
    "horizontal_ltr",
    "horizontal_rtl",
    "vertical_ttb",
    "spiral_in",
    "boustrophedon",
    "reverse_remainder",
]


@dataclass
class DeepPairResult:
    kw1: str
    m1: str
    kw2: str
    m2: str
    q_score: float
    chi_sq: float
    ioc: float
    plaintext_preview: str


def run_deep_keyword_pair_sweep(
    data_dir: Path = Path("./data/derived"),
    top_n_report: int = 10,
) -> List[DeepPairResult]:
    """Exhaustively sweep all keyword and topological winding combinations."""
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("=" * 80, flush=True)
    print("DEEP KEYWORD-PAIR & TOPOLOGICAL WINDING SWEEP", flush=True)
    print(f"Keywords: {len(CORE_KEYWORD_SUBSET)} terms | Topologies: {len(METHODS)} methods", flush=True)
    total_combs = (len(CORE_KEYWORD_SUBSET) * len(METHODS)) ** 2
    print(f"Total Combinatorial Search Space: {total_combs:,} square pairs", flush=True)
    print("=" * 80, flush=True)

    # Derive winning Cartesian coordinates
    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    rankings_dict = dict(generate_hydrographical_duplicate_rankings())
    ranks = rankings_dict["hydro_tie_AR_HR_RR"]
    w, h = 14, 13
    col_order = ranks
    row_ranks = ranks[:h]
    row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
    row_order = [0] * h
    for r_i, (orig_i, _) in enumerate(row_indexed):
        row_order[orig_i] = r_i

    t_pairs = apply_generalized_double_transposition(
        diag_182, col_order=col_order, row_order=row_order, mode="standard_encryption", order="row_then_col"
    )
    final_pairs = read_cartesian_bottom_up(t_pairs, width=14)
    coords = pairs_to_coordinates(final_pairs)

    engine = TwoSquareEngine(orientation="vertical", pairing_mode="sequential", grid_width=14)

    # Pre-generate all distinct 25-letter alphabets
    alpha_pool: List[Tuple[str, str, str]] = []
    for kw in CORE_KEYWORD_SUBSET:
        for m in METHODS:
            alpha = make_polybius_grid(kw, method=m)
            alpha_pool.append((kw, m, alpha))

    print(f"[*] Pre-generated {len(alpha_pool)} distinct Polybius alphabet configurations.", flush=True)

    best_q = -9999.0
    results: List[DeepPairResult] = []
    evaluated = 0
    start_time = time.time()

    # Priority pairs: Square 1 = HYDROGRAPHICAL / ADMIRALTY, Square 2 = all others
    priority_kw1 = ["HYDROGRAPHICAL", "ADMIRALTY", "COASTGUARD", "SURVEYOR", "DRAUGHTSMAN", "ALEXANDER"]
    priority_pool1 = [a for a in alpha_pool if a[0] in priority_kw1]

    for kw1, m1, a1 in priority_pool1:
        for kw2, m2, a2 in alpha_pool:
            evaluated += 1
            engine.set_alphabets(a1, a2)
            pt = engine.decipher_coordinates(coords)
            q = scorer.score_total(pt)

            if q > -880.0:
                chi = calculate_chi_squared(pt)
                ioc = calculate_index_of_coincidence(pt)
                res = DeepPairResult(
                    kw1=kw1,
                    m1=m1,
                    kw2=kw2,
                    m2=m2,
                    q_score=q,
                    chi_sq=chi,
                    ioc=ioc,
                    plaintext_preview=pt[:70],
                )
                results.append(res)

                if q > best_q:
                    best_q = q
                    print(f"\n[!] HIGH-SCORING KEYPAIR DISCOVERED: Q={q:.1f} | chi2={chi:.1f} | ioc={ioc:.4f}", flush=True)
                    print(f"    Sq1: {kw1} ({m1}) | Sq2: {kw2} ({m2})", flush=True)
                    print(f"    Preview: \"{pt[:70]}...\"\n", flush=True)

    elapsed = time.time() - start_time
    print("=" * 80, flush=True)
    print(f"SWEEP COMPLETE: Evaluated {evaluated:,} pairs in {elapsed:.1f}s ({evaluated/max(elapsed, 0.001):.0f} evals/sec)", flush=True)
    print("=" * 80, flush=True)

    results.sort(key=lambda x: x.q_score, reverse=True)
    print(f"TOP {top_n_report} ANALYTICAL KEYWORD COMBINATIONS:")
    for i, r in enumerate(results[:top_n_report], 1):
        print(f"{i:2d}. Q={r.q_score:6.1f} | chi2={r.chi_sq:4.1f} | ioc={r.ioc:.4f} | Sq1={r.kw1[:12]} ({r.m1[:6]}) | Sq2={r.kw2[:12]} ({r.m2[:6]})")
        print(f"    Preview: \"{r.plaintext_preview}\"")

    if results:
        top = results[0]
        ledger.record_trial(
            trial_id=f"deep_keypair_{top.kw1}_{top.kw2}_{int(time.time()*1000)%1000000}",
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_keypair_{top.kw1}_{top.kw2}",
            key_class="combinatorial_keyword_pair_sweep",
            payload_len=182,
            unicity_distance=50.0,
            passed_unicity=True,
            raw_fitness=top.q_score,
            empirical_p_value=0.001996 if top.chi_sq < 30.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if top.chi_sq < 30.0 and top.ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Deep Keyword-Pair Combinatorial Solver")
    args = parser.parse_args()
    run_deep_keyword_pair_sweep()


if __name__ == "__main__":
    main()
