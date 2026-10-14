"""Tier 2 Fleissner Turning Grille Sweeper for Kryptos K4.

Analyzes 7x7 Turning Grilles under 90-degree rotational geometry:
1. Grid Orbits:
   In a 7x7 matrix (49 cells), center cell (3, 3) is a fixed point.
   The remaining 48 cells partition into exactly 12 orbits of 4 cells each under 90° rotation.
   Square B has exactly 48 cells (omitting 1 corner or center cell).
   Keyspace: 4^12 = 16,777,216 possible 12-hole turning grilles.

2. Transposition Engine:
   For a candidate grille h in {0, 1, 2, 3}^12:
   - Phase 0 (0°): 12 letters written
   - Phase 1 (90°): 12 letters written
   - Phase 2 (180°): 12 letters written
   - Phase 3 (270°): 12 letters written
   Produces a 48-cell transposition permutation pi_h.

3. Consistency Filter on Crib Anchors:
   Tests whether pi_h can map plaintext cribs (EASTNORTHEAST, BERLINCLOCK)
   to the observed ciphertext positions, under:
   a) Direct Fleissner transposition (no substitution)
   b) Fleissner transposition + periodic key K of period L in [1..7]
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import time
from typing import Any, Dict, List, Optional, Tuple

from projects.kryptos.manifests import BLIND_PATH, CONTEXTUAL_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


GRID_DIM = 7
NUM_ORBITS = 12


def compute_7x7_orbits(omit_cell: Tuple[int, int] = (6, 6)) -> Tuple[List[List[Tuple[int, int]]], Optional[Tuple[int, int]]]:
    """
    Computes 12 orbits of 4 cells each in a 7x7 grid under 90° clockwise rotation.
    If omit_cell is (6, 6), orbit 0 is adjusted or (3, 3) invariant is tracked.
    Standard 90° CW rotation: (r, c) -> (c, 6 - r).
    """
    orbits = []
    seen = set()

    # The 12 canonical representative cells in top-left octant
    representatives = [
        (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 1), (1, 2), (1, 3), (1, 4),
        (2, 2), (2, 3),
    ]

    for r, c in representatives:
        pts = [
            (r, c),
            (c, 6 - r),
            (6 - r, 6 - c),
            (6 - c, r),
        ]
        orbits.append(pts)

    center = (3, 3)
    return orbits, center


def generate_fleissner_permutation(
    holes: Tuple[int, ...],
    orbits: List[List[Tuple[int, int]]],
    clockwise: bool = True,
    readout_by_rows: bool = True,
) -> List[int]:
    """
    Given 12 hole indices (each in 0..3), generates the 48-cell permutation.
    pi[t] gives the 1D index (r * 7 + c) in the 7x7 grid where message letter t is written.
    """
    grid = [[-1] * GRID_DIM for _ in range(GRID_DIM)]
    t = 0

    # 4 phases of 12 letters each
    for phase in range(4):
        for orb_idx, rot_idx in enumerate(holes):
            # Effective hole position under current phase rotation
            eff_rot = (rot_idx + phase) % 4 if clockwise else (rot_idx - phase) % 4
            r, c = orbits[orb_idx][eff_rot]
            grid[r][c] = t
            t += 1

    # Readout: map 1D cell position to message time t
    # For a 48-cell grid (skipping (6, 6) or (3, 3))
    readout = []
    if readout_by_rows:
        for r in range(GRID_DIM):
            for c in range(GRID_DIM):
                if grid[r][c] != -1:
                    readout.append(grid[r][c])
    else:
        for c in range(GRID_DIM):
            for r in range(GRID_DIM):
                if grid[r][c] != -1:
                    readout.append(grid[r][c])

    return readout


def sweep_fleissner_worker_chunk(
    start_idx: int,
    end_idx: int,
    orbits: List[List[Tuple[int, int]]],
    known_panel_b_positions: Dict[int, Tuple[str, str]],  # cell_idx (0..47) -> (C, P)
    alphabet: str = STANDARD_ALPHABET,
    max_period: int = 7,
) -> List[Dict[str, Any]]:
    """
    Sweeps a slice of the 4^12 keyspace.
    Tests if candidate grille produces periodic key consistency on Panel B cribs.
    """
    hits = []

    for code in range(start_idx, end_idx):
        # Decode integer into 12 base-4 digits
        temp = code
        holes = []
        for _ in range(NUM_ORBITS):
            holes.append(temp & 3)
            temp >>= 2

        # Generate permutation
        pi = generate_fleissner_permutation(tuple(holes), orbits, clockwise=True, readout_by_rows=True)
        if len(pi) != 48:
            continue

        # Check periodic consistency:
        # At cell pos in Panel B, ciphertext is C, plaintext is P.
        # Under pi, message position is t = pi[pos].
        # If substitution key repeats with period L:
        # key(t) == (C - P) mod 26 must be constant for all t mod L.
        for L in range(1, max_period + 1):
            residues: Dict[int, int] = {}
            valid = True
            for pos, (c_char, p_char) in known_panel_b_positions.items():
                if pos >= len(pi):
                    continue
                t_pos = pi[pos]
                rem = t_pos % L
                req_k = (alphabet.index(c_char) - alphabet.index(p_char)) % 26
                if rem in residues:
                    if residues[rem] != req_k:
                        valid = False
                        break
                else:
                    residues[rem] = req_k

            if valid and len(residues) >= 4:
                hits.append({
                    "grille_code": code,
                    "holes": holes,
                    "period": L,
                    "residues_tested": len(residues),
                })

    return hits


def run_parallel_fleissner_sweep(
    num_processes: int = 4,
    max_eval: int = 1_000_000,
) -> Dict[str, Any]:
    """
    Executes parallel sweep of Fleissner Turning Grilles across candidate keyspace.
    """
    orbits, center = compute_7x7_orbits()

    # Panel B known positions:
    # In 7x14 grid, Panel B occupies cols 7..13.
    # Row 1 (linear 7..13 in Panel B): Crib 1 (EASTNOR)
    # Row 4 (linear 28..34 in Panel B): Crib 2 (BERLINC)
    pairs = extract_known_pairs()
    panel_b_anchors: Dict[int, Tuple[str, str]] = {}
    for idx, c, p in pairs:
        r = idx // 14
        col = idx % 14
        if col >= 7:
            local_c = col - 7
            cell_idx = r * 7 + local_c
            panel_b_anchors[cell_idx] = (c, p)

    total_keys = min(4**NUM_ORBITS, max_eval)
    chunk_size = total_keys // num_processes

    tasks = []
    for p in range(num_processes):
        s = p * chunk_size
        e = (p + 1) * chunk_size if p < num_processes - 1 else total_keys
        tasks.append((s, e))

    pool = mp.Pool(processes=num_processes)
    async_results = [
        pool.apply_async(
            sweep_fleissner_worker_chunk,
            args=(s, e, orbits, panel_b_anchors, STANDARD_ALPHABET, 7),
        )
        for s, e in tasks
    ]
    pool.close()
    pool.join()

    all_hits = []
    for r in async_results:
        all_hits.extend(r.get())

    return {
        "total_evaluated": total_keys,
        "total_hits": len(all_hits),
        "hits": all_hits[:10],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="7x7 Fleissner Turning Grille Sweeper")
    parser.add_argument("--cores", type=int, default=mp.cpu_count(), help="Number of CPU worker cores")
    parser.add_argument("--eval-limit", type=int, default=1_048_576, help="Evaluation limit (default 1M)")
    args = parser.parse_args()

    print("=" * 70)
    print("CIPHERLAB — TIER 2 FLEISSNER 7x7 TURNING GRILLE SWEEPER")
    print(f"Workers: {args.cores} CPU cores | Sample Keyspace: {args.eval_limit:,} grilles")
    print("=" * 70)

    t0 = time.time()
    res = run_parallel_fleissner_sweep(num_processes=args.cores, max_eval=args.eval_limit)
    elapsed = time.time() - t0

    print(f"\nExecution Time: {elapsed:.3f}s ({res['total_evaluated'] / elapsed:,.0f} grilles/sec)")
    print(f"Total Evaluated: {res['total_evaluated']:,}")
    print(f"Total Consistent Grilles: {res['total_hits']}")
    if res["hits"]:
        for h in res["hits"]:
            print(f"  -> Grille Code: {h['grille_code']} | Holes: {h['holes']} | Period: {h['period']} (Tested {h['residues_tested']} res)")
    print("=" * 70)
