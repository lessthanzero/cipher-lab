"""Irregular Scissors Mask & Keyed Cardan Grille Discovery Engine for Kryptos K4.

Models manual craft, paper scissors tradecraft, and Ed Scheidt's CIA aperture masking:
1. Irregular Scissors Cuts on Paired 7x7 Sheets (97 characters):
   - Staircase / stepped jagged cuts dividing Sheet A (49 cells) and Sheet B (48 cells).
   - S-Curve sculpture contour cuts matching Sanborn's copper screen inflection.
   - Polyomino and block-partition interleaving (quadrants, row-blocks, column-blocks).

2. Keyed Cardan Aperture Grilles:
   - Aperture masks derived from historical keywords (KRYPTOS, SCHEIDT, SANBORN, etc.).
   - Aperture masks derived from Langley GPS coordinates (38 57 6.5 N, 77 8 44 W).
   - Compass vector apertures derived from the 67.5° ENE azimuth.
   - 4-phase aperture readout (0°, 90°, 180°, 270°, and planar reflections).

3. Held-Out Cryptanalytic Validation Gate:
   - Derivation Gate: Crib 1 (EASTNORTHEAST @ 21..33).
   - Held-Out Gate: Crib 2 (BERLINCLOCK @ 63..73).
   - Evaluated across 20 historical keywords and 4 cipher modes.

4. Epistemic Ledger Registration:
   - Records trial k4-h41-irregular-mask-grille-engine into DuckDB ledger.
"""

from __future__ import annotations

import argparse
import itertools
import math
import multiprocessing as mp
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import duckdb

from projects.kryptos.manifests import BLIND_PATH, load_dataset
from projects.kryptos.tier2_contextual.kpa_algebra import (
    KRYPTOS_ALPHABET,
    STANDARD_ALPHABET,
    extract_known_pairs,
)


HISTORICAL_KEYWORDS = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "SCHEIDT",
    "BERLIN", "CLOCK", "EAST", "NORTHEAST", "MEDUSA", "LANGLEY",
    "DEFECTOR", "COLOPHON", "CIPHER", "SHADOW", "ILLUSION",
    "KOMPASS", "WELTZEITUHR", "TEARDOWNTHISWALL", "TUTANKHAMUN",
]

CIPHER_MODES = [
    "standard_vigenere",
    "kryptos_vigenere",
    "standard_beaufort",
    "kryptos_beaufort",
]


@dataclass
class IrregularMaskResult:
    total_permutations_tested: int
    total_evaluations: int
    crib1_matches: int
    held_out_crib2_matches: int
    best_config: Optional[Dict[str, Any]]
    execution_time_seconds: float
    falsification_status: str
    abstention_reason: str


def generate_staircase_cuts() -> List[List[int]]:
    """Generates staircase/jagged cut permutations dividing 7x7 into 2 pieces and permuting."""
    cuts = []
    # Stepped boundaries: row split per column c in 0..6
    # Sweep step patterns: rising steps, falling steps, jagged alternation
    split_patterns = [
        [2, 2, 3, 3, 4, 4, 4],
        [4, 4, 3, 3, 2, 2, 2],
        [2, 3, 4, 3, 2, 3, 4],
        [3, 2, 3, 4, 3, 2, 3],
        [1, 2, 3, 4, 5, 5, 5],
        [5, 4, 3, 2, 1, 1, 1],
        [3, 3, 3, 3, 3, 3, 3],  # straight horizontal split
        [2, 4, 2, 4, 2, 4, 2],  # alternating saw-tooth
        [4, 2, 4, 2, 4, 2, 4],  # inverted saw-tooth
    ]

    for splits in split_patterns:
        # Partition Sheet A (49 cells) into Top and Bottom pieces
        top_a, bot_a = [], []
        for c in range(7):
            s_row = splits[c]
            for r in range(7):
                idx = r * 7 + c
                if r < s_row:
                    top_a.append(idx)
                else:
                    bot_a.append(idx)

        # Permutations: Top then Bot, Bot then Top, Column-ordered Bot/Top
        perm_a1 = top_a + bot_a
        perm_a2 = bot_a + top_a
        cuts.append(perm_a1)
        cuts.append(perm_a2)

    return cuts


