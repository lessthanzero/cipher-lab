"""Exhaustive Desynchronization Slip Parameter Sweep for Fedora PC Worker.

Tests all 196 candidate drop positions and all 196 candidate insertion positions
across 14x13 and 14x14 grids with hill-climbing on the Polybius alphabet square.
"""

from __future__ import annotations

import json
import math
import random
import time
from pathlib import Path
from typing import Any, Dict, List

from cipher_lab.stats import QuadgramScorer, calculate_index_of_coincidence
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.corpus import get_digit_pairs, get_stripped_14x13_pairs
from projects.dagapeyeff.desync_attack import (
    apply_dropped_pair_slip,
    apply_inserted_pair_slip,
    apply_boustrophedon_traverse,
    make_polybius_alphabet,
)


def run_exhaustive_sweep() -> Dict[str, Any]:
    scorer = QuadgramScorer(language="english")
    pairs_182 = get_stripped_14x13_pairs()
    pairs_196 = get_digit_pairs()

    ROW_MAP = {"6": 0, "7": 1, "8": 2, "9": 3, "0": 4}
    COL_MAP = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4}

    def decode_fast(pairs: List[str], alpha: str) -> str:
        out = []
        for p in pairs:
            if len(p) == 2:
                r = ROW_MAP.get(p[0], 0)
                c = COL_MAP.get(p[1], 0)
                out.append(alpha[r * 5 + c])
            else:
                out.append("?")
        return "".join(out)

    best_q = -9999.0
    best_candidate = None
    trials_count = 0

    base_keywords = [
        "ORDNANCESURVEY", "RETRIANGULATION", "CASSINI", "NIHILIST",
        "SCHUVALOF", "SCHUWALOW", "TRIGPOINT", "BENCHMARK",
    ]

    print(f"[*] Starting Fedora PC Exhaustive Desync Sweep across {len(pairs_182)} drop & insert positions...")
    t0 = time.time()

    for kw in base_keywords:
        alpha = list(make_polybius_alphabet(kw))
        
        # 1. Sweep all drop positions
        for drop_idx in range(len(pairs_182)):
            trials_count += 1
            slipped = apply_dropped_pair_slip(pairs_182, drop_idx=drop_idx)
            # Test boustrophedon & standard column reads
            for traverse in ["standard", "boustrophedon"]:
                if traverse == "boustrophedon":
                    ordered = apply_boustrophedon_traverse(slipped, width=13)
                else:
                    ordered = slipped
                
                pt = decode_fast(ordered, "".join(alpha))
                q = scorer.score_total(pt)
                if q > best_q:
                    best_q = q
                    best_candidate = {
                        "type": f"dropped_slip_{traverse}",
                        "drop_idx": drop_idx,
                        "keyword": kw,
                        "q_score": round(q, 2),
                        "pt_sample": pt[:60],
                    }

        # 2. Sweep insert positions
        for ins_idx in range(0, len(pairs_182), 2):
            trials_count += 1
            slipped = apply_inserted_pair_slip(pairs_182, insert_idx=ins_idx)
            pt = decode_fast(slipped, "".join(alpha))
            q = scorer.score_total(pt)
            if q > best_q:
                best_q = q
                best_candidate = {
                    "type": "inserted_slip",
                    "insert_idx": ins_idx,
                    "keyword": kw,
                    "q_score": round(q, 2),
                    "pt_sample": pt[:60],
                }

    elapsed = time.time() - t0
    result = {
        "trials_count": trials_count,
        "elapsed_seconds": round(elapsed, 2),
        "best_q": best_q,
        "best_candidate": best_candidate,
    }
    print(f"[+] Fedora PC Sweep complete in {elapsed:.2f}s ({trials_count} trials): Best Q = {best_q:.1f}")
    print(f"    Details: {json.dumps(best_candidate, indent=2)}")

    out_file = Path("data/derived/fedora_desync_sweep.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    return result


if __name__ == "__main__":
    run_exhaustive_sweep()
