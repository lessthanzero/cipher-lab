"""Coordinated Multi-Crib SAT Inversion for D'Agapeyeff Two-Square.

Simultaneously evaluates candidate English clauses across all 7 garbled segments:
1. Pos 7..16:   "GRADI E S CARON GOS" (fixing C -> S: Degrees South)
2. Pos 44..53:  "AID IF IT IS" (fixing IE V -> IF)
3. Pos 54..63:  "CAUSE ORDER MEN" (or "TO USE ORDER MEN")
4. Pos 75..86:  "WHERE A CLOSURE" (fixing WHEE AC LOCURE)
5. Pos 87..103: "MILITARY CIVIL CASE" or "SPECIAL CASE"
6. Pos 107..125:"YET AT ALL PORTS BOUND WERE" (fixing YT AT ALI BUTS BOUN)
7. Pos 145..158:"SECTOR ENSURE" (fixing NECT ORE SURE)

For each candidate clause combination:
Uses Z3 to determine if a valid bijective pair of 5x5 Polybius squares exists
that satisfies all letter constraints simultaneously.
"""

from __future__ import annotations

import itertools
from typing import Dict, List, Optional, Set, Tuple

import z3

from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)
from projects.dagapeyeff.algebraic_cell_extractor import get_winning_coordinates
from projects.dagapeyeff.two_square import STANDARD_ALPHABET, TwoSquareEngine

TARGET_SQ1 = "BDCOATXLUIGSRENHPWMYFZKQV"
TARGET_SQ2 = "WIMLTVRGCNESDYAKOZUBXFPHQ"

# Highly invariant anchor letters (positions and known letters)
# These form the immutable core of the message
CORE_INVARIANTS: List[Tuple[int, str]] = [
    # 0..8: "BDN GRADI"
    (0, "B"), (1, "D"), (2, "N"), (3, "G"), (4, "R"), (5, "A"), (6, "D"), (7, "I"), (8, "E"),
    # 17..37: "SOME AS SHE SEND ARDS WERE"
    (17, "S"), (18, "O"), (19, "M"), (20, "E"), (21, "A"), (22, "S"), (23, "S"), (24, "H"),
    (25, "E"), (26, "S"), (27, "E"), (28, "N"), (29, "D"), (30, "A"), (31, "R"), (32, "D"),
    (33, "S"), (34, "W"), (35, "E"), (36, "R"), (37, "E"),
    # 44..46: "AID"
    (44, "A"), (45, "I"), (46, "D"),
    # 51..53: "IS"
    (51, "I"), (52, "T"), (53, "I"), (54, "S"),
    # 62..67: "MEN GET"
    (62, "M"), (63, "E"), (64, "N"), (65, "G"), (66, "E"), (67, "T"),
    # 72..74: "ARE"
    (72, "A"), (73, "R"), (74, "E"),
    # 100..103: "CASE"
    (100, "C"), (101, "A"), (102, "S"), (103, "E"),
    # 104..106: "BUT"
    (104, "B"), (105, "U"), (106, "T"),
    # 122..125: "WERE"
    (122, "W"), (123, "E"), (124, "R"), (125, "E"),
    # 138..144: "ON MORNING"
    (138, "O"), (139, "N"), (140, "N"), (141, "I"), (142, "N"), (143, "G"),
    # 144..147: "TOIL"
    (144, "T"), (145, "O"), (146, "I"), (147, "L"),
    # 155..158: "SURE"
    (155, "S"), (156, "U"), (157, "R"), (158, "E"),
    # 159..163: "DAY BY"
    (159, "D"), (160, "A"), (161, "Y"), (162, "B"), (163, "Y"),
    # 169..173: "WING"
    (169, "W"), (170, "I"), (171, "N"), (172, "G"),
]