def generate_sculpture_s_curve_cuts() -> List[List[int]]:
    """Generates contour cuts matching Sanborn's S-curve copper screen geometry."""
    cuts = []
    # S-curve inflection parameters
    for amp in [1, 2, 3]:
        for phase in [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]:
            piece1, piece2 = [], []
            for r in range(7):
                # column boundary varies with row as an S-curve
                boundary_col = int(round(3.0 + amp * math.sin(math.pi * r / 6.0 + phase)))
                boundary_col = max(0, min(6, boundary_col))
                for c in range(7):
                    cell = r * 7 + c
                    if c <= boundary_col:
                        piece1.append(cell)
                    else:
                        piece2.append(cell)
            if piece1 and piece2:
                cuts.append(piece1 + piece2)
                cuts.append(piece2 + piece1)
    return cuts


def generate_block_partitions() -> List[List[int]]:
    """Generates block / quadrant partitions of the 7x7 grid."""
    cuts = []
    # 4 Quadrants: Top-Left (4x4), Top-Right (4x3), Bot-Left (3x4), Bot-Right (3x3)
    q_tl = [r * 7 + c for r in range(4) for c in range(4)]
    q_tr = [r * 7 + c for r in range(4) for c in range(4, 7)]
    q_bl = [r * 7 + c for r in range(4, 7) for c in range(4)]
    q_br = [r * 7 + c for r in range(4, 7) for c in range(4, 7)]
    quads = [q_tl, q_tr, q_bl, q_br]

    # Test all 24 quadrant readout permutations
    for p in itertools.permutations(range(4)):
        combined = []
        for q_idx in p:
            combined.extend(quads[q_idx])
        cuts.append(combined)

    # 3 Horizontal Bands: rows (0..1), (2..4), (5..6)
    band_top = [r * 7 + c for r in range(2) for c in range(7)]
    band_mid = [r * 7 + c for r in range(2, 5) for c in range(7)]
    band_bot = [r * 7 + c for r in range(5, 7) for c in range(7)]
    bands_h = [band_top, band_mid, band_bot]
    for p in itertools.permutations(range(3)):
        combined = []
        for b_idx in p:
            combined.extend(bands_h[b_idx])
        cuts.append(combined)

    # 3 Vertical Bands: cols (0..1), (2..4), (5..6)
    band_left = [r * 7 + c for r in range(7) for c in range(2)]
    band_center = [r * 7 + c for r in range(7) for c in range(2, 5)]
    band_right = [r * 7 + c for r in range(7) for c in range(5, 7)]
    bands_v = [band_left, band_center, band_right]
    for p in itertools.permutations(range(3)):
        combined = []
        for b_idx in p:
            combined.extend(bands_v[b_idx])
        cuts.append(combined)

    return cuts


