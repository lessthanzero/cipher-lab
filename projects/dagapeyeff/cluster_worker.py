"""Multi-Node Distributed Worker for D'Agapeyeff Cluster Campaign.

Executes high-throughput parallel simulated annealing + greedy hill-climbing polish
across available CPU cores on either macOS (Apple Silicon) or Fedora Linux (x86_64).

Explores:
- Winning key family: HYDROGRAPHICAL (with all duplicate tie-breaks) + Sibling Admiralty keys
- Cartographic Traversals on transposed grid: standard raster, Cartesian bottom-up, boustrophedon
- Vertical Two-Square rectangle coordinate transformations
- Logs candidate trials to JSONL for atomic multi-process / multi-node merging
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_index_of_coincidence,
)
from projects.dagapeyeff.admiralty_sweep import (
    ADMIRALTY_KEYWORDS_14,
    generate_hydrographical_duplicate_rankings,
)
from projects.dagapeyeff.benchmarks import evaluate_against_competition
from projects.dagapeyeff.cartographic_grid import (
    read_cartesian_bottom_up,
    read_cartographic_boustrophedon,
    read_diagonal_matrix_transpose,
)
from projects.dagapeyeff.corpus import get_digit_pairs
from projects.dagapeyeff.exact_14key_sweep import apply_generalized_double_transposition
from projects.dagapeyeff.hydrographical_deep_runner import (
    NAUTICAL_CARTOGRAPHIC_KEYWORDS,
    polish_state_hill_climb,
)
from projects.dagapeyeff.kerckhoffs_defect import get_standard_key_order
from projects.dagapeyeff.two_square import pairs_to_coordinates
from projects.dagapeyeff.two_square_annealer import (
    TwoSquareAnnealer,
    TwoSquareState,
)


@dataclass
class ClusterTrialResult:
    trial_id: str
    node_name: str
    worker_id: int
    keyword_label: str
    traversal: str
    direction: str
    order: str
    pairing: str
    dual_alphabets: bool
    q_score: float
    chi_sq: float
    ioc: float
    alphabet1: str
    alphabet2: str
    plaintext_preview: str
    timestamp: float


def apply_traversal_on_pairs(pairs: List[str], traversal: str, width: int = 14) -> List[str]:
    """Apply cartographic traversal convention to pairs."""
    if traversal == "cartesian_bottom_up":
        return read_cartesian_bottom_up(pairs, width=width)
    elif traversal == "boustrophedon_horiz":
        return read_cartographic_boustrophedon(pairs, width=width, vertical=False)
    elif traversal == "boustrophedon_vert":
        return read_cartographic_boustrophedon(pairs, width=width, vertical=True)
    else:  # standard raster
        return pairs


def run_worker_loop(
    worker_id: int,
    node_name: str,
    task_family: str,
    time_budget_secs: float,
    output_path: Path,
    seed: int,
) -> None:
    """Individual worker process executing continuous annealing + polish chains."""
    start_time = time.time()
    rng = random.Random(seed + worker_id * 1000)
    scorer = QuadgramScorer(language="english")

    raw_196 = get_digit_pairs()
    diag_182 = read_diagonal_matrix_transpose(raw_196, width=14)[:182]
    w, h = 14, 13

    # Configure candidate key library based on task family
    hydro_variants = generate_hydrographical_duplicate_rankings()
    if task_family == "hydrographical_focus":
        key_pool = hydro_variants
    elif task_family == "admiralty_siblings":
        key_pool = []
        for kw in ADMIRALTY_KEYWORDS_14:
            ranks = get_standard_key_order(kw)
            key_pool.append((kw, ranks[:w] if len(ranks) >= w else (ranks * 2)[:w]))
    else:  # full pool
        key_pool = hydro_variants
        for kw in ADMIRALTY_KEYWORDS_14:
            ranks = get_standard_key_order(kw)
            key_pool.append((kw, ranks[:w] if len(ranks) >= w else (ranks * 2)[:w]))

    traversals = ["standard", "cartesian_bottom_up", "boustrophedon_horiz"]
    directions = ["standard_encryption", "kerckhoffs_decryption"]
    orders = ["row_then_col", "col_then_row"]

    chain_idx = 0
    while (time.time() - start_time) < (time_budget_secs - 5.0):
        chain_idx += 1
        remaining_s = time_budget_secs - (time.time() - start_time)
        chain_duration = min(60.0, max(5.0, remaining_s * 0.1))

        # Sample parameters with Bayesian prior on empirically proven configurations
        label, ranks = rng.choice(key_pool)
        traversal = rng.choices(
            ["cartesian_bottom_up", "boustrophedon_horiz", "standard"],
            weights=[0.60, 0.25, 0.15],
            k=1,
        )[0]
        direction = "standard_encryption" if rng.random() < 0.85 else "kerckhoffs_decryption"
        order = "row_then_col" if rng.random() < 0.85 else "col_then_row"
        pairing = "sequential" if rng.random() < 0.80 else "vertical_grid"
        dual = True if rng.random() < 0.90 else False

        col_order = ranks
        row_ranks = ranks[:h]
        row_indexed = sorted(list(enumerate(row_ranks)), key=lambda x: (x[1], x[0]))
        row_order = [0] * h
        for r_i, (orig_i, _) in enumerate(row_indexed):
            row_order[orig_i] = r_i

        # 1. Double transposition on diag_182
        t_pairs = apply_generalized_double_transposition(
            diag_182,
            col_order=col_order,
            row_order=row_order,
            mode=direction,
            order=order,
        )

        # 2. Cartographic drafting traversal
        final_pairs = apply_traversal_on_pairs(t_pairs, traversal=traversal, width=w)

        # 3. Two-Square Annealer
        kw1 = rng.choice(NAUTICAL_CARTOGRAPHIC_KEYWORDS)
        kw2 = rng.choice(NAUTICAL_CARTOGRAPHIC_KEYWORDS)

        annealer = TwoSquareAnnealer(
            grid_mode="custom",
            orientation="vertical",
            dual_alphabets=dual,
            pairing_mode=pairing,
            with_transposition=False,
            language="english",
            seed_keyword1=kw1,
            seed_keyword2=kw2,
            lexical_bonus_weight=0.20,
            seed=rng.randint(1, 1000000),
        )
        annealer.pairs = final_pairs
        annealer.coords = pairs_to_coordinates(final_pairs)
        annealer._precompute_fixed_indices()

        raw_state = annealer.run_two_square_chain(
            duration_secs=chain_duration * 0.80,
            initial_temp=25.0,
            cooling_rate=0.9998,
        )

        # 4. Greedy hill-climbing polish (deeper steps)
        polished = polish_state_hill_climb(annealer, raw_state, max_steps=350)

        pt = polished.candidate_pt
        q_score = scorer.score_total(pt)
        chi = calculate_chi_squared(pt)
        ioc = calculate_index_of_coincidence(pt)

        trial = ClusterTrialResult(
            trial_id=f"{node_name}_w{worker_id}_c{chain_idx}_{int(time.time()*1000)%1000000}",
            node_name=node_name,
            worker_id=worker_id,
            keyword_label=label,
            traversal=traversal,
            direction=direction,
            order=order,
            pairing=pairing,
            dual_alphabets=dual,
            q_score=q_score,
            chi_sq=chi,
            ioc=ioc,
            alphabet1=polished.alphabet1,
            alphabet2=polished.alphabet2,
            plaintext_preview=pt[:70],
            timestamp=time.time(),
        )

        # Atomic append to JSONL output
        try:
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(trial)) + "\n")
        except Exception:
            pass

        if q_score > -846.5:
            print(f"[!] [{node_name}-W{worker_id}] RECORD: Q={q_score:.1f} (chi={chi:.1f}, ioc={ioc:.4f}) Key: {label} ({traversal}, {direction})", flush=True)
            print(f"    Preview: \"{pt[:70]}...\"", flush=True)

        if q_score > -692.13:
            print(f"!!! BREAKTHROUGH on {node_name}-W{worker_id}: Q={q_score:.1f} !!!", flush=True)
            print(f"Plaintext: {pt}", flush=True)
            break


def run_cluster_worker_pool(
    node_name: str,
    num_workers: int,
    task_family: str,
    time_budget_mins: float,
    output_path: Path,
    seed: int = 42,
) -> None:
    """Launch process pool executing parallel worker loops."""
    time_budget_secs = time_budget_mins * 60.0
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 80, flush=True)
    print(f"CLUSTER WORKER POOL STARTED: Node '{node_name}' ({num_workers} Workers)", flush=True)
    print(f"Task Family: {task_family} | Budget: {time_budget_mins:.1f} mins ({time_budget_secs:.0f}s)", flush=True)
    print(f"Output File: {output_path}", flush=True)
    print("=" * 80, flush=True)

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(
                run_worker_loop,
                w_id,
                node_name,
                task_family,
                time_budget_secs,
                output_path,
                seed,
            )
            for w_id in range(num_workers)
        ]
        concurrent.futures.wait(futures)

    print(f"[*] Cluster Worker Pool '{node_name}' finished.", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-Node Cluster Worker Pool")
    parser.add_argument("--node-name", default="local_darwin", type=str, help="Node name identifier")
    parser.add_argument("--num-workers", default=4, type=int, help="Number of parallel worker processes")
    parser.add_argument("--task-family", default="full_pool", choices=["hydrographical_focus", "admiralty_siblings", "full_pool"], help="Task family")
    parser.add_argument("--time-budget-mins", default=60.0, type=float, help="Time budget in minutes")
    parser.add_argument("--output-file", default="./data/derived/cluster_trials.jsonl", type=Path, help="Output JSONL path")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_cluster_worker_pool(
        node_name=args.node_name,
        num_workers=args.num_workers,
        task_family=args.task_family,
        time_budget_mins=args.time_budget_mins,
        output_path=args.output_file,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