# Candidate hypotheses for the 7 garbled segments
CANDIDATE_BRANCHES: Dict[str, List[List[Tuple[int, str]]]] = {
    "Preamble_Deg": [
        [(9, "S")],  # Degrees South (fixing C -> S, couples with CLOSURE!)
        [(9, "C")],  # Degrees Compass
    ],
    "Aid_Condition": [
        [(47, "F"), (48, "I"), (49, "T"), (50, "I")],  # "FIT I..."
        [(47, "I"), (48, "F"), (49, "I"), (50, "T")],  # "IF IT..."
        [(47, "I"), (48, "E"), (49, "V"), (50, "I")],  # Baseline "IEVI..."
    ],
    "Closure_Clause": [
        # WHERE A CLOSURE (Pos 75..86)
        [
            (75, "W"), (76, "H"), (77, "E"), (78, "R"), (79, "E"),
            (80, "A"), (81, "C"), (82, "L"), (83, "O"), (84, "S"), (85, "U"), (86, "R"), (87, "E")
        ],
        # Baseline WHEE AC LOCURE
        [
            (75, "W"), (76, "H"), (77, "E"), (78, "E"), (79, "A"),
            (80, "C"), (81, "L"), (82, "O"), (83, "C"), (84, "U"), (85, "R"), (86, "E")
        ],
    ],
    "Bound_Clause": [
        # YET AT ALL PORTS BOUND (Pos 107..121)
        [
            (107, "Y"), (108, "E"), (109, "T"), (110, "A"), (111, "T"),
            (112, "A"), (113, "L"), (114, "L"), (115, "P"), (116, "O"), (117, "R"), (118, "T"),
            (119, "S"), (120, "B"), (121, "O"), (122, "U"), (123, "N"), (124, "D")
        ],
        # Baseline YT AT ALI BUTS BOUN
        [
            (107, "Y"), (108, "T"), (109, "A"), (110, "T"), (111, "A"),
            (112, "L"), (113, "I"), (114, "B"), (115, "U"), (116, "T"), (117, "S"),
            (118, "B"), (119, "O"), (120, "U"), (121, "N")
        ],
    ],
    "Sector_Ensure": [
        # SECTOR ENSURE (Pos 148..158)
        [
            (148, "S"), (149, "E"), (150, "C"), (151, "T"), (152, "O"), (153, "R"),
            (154, "E"), (155, "N"), (156, "S"), (157, "U"), (158, "R"), (159, "E")
        ],
        # Baseline NECT ORE SURE
        [
            (148, "N"), (149, "E"), (150, "C"), (151, "T"), (152, "O"), (153, "R"),
            (154, "E"), (155, "S"), (156, "U"), (157, "R"), (158, "E")
        ],
    ]
}


def build_pos_map(coords: List[Tuple[int, int]]) -> Dict[int, Tuple[int, int, int]]:
    """Map message position -> (square, row, col)."""
    pos_map = {}
    for i in range(0, 182, 2):
        r1, c1 = coords[i]
        r2, c2 = coords[i + 1]
        tc1 = c2 if c1 != c2 else c1
        tc2 = c1 if c1 != c2 else c2
        pos_map[i] = (1, r1, tc1)
        pos_map[i + 1] = (2, r2, tc2)
    return pos_map