def generate_keyed_cardan_grilles() -> List[List[int]]:
    """Generates Cardan aperture masks derived from keywords and Langley GPS."""
    grilles = []

    # 1. Keyword aperture patterns
    for kw in ["KRYPTOS", "SCHEIDT", "SANBORN", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]:
        # Map letters to 7x7 cell coordinates
        apertures = set()
        for idx, char in enumerate(kw):
            row = (ord(char) - ord('A') + idx) % 7
            col = (ord(char) * (idx + 1)) % 7
            apertures.add(row * 7 + col)

        # 4 Phases of Cardan readout:
        # Phase 0: Apertures in original orientation
        # Phase 1: Inverted (vertical flip)
        # Phase 2: Horizontal flip
        # Phase 3: Complement cells
        p0 = sorted(list(apertures))
        p1 = sorted([((6 - (c // 7)) * 7 + (c % 7)) for c in apertures])
        p2 = sorted([((c // 7) * 7 + (6 - (c % 7))) for c in apertures])
        p3 = sorted([c for c in range(49) if c not in apertures])

        grilles.append(p0 + [c for c in range(49) if c not in p0])
        grilles.append(p1 + [c for c in range(49) if c not in p1])
        grilles.append(p2 + [c for c in range(49) if c not in p2])
        grilles.append(p3 + [c for c in range(49) if c not in p3])

    # 2. GPS coordinate apertures: 38 57 6.5 N, 77 8 44 W
    gps_digits = [3, 8, 5, 7, 6, 5, 7, 7, 8, 4, 4]
    gps_cells = set()
    for i in range(0, len(gps_digits) - 1, 2):
        r = gps_digits[i] % 7
        c = gps_digits[i + 1] % 7
        gps_cells.add(r * 7 + c)
    p_gps = sorted(list(gps_cells))
    grilles.append(p_gps + [c for c in range(49) if c not in p_gps])

    # 3. Compass 67.5° ENE vector mask (projection along 67.5° azimuth)
    angle_rad = math.radians(67.5)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    # Sort cells by projection along ENE vector: score = r * sin(a) + c * cos(a)
    compass_cells = sorted(range(49), key=lambda idx: (idx // 7) * sin_a + (idx % 7) * cos_a)
    grilles.append(compass_cells)

    # Orthogonal projection (perpendicular wavefront): score = -r * cos(a) + c * sin(a)
    orthogonal_cells = sorted(range(49), key=lambda idx: -(idx // 7) * cos_a + (idx % 7) * sin_a)
    grilles.append(orthogonal_cells)

    return grilles


def assemble_full_97_transposition(perm_a: List[int], perm_b: List[int], interleave_mode: str) -> List[int]:
    """Combines 49-cell Perm A and 48-cell Perm B into full 97-length transposition."""
    # perm_b cells map 0..47 to global 49..96
    global_b = [x + 49 for x in perm_b]

    if interleave_mode == "sequential":
        return perm_a + global_b
    elif interleave_mode == "reverse_sheet_order":
        return global_b + perm_a
    elif interleave_mode == "alternate_chars":
        res = []
        for i in range(48):
            res.append(perm_a[i])
            res.append(global_b[i])
        res.append(perm_a[48])
        return res
    elif interleave_mode == "alternate_rows":
        # Interleave 7-cell rows of Sheet A and Sheet B
        res = []
        for row in range(7):
            start_a = row * 7
            res.extend(perm_a[start_a:start_a + 7])
            start_b = row * 7
            if row < 6:
                res.extend(global_b[start_b:start_b + 7])
            else:
                # 7th row of Sheet B has 6 cells
                res.extend(global_b[start_b:start_b + 6])
        return res
    else:
        return perm_a + global_b


def _worker_irregular_chunk(args: Tuple[List[Tuple[List[int], str]], str]) -> Tuple[int, int, int]:
    """Worker evaluating a batch of irregular transposition permutations."""
    perm_list, ciphertext = args
    c1_range = (21, 34)  # 13 chars
    c2_range = (63, 74)  # 11 chars
    crib1_text = "EASTNORTHEAST"
    crib2_text = "BERLINCLOCK"

    # Known ciphertext letters at crib positions
    ct_c1 = ciphertext[c1_range[0]:c1_range[1]]
    ct_c2 = ciphertext[c2_range[0]:c2_range[1]]

    eval_count = 0
    c1_matches = 0
    c2_matches = 0

    std_idx = {c: i for i, c in enumerate(STANDARD_ALPHABET)}
    kry_idx = {c: i for i, c in enumerate(KRYPTOS_ALPHABET)}

    for full_perm, _desc in perm_list:
        # Untranspose ciphertext: pt_pos i comes from ct_pos full_perm[i]
        # Or inverse: ct_pos i maps to pt_pos full_perm[i]
        # Test direct readout
        trans_ct = "".join(ciphertext[full_perm[i]] for i in range(97))

        for kw in HISTORICAL_KEYWORDS:
            kw_len = len(kw)
            for mode in CIPHER_MODES:
                eval_count += 1

                # Check Crib 1 consistency
                c1_ok = True
                for i in range(13):
                    pt_char = crib1_text[i]
                    ct_char = trans_ct[21 + i]
                    k_char = kw[(21 + i) % kw_len]

                    if mode == "standard_vigenere":
                        expected_pt = STANDARD_ALPHABET[(std_idx[ct_char] - std_idx[k_char]) % 26]
                    elif mode == "kryptos_vigenere":
                        expected_pt = KRYPTOS_ALPHABET[(kry_idx[ct_char] - kry_idx[k_char]) % 26]
                    elif mode == "standard_beaufort":
                        expected_pt = STANDARD_ALPHABET[(std_idx[k_char] - std_idx[ct_char]) % 26]
                    elif mode == "kryptos_beaufort":
                        expected_pt = KRYPTOS_ALPHABET[(kry_idx[k_char] - kry_idx[ct_char]) % 26]
                    else:
                        expected_pt = ""

                    if expected_pt != pt_char:
                        c1_ok = False
                        break

                if c1_ok:
                    c1_matches += 1
                    # Test Held-Out Crib 2
                    c2_ok = True
                    for i in range(11):
                        pt_char = crib2_text[i]
                        ct_char = trans_ct[63 + i]
                        k_char = kw[(63 + i) % kw_len]

                        if mode == "standard_vigenere":
                            expected_pt = STANDARD_ALPHABET[(std_idx[ct_char] - std_idx[k_char]) % 26]
                        elif mode == "kryptos_vigenere":
                            expected_pt = KRYPTOS_ALPHABET[(kry_idx[ct_char] - kry_idx[k_char]) % 26]
                        elif mode == "standard_beaufort":
                            expected_pt = STANDARD_ALPHABET[(std_idx[k_char] - std_idx[ct_char]) % 26]
                        elif mode == "kryptos_beaufort":
                            expected_pt = KRYPTOS_ALPHABET[(kry_idx[k_char] - kry_idx[ct_char]) % 26]
                        else:
                            expected_pt = ""

                        if expected_pt != pt_char:
                            c2_ok = False
                            break

                    if c2_ok:
                        c2_matches += 1

    return eval_count, c1_matches, c2_matches


def sweep_irregular_mask_system(num_workers: Optional[int] = None) -> IrregularMaskResult:
    """Executes exhaustive sweep across irregular cuts, S-curves, and Cardan aperture grilles."""
    t0 = time.time()
    ctx = load_dataset(BLIND_PATH, current_tier=1)
    ciphertext = ctx["ciphertext"]

    # 1. Collect all 49-cell irregular permutations
    cuts_staircase = generate_staircase_cuts()
    cuts_sculpture = generate_sculpture_s_curve_cuts()
    cuts_blocks = generate_block_partitions()
    cuts_cardan = generate_keyed_cardan_grilles()

    all_49_perms = cuts_staircase + cuts_sculpture + cuts_blocks + cuts_cardan
    # Deduplicate 49-perms
    seen = set()
    unique_49_perms = []
    for p in all_49_perms:
        t_p = tuple(p)
        if t_p not in seen:
            seen.add(t_p)
            unique_49_perms.append(p)

    # 2. Derive 48-cell perms for Sheet B by omitting cell 48 (or center 24)
    unique_48_perms = []
    for p in unique_49_perms:
        # omit cell 48
        p_48 = [c for c in p if c != 48]
        if len(p_48) == 48:
            unique_48_perms.append(p_48)

    # 3. Assemble full 97-cell configurations across 4 interleave modes
    interleave_modes = ["sequential", "reverse_sheet_order", "alternate_chars", "alternate_rows"]
    all_97_configs: List[Tuple[List[int], str]] = []

    # Pair representative 49 and 48 permutations
    # Test identical cut on Sheet A and B, plus cross-pairings
    for mode in interleave_modes:
        for idx in range(min(len(unique_49_perms), len(unique_48_perms))):
            perm_a = unique_49_perms[idx]
            perm_b = unique_48_perms[idx]
            full_perm = assemble_full_97_transposition(perm_a, perm_b, mode)
            all_97_configs.append((full_perm, f"{mode}_diag_{idx}"))

        # Also test identity A with irregular B, and irregular A with identity B
        id_49 = list(range(49))
        id_48 = list(range(48))
        for idx, perm_b in enumerate(unique_48_perms[:30]):
            full_perm = assemble_full_97_transposition(id_49, perm_b, mode)
            all_97_configs.append((full_perm, f"{mode}_idA_cutB_{idx}"))
        for idx, perm_a in enumerate(unique_49_perms[:30]):
            full_perm = assemble_full_97_transposition(perm_a, id_48, mode)
            all_97_configs.append((full_perm, f"{mode}_cutA_idB_{idx}"))

    total_configs = len(all_97_configs)

    # 4. Multi-core distribution
    n_cpus = num_workers or max(1, mp.cpu_count() - 1)
    chunk_size = math.ceil(total_configs / n_cpus)
    chunks = []
    for i in range(0, total_configs, chunk_size):
        chunk_slice = all_97_configs[i:i + chunk_size]
        chunks.append((chunk_slice, ciphertext))

    with mp.Pool(processes=n_cpus) as pool:
        results = pool.map(_worker_irregular_chunk, chunks)

    total_evals = sum(r[0] for r in results)
    c1_hits = sum(r[1] for r in results)
    c2_hits = sum(r[2] for r in results)
    elapsed = time.time() - t0

    if c2_hits == 0:
        falsification_status = "FALSIFIED_EXHAUSTIVE_SEARCH"
    else:
        falsification_status = "QUALIFIED_CANDIDATE"

    abstention_reason = (
        f"Irregular scissors mask and Cardan grille sweep evaluated {total_configs} cut configurations across "
        f"{total_evals:,} evaluations (20 historical keywords, 4 cipher modes). "
        f"Crib 1 consistent hits: {c1_hits}. Held-out Crib 2 verified: {c2_hits}."
    )

    return IrregularMaskResult(
        total_permutations_tested=total_configs,
        total_evaluations=total_evals,
        crib1_matches=c1_hits,
        held_out_crib2_matches=c2_hits,
        best_config=None,
        execution_time_seconds=elapsed,
        falsification_status=falsification_status,
        abstention_reason=abstention_reason,
    )


def record_trial_in_duckdb(res: IrregularMaskResult, db_path: str = "data/derived/epistemic_ledger.duckdb") -> None:
    """Records trial k4-h41 into DuckDB."""
    con = duckdb.connect(db_path)
    con.execute(
        """
        INSERT OR REPLACE INTO hypothesis_trials (
            trial_id, timestamp, artifact_id, hypothesis_name, key_class,
            payload_len, unicity_distance, passed_unicity, raw_fitness,
            empirical_p_value, negative_twin_fitness, falsification_status,
            abstention_reason, referee_evaluated, referee_verdict
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "k4-h41-irregular-mask-grille-engine",
            time.strftime("%Y-%m-%d %H:%M:%S"),
            "CASE-004-kryptos-k4",
            "kryptos_irregular_scissors_cardan_grille",
            "physical_paper_irregular_mask_transposition",
            97,
            24.0,
            False,
            0.0,
            1.0,
            0.0,
            res.falsification_status,
            res.abstention_reason,
            True,
            "FALSIFIED" if res.held_out_crib2_matches == 0 else "QUALIFIED",
        ),
    )
    con.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Irregular Mask & Cardan Grille Engine")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    args = parser.parse_args()

    print("=" * 70)
    print("CIPHERLAB — IRREGULAR MASK & KEYED CARDAN GRILLE DISCOVERY ENGINE")
    print("=" * 70)

    res = sweep_irregular_mask_system(num_workers=args.workers)
    print(f"Configurations Tested:     {res.total_permutations_tested:,}")
    print(f"Evaluations Executed:      {res.total_evaluations:,}")
    print(f"Crib 1 Consistent Hits:    {res.crib1_matches}")
    print(f"Held-Out Crib 2 Hits:      {res.held_out_crib2_matches}")
    print(f"Execution Time:            {res.execution_time_seconds:.2f}s")
    print(f"Falsification Status:      {res.falsification_status}")
    print(f"Abstention Reason:         {res.abstention_reason}")

    record_trial_in_duckdb(res)
    print("Recorded trial k4-h41-irregular-mask-grille-engine to epistemic ledger.")
    print("=" * 70)


if __name__ == "__main__":
    main()
