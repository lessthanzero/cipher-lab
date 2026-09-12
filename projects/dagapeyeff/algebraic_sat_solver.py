"""Algebraic SAT Two-Square Solver for D'Agapeyeff (1939).

Uses Z3 SMT solver to find the exact, unique 5x5 Polybius Squares
under the rigid geometric constraints of Vertical Two-Square decipherment,
seeded by the marginal posterior consensus from 14,173 ledger trials.
"""

from __future__ import annotations

from typing import Dict, Tuple

import z3
from cipher_lab.stats import QuadgramScorer, calculate_chi_squared, calculate_index_of_coincidence

from projects.dagapeyeff.algebraic_cell_extractor import get_winning_coordinates
from projects.dagapeyeff.linguistic_reconstruction import compute_posterior_consensus
from projects.dagapeyeff.two_square import STANDARD_ALPHABET, TwoSquareEngine


def solve_consensus_via_z3(confidence_threshold: float = 0.80) -> None:
    coords = get_winning_coordinates()
    consensus_text, consensus_stats = compute_posterior_consensus()

    solver = z3.Solver()

    # 25 integer variables for Square 1 and Square 2 (0..24 representing STANDARD_ALPHABET)
    sq1_vars = [z3.Int(f"sq1_{r}_{c}") for r in range(5) for c in range(5)]
    sq2_vars = [z3.Int(f"sq2_{r}_{c}") for r in range(5) for c in range(5)]

    # Domain constraints: 0 <= val < 25
    for v in sq1_vars + sq2_vars:
        solver.add(v >= 0, v < 25)

    # Distinct letter constraints (bijective 5x5 grid)
    solver.add(z3.Distinct(sq1_vars))
    solver.add(z3.Distinct(sq2_vars))

    # Pre-compute (square, row, col) for each of the 182 positions
    pos_map: Dict[int, Tuple[int, int, int]] = {}
    for i in range(0, 182, 2):
        r1, c1 = coords[i]
        r2, c2 = coords[i + 1]

        target_c1 = c2 if c1 != c2 else c1
        target_c2 = c1 if c1 != c2 else c2

        pos_map[i] = (1, r1, target_c1)
        pos_map[i + 1] = (2, r2, target_c2)

    char_to_val = {c: i for i, c in enumerate(STANDARD_ALPHABET)}
    val_to_char = {i: c for i, c in enumerate(STANDARD_ALPHABET)}

    # High-confidence consensus characters
    high_conf = [s for s in consensus_stats if s.confidence >= confidence_threshold]
    print(f"[*] Total High-Confidence Positions (>= {confidence_threshold*100:.0f}%): {len(high_conf)}/182")

    # Group constraints by cell
    cell_votes: Dict[Tuple[int, int, int], Dict[str, int]] = {}
    for s in high_conf:
        sq, r, c = pos_map[s.position]
        key = (sq, r, c)
        if key not in cell_votes:
            cell_votes[key] = {}
        cell_votes[key][s.consensus_char] = cell_votes[key].get(s.consensus_char, 0) + 1

    print(f"[*] Cells addressed by high-confidence consensus: {len(cell_votes)}/50 total cells")

    # Add consistent cell constraints
    cells_assigned_sq1 = 0
    cells_assigned_sq2 = 0
    assigned_letters_sq1 = set()
    assigned_letters_sq2 = set()

    for (sq, r, c), votes in sorted(cell_votes.items()):
        # Pick the majority letter for this cell
        sorted_votes = sorted(votes.items(), key=lambda x: x[1], reverse=True)
        top_char = sorted_votes[0][0]
        
        # Check if this letter is already assigned to another cell in the same square
        if sq == 1:
            if top_char not in assigned_letters_sq1:
                solver.add(sq1_vars[r * 5 + c] == char_to_val[top_char])
                assigned_letters_sq1.add(top_char)
                cells_assigned_sq1 += 1
                print(f"  Sq1[{r},{c}] = '{top_char}' (votes: {votes})")
            else:
                print(f"  [!] Skip duplicate letter '{top_char}' for Sq1[{r},{c}]")
        else:
            if top_char not in assigned_letters_sq2:
                solver.add(sq2_vars[r * 5 + c] == char_to_val[top_char])
                assigned_letters_sq2.add(top_char)
                cells_assigned_sq2 += 1
                print(f"  Sq2[{r},{c}] = '{top_char}' (votes: {votes})")
            else:
                print(f"  [!] Skip duplicate letter '{top_char}' for Sq2[{r},{c}]")

    print(f"\n[*] Directly locked in Z3: Square 1 = {cells_assigned_sq1}/25 cells | Square 2 = {cells_assigned_sq2}/25 cells")

    # Check satisfiability and solve!
    print("\n[*] Solving Z3 constraint system for remaining unassigned cells...")
    check_res = solver.check()
    print(f"[*] Z3 Solver Result: {check_res}")

    if check_res == z3.sat:
        model = solver.model()
        sq1_chars = [val_to_char[model[sq1_vars[i]].as_long()] for i in range(25)]
        sq2_chars = [val_to_char[model[sq2_vars[i]].as_long()] for i in range(25)]

        sq1_str = "".join(sq1_chars)
        sq2_str = "".join(sq2_chars)

        print("\n" + "=" * 80)
        print("ALGEBRAIC SAT TWO-SQUARE SOLUTION:")
        print("=" * 80)
        print(f"Square 1 ({sq1_str}):")
        for r in range(5):
            print("  " + " ".join(sq1_chars[r * 5 : (r + 1) * 5]))

        print(f"\nSquare 2 ({sq2_str}):")
        for r in range(5):
            print("  " + " ".join(sq2_chars[r * 5 : (r + 1) * 5]))

        engine = TwoSquareEngine(alphabet1=sq1_str, alphabet2=sq2_str, orientation="vertical", pairing_mode="sequential")
        pt = engine.decipher_coordinates(coords)
        scorer = QuadgramScorer(language="english")
        q = scorer.score_total(pt)
        chi = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)

        print("\nDecrypted Plaintext (182 positions):")
        print(f"\"{pt}\"")
        print(f"Q-Score: {q:.1f} | Chi2: {chi:.1f} | IoC: {ioc:.4f}")
    else:
        print("[!] Solver returned unsat. Check for conflicting letter assignments.")


if __name__ == "__main__":
    solve_consensus_via_z3(confidence_threshold=0.80)