def test_crib_combination(
    candidate_constraints: List[Tuple[int, str]],
    pos_map: Dict[int, Tuple[int, int, int]],
    coords: List[Tuple[int, int]],
    scorer: QuadgramScorer,
    engine: TwoSquareEngine,
) -> Optional[Tuple[float, str, str, str]]:
    """Test if a set of constraints is SAT and evaluate fitness."""
    solver = z3.Solver()
    sq1_vars = [z3.Int(f"sq1_{r}_{c}") for r in range(5) for c in range(5)]
    sq2_vars = [z3.Int(f"sq2_{r}_{c}") for r in range(5) for c in range(5)]

    for v in sq1_vars + sq2_vars:
        solver.add(v >= 0, v < 25)

    solver.add(z3.Distinct(sq1_vars))
    solver.add(z3.Distinct(sq2_vars))

    char_to_val = {c: i for i, c in enumerate(STANDARD_ALPHABET)}
    val_to_char = {i: c for i, c in enumerate(STANDARD_ALPHABET)}

    # Check cell conflicts directly first
    sq1_cell_map: Dict[Tuple[int, int], str] = {}
    sq2_cell_map: Dict[Tuple[int, int], str] = {}

    for pos, char in candidate_constraints:
        if pos >= 182:
            continue
        char = char.upper().replace("J", "I")
        sq, r, c = pos_map[pos]
        if sq == 1:
            if (r, c) in sq1_cell_map and sq1_cell_map[(r, c)] != char:
                return None  # Direct conflict
            sq1_cell_map[(r, c)] = char
        else:
            if (r, c) in sq2_cell_map and sq2_cell_map[(r, c)] != char:
                return None
            sq2_cell_map[(r, c)] = char

    # Check distinct letters within the same square
    if len(set(sq1_cell_map.values())) != len(sq1_cell_map):
        return None
    if len(set(sq2_cell_map.values())) != len(sq2_cell_map):
        return None

    # Add constraints to Z3
    for (r, c), char in sq1_cell_map.items():
        solver.add(sq1_vars[r * 5 + c] == char_to_val[char])
    for (r, c), char in sq2_cell_map.items():
        solver.add(sq2_vars[r * 5 + c] == char_to_val[char])

    if solver.check() != z3.sat:
        return None

    model = solver.model()
    sq1_chars = [val_to_char[model[sq1_vars[i]].as_long()] for i in range(25)]
    sq2_chars = [val_to_char[model[sq2_vars[i]].as_long()] for i in range(25)]

    sq1_str = "".join(sq1_chars)
    sq2_str = "".join(sq2_chars)

    engine.set_alphabets(sq1_str, sq2_str)
    pt = engine.decipher_coordinates(coords)
    q = scorer.score_total(pt)

    return q, sq1_str, sq2_str, pt


def main() -> None:
    print("=" * 80)
    print("COORDINATED MULTI-CRIB SAT INVERSION")
    print("Testing linguistic hypothesis combinations across the 7 garbled segments")
    print("=" * 80)

    coords = get_winning_coordinates()
    pos_map = build_pos_map(coords)
    scorer = QuadgramScorer(language="english")
    engine = TwoSquareEngine(orientation="vertical", pairing_mode="sequential")

    branch_keys = list(CANDIDATE_BRANCHES.keys())
    branch_options = [CANDIDATE_BRANCHES[k] for k in branch_keys]

    total_combinations = 1
    for opt in branch_options:
        total_combinations *= len(opt)

    print(f"[*] Evaluating {total_combinations} combinatorial clause hypotheses in Z3...", flush=True)

    valid_solutions = []

    for combo in itertools.product(*branch_options):
        # Combine core invariants with this branch combination
        test_constraints = list(CORE_INVARIANTS)
        for clause in combo:
            test_constraints.extend(clause)

        res = test_crib_combination(test_constraints, pos_map, coords, scorer, engine)
        if res is not None:
            q, sq1, sq2, pt = res
            chi = calculate_chi_squared(pt)
            ioc = calculate_index_of_coincidence(pt)
            valid_solutions.append((q, chi, ioc, sq1, sq2, pt))
            print(f"[+] SAT VALID COMBINATION: Q={q:.1f} | chi2={chi:.1f} | ioc={ioc:.4f}", flush=True)
            print(f"    Preview: \"{pt[17:100]}...\"", flush=True)

    valid_solutions.sort(key=lambda x: x[0], reverse=True)

    print("\n" + "=" * 80)
    print(f"SAT EVALUATION COMPLETE: {len(valid_solutions)}/{total_combinations} combinations are mathematically valid")
    print("=" * 80)

    for i, (q, chi, ioc, sq1, sq2, pt) in enumerate(valid_solutions[:5], 1):
        print(f"\n{i}. Solution (Q={q:.1f}, chi2={chi:.1f}, ioc={ioc:.4f}):")
        print(f"   Square 1: {sq1}")
        print(f"   Square 2: {sq2}")
        print(f"   Plaintext:\n   \"{pt}\"")


if __name__ == "__main__":
    main()
