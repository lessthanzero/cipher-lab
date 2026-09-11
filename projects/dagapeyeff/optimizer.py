"""Evolutionary permutation optimizer & systematic hypothesis sweep for D'Agapeyeff."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

from cipher_lab.loop import CipherDiscoveryLoop
from cipher_lab.stats import QuadgramScorer

from projects.dagapeyeff.corpus import get_clean_digits
from projects.dagapeyeff.hypotheses import (
    apply_columnar_transposition,
    apply_error_slip,
    decode_polybius_fractionation,
)


class DagapeyeffOptimizer:
    """Evolutionary and systematic search over fractionated transposition keyspaces."""

    def __init__(self, data_dir: Path, seed: int = 42) -> None:
        self.digits = get_clean_digits()
        self.loop = CipherDiscoveryLoop(
            artifact_id="dagapeyeff_1939",
            ciphertext=self.digits,
            alphabet_size=25,
            key_space_bits=84.0,
            historical_context="1939 British cryptographer challenge; likely fractionated Polybius with transposition.",
            data_dir=data_dir,
        )
        self.rng = random.Random(seed)
        self.scorer = QuadgramScorer()

    def run_transposition_sweep(self, max_iterations: int = 50) -> None:
        """Sweep candidate columnar widths and random permutations."""
        print(f"[*] Starting D'Agapeyeff Transposition Sweep ({max_iterations} iterations)...")
        best_score = -999.0
        best_trial = None

        widths = [7, 14]  # Factors of 196 (14x14 grid) and common military transposition widths

        for w in widths:
            base_perm = list(range(w))
            for i in range(max_iterations // len(widths)):
                perm = base_perm[:]
                self.rng.shuffle(perm)
                transposed_digits = apply_columnar_transposition(self.digits, perm)
                pt = decode_polybius_fractionation(transposed_digits)
                
                hyp_name = f"H_col_w{w}_iter_{i}"
                eval_res = self.loop.evaluate_candidate(
                    hypothesis_name=hyp_name,
                    key_class="columnar_transposition",
                    key_desc=f"Width {w}, perm={perm[:6]}...",
                    candidate_pt=pt,
                )

                if eval_res.quadgram_score > best_score:
                    best_score = eval_res.quadgram_score
                    best_trial = eval_res

        print(f"[+] Transposition sweep complete. Best quadgram score: {best_score:.2f}")
        if best_trial:
            print(f"[+] Best hypothesis: {best_trial.hypothesis_name} (viable={best_trial.is_statistically_viable})")

    def run_clerical_slip_sweep(self) -> None:
        """Systematically test single-digit deletion across all 14 row boundaries."""
        print("[*] Starting Clerical Slip Boundary Sweep (rows 1 to 14)...")
        for row_idx in range(14):
            boundary_idx = (row_idx + 1) * 14 - 1
            for error_type in ["delete", "swap"]:
                modified_digits = apply_error_slip(self.digits, slip_index=boundary_idx, error_type=error_type)
                pt = decode_polybius_fractionation(modified_digits)
                hyp_name = f"H_slip_row{row_idx+1}_{error_type}"
                self.loop.evaluate_candidate(
                    hypothesis_name=hyp_name,
                    key_class="error_slip",
                    key_desc=f"Clerical {error_type} at row {row_idx+1} boundary (idx {boundary_idx})",
                    candidate_pt=pt,
                )

        summary = self.loop.ledger.get_summary_statistics("dagapeyeff_1939")
        print(f"[+] Clerical slip sweep complete. Total trials in denominator: {summary['total_trials_denominator']}")
        print(f"[+] Multiplicity Bonferroni critical threshold: {summary['bonferroni_critical_p']:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="./data/derived", type=Path)
    parser.add_argument("--iterations", default=30, type=int)
    args = parser.parse_args()

    opt = DagapeyeffOptimizer(data_dir=args.data_dir)
    opt.run_transposition_sweep(max_iterations=args.iterations)
    opt.run_clerical_slip_sweep()


if __name__ == "__main__":
    main()
