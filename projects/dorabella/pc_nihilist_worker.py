"""Dedicated Fedora PC Nihilist Coordinate Batch Worker."""

from __future__ import annotations

import json
import sys
from typing import List

from projects.dorabella.nihilist_coordinate_solver import NihilistCoordinateSolver

def main():
    if len(sys.argv) < 2:
        print("[PC Worker] No keywords passed.")
        return

    keywords = sys.argv[1:]
    solver = NihilistCoordinateSolver()
    scores = []
    best_kw = None
    best_q = -9999.0

    for k in keywords:
        res = solver.evaluate_keyword(k, mode="subtract")
        scores.append(res.q_score)
        if res.q_score > best_q:
            best_q = res.q_score
            best_kw = k

    print(f"[PC Worker] Evaluated {len(scores)} keywords. Best: {best_kw} (Q = {best_q:.1f})")

if __name__ == "__main__":
    main()
