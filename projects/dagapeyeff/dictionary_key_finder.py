"""Exhaustive Dictionary Key Finder for D'Agapeyeff Polybius Squares.

Searches 235,000 words from /usr/share/dict/words across all 6 classical grid topologies:
- horizontal_ltr
- horizontal_rtl
- vertical_ttb
- spiral_in
- boustrophedon
- reverse_remainder

Measures:
1. Exact character overlap with Target Square 1 and Target Square 2.
2. Coordinate distance (Manhattan distance in 5x5 grid) to target squares.
3. Decipherment Q-score on the 182-character D'Agapeyeff ciphertext.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Set, Tuple

from cipher_lab.stats import QuadgramScorer

from projects.dagapeyeff.algebraic_cell_extractor import get_winning_coordinates
from projects.dagapeyeff.polybius_reverse_key import make_polybius_grid
from projects.dagapeyeff.two_square import STANDARD_ALPHABET, TwoSquareEngine

TARGET_SQ1 = "BDCOATXLUIGSRENHPWMYFZKQV"
TARGET_SQ2 = "WIMLTVRGCNESDYAKOZUBXFPHQ"

METHODS = [
    "horizontal_ltr",
    "horizontal_rtl",
    "vertical_ttb",
    "spiral_in",
    "boustrophedon",
    "reverse_remainder",
]


def load_candidate_words(min_len: int = 4, max_len: int = 16) -> List[str]:
    """Load and filter English words from system dictionary."""
    dict_path = Path("/usr/share/dict/words")
    if not dict_path.exists():
        return []

    words: Set[str] = set()
    with open(dict_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            w = line.strip().upper().replace("J", "I")
            if min_len <= len(w) <= max_len and all(c in STANDARD_ALPHABET for c in w):
                words.add(w)
    return sorted(list(words))


def manhattan_distance_5x5(grid_a: str, grid_b: str) -> int:
    """Sum of Manhattan grid distances for matching letters between two 5x5 grids."""
    pos_a = {c: (i // 5, i % 5) for i, c in enumerate(grid_a)}
    pos_b = {c: (i // 5, i % 5) for i, c in enumerate(grid_b)}
    total_dist = 0
    for c in STANDARD_ALPHABET:
        if c in pos_a and c in pos_b:
            r1, c1 = pos_a[c]
            r2, c2 = pos_b[c]
            total_dist += abs(r1 - r2) + abs(c1 - c2)
    return total_dist


def main() -> None:
    print("=" * 80)
    print("EXHAUSTIVE DICTIONARY KEY INVERSION FOR SQUARE 1 & SQUARE 2")
    print("=" * 80)

    words = load_candidate_words(min_len=4, max_len=16)
    print(f"[*] Loaded {len(words):,} clean candidate keywords from /usr/share/dict/words")

    best_sq1_matches: List[Tuple[int, int, str, str]] = []  # (exact_matches, -dist, word, method)
    best_sq2_matches: List[Tuple[int, int, str, str]] = []

    for w in words:
        for m in METHODS:
            try:
                g = make_polybius_grid(w, method=m)
                # Compare to Square 1
                exact1 = sum(1 for a, b in zip(g, TARGET_SQ1) if a == b)
                dist1 = manhattan_distance_5x5(g, TARGET_SQ1)
                best_sq1_matches.append((exact1, -dist1, w, m))

                # Compare to Square 2
                exact2 = sum(1 for a, b in zip(g, TARGET_SQ2) if a == b)
                dist2 = manhattan_distance_5x5(g, TARGET_SQ2)
                best_sq2_matches.append((exact2, -dist2, w, m))
            except Exception:
                continue

    # Sort by exact matches descending, then lowest Manhattan distance
    best_sq1_matches.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best_sq2_matches.sort(key=lambda x: (x[0], x[1]), reverse=True)

    print("\n" + "=" * 80)
    print("TOP 15 KEYWORD MATCHES FOR SQUARE 1 (Target: BDCOATXLUIGSRENHPWMYFZKQV):")
    print("=" * 80)
    for i, (exact, neg_dist, w, m) in enumerate(best_sq1_matches[:15], 1):
        g = make_polybius_grid(w, method=m)
        print(f"{i:2d}. [{exact:2d}/25 exact, dist={-neg_dist:3d}] Word: {w:16s} Method: {m:16s} Grid: {g}")

    print("\n" + "=" * 80)
    print("TOP 15 KEYWORD MATCHES FOR SQUARE 2 (Target: WIMLTVRGCNESDYAKOZUBXFPHQ):")
    print("=" * 80)
    for i, (exact, neg_dist, w, m) in enumerate(best_sq2_matches[:15], 1):
        g = make_polybius_grid(w, method=m)
        print(f"{i:2d}. [{exact:2d}/25 exact, dist={-neg_dist:3d}] Word: {w:16s} Method: {m:16s} Grid: {g}")

    # Now let's evaluate the top pairs with our TwoSquareEngine against ciphertext
    print("\n" + "=" * 80)
    print("EVALUATING TOP MATCHING KEYWORD PAIRS AGAINST 182-CHAR CIPHERTEXT")
    print("=" * 80)

    coords = get_winning_coordinates()
    engine = TwoSquareEngine(orientation="vertical", pairing_mode="sequential")
    scorer = QuadgramScorer(language="english")

    top_sq1_candidates = best_sq1_matches[:8]
    top_sq2_candidates = best_sq2_matches[:8]

    scored_pairs = []
    for _, _, w1, m1 in top_sq1_candidates:
        g1 = make_polybius_grid(w1, method=m1)
        for _, _, w2, m2 in top_sq2_candidates:
            g2 = make_polybius_grid(w2, method=m2)
            engine.set_alphabets(g1, g2)
            pt = engine.decipher_coordinates(coords)
            q = scorer.score_total(pt)
            scored_pairs.append((q, w1, m1, w2, m2, pt[:70]))

    scored_pairs.sort(key=lambda x: x[0], reverse=True)
    print("\nTop Evaluated Pairs:")
    for i, (q, w1, m1, w2, m2, preview) in enumerate(scored_pairs[:10], 1):
        print(f"{i:2d}. Q={q:6.1f} | Sq1={w1} ({m1}) | Sq2={w2} ({m2})")
        print(f"    Preview: \"{preview}...\"")


if __name__ == "__main__":
    main()
