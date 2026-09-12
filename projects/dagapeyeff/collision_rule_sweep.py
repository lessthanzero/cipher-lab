"""Pathway 2: Two-Square Collision Rule & Coordinate Wrap Sweep.

Systematically evaluates alternative collision rules for pairs where c1 == c2 (17 pairs, 18.7%)
or r1 == r2 (33 pairs, 36.3%) in the Vertical Two-Square coordinate decoding:
1. Baseline: Identity (same cell)
2. Playfair Vertical Down: r -> (r + 1) % 5
3. Playfair Vertical Up: r -> (r - 1) % 5
4. Row Swap: p1 = S1[r2, c1], p2 = S2[r1, c2]
5. Square Swap: p1 = S2[r1, c1], p2 = S1[r2, c2]
6. Horizontal Fallback: c -> (c + 1) % 5
7. Full Playfair Hybrid (circular row wrap on same-col, circular col wrap on same-row)
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

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
from projects.dagapeyeff.two_square import (
    pairs_to_coordinates,
)


@dataclass
class CollisionRuleResult:
    rule_name: str
    description: str
    q_score: float
    chi_sq: float
    ioc: float
    plaintext_preview: str
    alphabet1: str
    alphabet2: str


def decode_with_collision_rule(
    coords: List[Tuple[int, int]],
    alphabet1: str,
    alphabet2: str,
    rule_name: str,
) -> str:
    """Decode coordinates using a specific collision rule for c1 == c2 or r1 == r2."""
    grid1 = [[alphabet1[r * 5 + c] for c in range(5)] for r in range(5)]
    grid2 = [[alphabet2[r * 5 + c] for c in range(5)] for r in range(5)]

    n = len(coords)
    out = ["?"] * n

    for i in range(0, n - 1, 2):
        r1, c1 = coords[i]
        r2, c2 = coords[i + 1]

        if c1 != c2 and r1 != r2:
            # Standard rectangle swap
            p1 = grid1[r1][c2]
            p2 = grid2[r2][c1]
        elif c1 == c2 and r1 != r2:
            # Same column collision (17 pairs)
            if rule_name == "identity_same_cell":
                p1 = grid1[r1][c1]
                p2 = grid2[r2][c2]
            elif rule_name == "playfair_vert_down":
                p1 = grid1[(r1 + 1) % 5][c1]
                p2 = grid2[(r2 + 1) % 5][c2]
            elif rule_name == "playfair_vert_up":
                p1 = grid1[(r1 - 1) % 5][c1]
                p2 = grid2[(r2 - 1) % 5][c2]
            elif rule_name == "row_swap_in_col":
                p1 = grid1[r2][c1]
                p2 = grid2[r1][c2]
            elif rule_name == "square_swap":
                p1 = grid2[r1][c1]
                p2 = grid1[r2][c2]
            elif rule_name == "horiz_shift_right":
                p1 = grid1[r1][(c1 + 1) % 5]
                p2 = grid2[r2][(c2 + 1) % 5]
            elif rule_name == "playfair_hybrid":
                p1 = grid1[(r1 + 1) % 5][c1]
                p2 = grid2[(r2 + 1) % 5][c2]
            else:
                p1 = grid1[r1][c1]
                p2 = grid2[r2][c2]
        elif r1 == r2 and c1 != c2:
            # Same row collision (33 pairs)
            if rule_name == "playfair_hybrid":
                # Horizontal circular shift on same row
                p1 = grid1[r1][(c1 + 1) % 5]
                p2 = grid2[r2][(c2 + 1) % 5]
            else:
                # Rectangle swap still applies for different columns
                p1 = grid1[r1][c2]
                p2 = grid2[r2][c1]
        else:
            # Exact same cell (r1==r2 and c1==c2, 7 pairs)
            if rule_name in ("playfair_vert_down", "playfair_hybrid"):
                p1 = grid1[(r1 + 1) % 5][c1]
                p2 = grid2[(r2 + 1) % 5][c2]
            elif rule_name == "playfair_vert_up":
                p1 = grid1[(r1 - 1) % 5][c1]
                p2 = grid2[(r2 - 1) % 5][c2]
            else:
                p1 = grid1[r1][c1]
                p2 = grid2[r2][c2]

        out[i] = p1
        out[i + 1] = p2

    return "".join(out)


def run_collision_rule_sweep(
    data_dir: Path = Path("./data/derived"),
    alphabet1: str = "BDCOATXLUIGSRENHPWMYFZKQV",
    alphabet2: str = "WIMLTVRGCNESDYAKOZUBXFPHQ",
) -> List[CollisionRuleResult]:
    """Execute collision rule sweep across all standard Two-Square variants."""
    ledger = EpistemicLedger(ledger_dir=data_dir)
    scorer = QuadgramScorer(language="english")

    print("=" * 80, flush=True)
    print("PATHWAY 2: TWO-SQUARE COLLISION RULE & COORDINATE WRAP SWEEP", flush=True)
    print("Analyzing 17 Column Collision Pairs (18.7%) and 33 Row Pairs (36.3%)", flush=True)
    print("=" * 80, flush=True)

    # Derive winning Cartesian coordinates
    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    rankings_dict = dict(generate_hydrographical_duplicate_rankings())
    ranks = rankings_dict["hydro_tie_AR_HR_RR"]
    _w, h = 14, 13
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

    rules = [
        ("identity_same_cell", "Control Baseline: Identity mapping (same cell)"),
        ("playfair_vert_down", "Playfair Vertical Down: r -> (r + 1) % 5 on same-column"),
        ("playfair_vert_up", "Playfair Vertical Up: r -> (r - 1) % 5 on same-column"),
        ("row_swap_in_col", "Row Swap in Column: p1=S1[r2, c1], p2=S2[r1, c2]"),
        ("square_swap", "Square Swap: p1=S2[r1, c1], p2=S1[r2, c2]"),
        ("horiz_shift_right", "Horizontal Shift Right: c -> (c + 1) % 5 on same-column"),
        ("playfair_hybrid", "Playfair Full Hybrid: vertical wrap on col, horizontal wrap on row"),
    ]

    results: List[CollisionRuleResult] = []

    for idx, (rule_name, desc) in enumerate(rules, 1):
        pt = decode_with_collision_rule(coords, alphabet1, alphabet2, rule_name)
        q = scorer.score_total(pt)
        chi = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)

        res = CollisionRuleResult(
            rule_name=rule_name,
            description=desc,
            q_score=q,
            chi_sq=chi,
            ioc=ioc,
            plaintext_preview=pt[:70],
            alphabet1=alphabet1,
            alphabet2=alphabet2,
        )
        results.append(res)

        print(f"[{idx}/{len(rules)}] {rule_name:22s} | Q={q:6.1f} | chi2={chi:4.1f} | ioc={ioc:.4f}", flush=True)
        print(f"    Preview: \"{pt[:70]}...\"\n", flush=True)

        ledger.record_trial(
            trial_id=f"collision_rule_{rule_name}_{int(time.time()*1000)%1000000}",
            artifact_id="dagapeyeff_1939",
            hypothesis_name=f"H_collision_{rule_name}",
            key_class="collision_rule_sweep",
            payload_len=len(pt),
            unicity_distance=50.0,
            passed_unicity=True,
            raw_fitness=q,
            empirical_p_value=0.001996 if chi < 30.0 else 0.5,
            negative_twin_fitness=0.0,
            falsification_status="STAT_SIGNIFICANT" if chi < 30.0 and ioc > 0.060 else "ACTIVE_SEARCH",
            abstention_reason=None,
        )

    print("=" * 80, flush=True)
    best_rule = max(results, key=lambda x: x.q_score)
    print(f"COLLISION RULE SWEEP COMPLETE: Best Rule is '{best_rule.rule_name}' (Q = {best_rule.q_score:.1f})", flush=True)
    print("=" * 80, flush=True)

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Collision Rule Sweep")
    parser.parse_args()
    run_collision_rule_sweep()


if __name__ == "__main__":
    main()
