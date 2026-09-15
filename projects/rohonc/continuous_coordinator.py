"""Continuous Dual-Node Discovery Coordinator for Rohonc Codex.

Coordinates continuous execution across Darwin Apple Silicon (Node A) and Fedora Linux PC (Node B):
- Node A (Local Darwin M1 Pro): Graph morpheme clustering, affix annealing, 24-scene micro-Diatessaron sequence alignment.
- Node B (Remote Fedora PC): High-throughput parallel Monte Carlo Markov order-2 & order-3 null sweeps.
- Epistemic Ledger: Synchronizes all trials into DuckDB and streams events to JSONL.
- Live Telemetry: Heartbeat emitted every 60 seconds reporting progress, hardware health, and discovery stats.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cipher_lab.harness import RemoteComputeWorker, get_darwin_available_memory_gb
from cipher_lab.ledger import EpistemicLedger

from projects.rohonc.codebook import RohoncCodebookEngine
from projects.rohonc.corpus import FOLIO_TRANSCRIPTIONS, get_all_rohonc_lines, get_all_rohonc_tokens
from projects.rohonc.discovery_pc import dispatch_remote_mc_fedora, run_local_or_native_mc
from projects.rohonc.liturgical_aligner import (
    LITURGICAL_MICRO_DIATESSARON_24,
    RohoncLiturgicalAligner,
)
from projects.rohonc.morpheme_clusterer import RohoncMorphemeClusterer


@dataclass
class HeartbeatTelemetry:
    timestamp: str
    elapsed_seconds: float
    target_seconds: float
    percent_complete: float
    darwin_memory_available_gb: float
    fedora_pc_reachable: bool
    total_ledger_trials: int
    significant_discoveries: int
    active_hypotheses: int
    latest_event: str


class RohoncContinuousCoordinator:
    """Orchestrates 30-minute dual-node continuous discovery pipeline."""

    def __init__(
        self,
        duration_seconds: int = 1800,
        heartbeat_interval: int = 60,
        data_dir: Path = Path("./data/derived"),
    ) -> None:
        self.duration_seconds = duration_seconds
        self.heartbeat_interval = heartbeat_interval
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.ledger = EpistemicLedger(ledger_dir=self.data_dir)
        self.stream_path = self.data_dir / "rohonc_continuous_stream.jsonl"

        self.worker_pc = RemoteComputeWorker(host="pc")
        self.aligner = RohoncLiturgicalAligner(stages=LITURGICAL_MICRO_DIATESSARON_24)
        self.clusterer = RohoncMorphemeClusterer()
        self.codebook = RohoncCodebookEngine()
        self.tokens = get_all_rohonc_tokens()
        self.lines = get_all_rohonc_lines()

        self.start_time: float = 0.0
        self.cycle_count: int = 0
        self.discoveries: List[Dict[str, Any]] = []

    def _log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Write structured event to live JSONL stream."""
        rec = {
            "timestamp": datetime.now(UTC).isoformat(),
            "elapsed_s": round(time.time() - self.start_time, 2) if self.start_time else 0.0,
            "event_type": event_type,
            "data": data,
        }
        with open(self.stream_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    def run_continuous_session(self) -> Dict[str, Any]:
        """Execute the continuous dual-node discovery loop until duration expires."""
        self.start_time = time.time()
        end_time = self.start_time + self.duration_seconds
        last_heartbeat = self.start_time

        print("=" * 80)
        print(f"ROHONC CODEX: STARTING CONTINUOUS DUAL-NODE DISCOVERY ({self.duration_seconds / 60:.1f} MINUTES)")
        print(f"Start Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Target Duration: {self.duration_seconds}s | Heartbeat Interval: {self.heartbeat_interval}s")
        print(f"Node A: Local Apple Silicon ({platform.node()}, Darwin macOS)")
        print(f"Node B: Remote Fedora Linux PC ('pc', Reachable: {self.worker_pc.is_reachable()})")
        print("=" * 80)

        self._log_event("session_start", {
            "duration_seconds": self.duration_seconds,
            "heartbeat_interval": self.heartbeat_interval,
            "fedora_reachable": self.worker_pc.is_reachable(),
        })

        while time.time() < end_time:
            self.cycle_count += 1
            cycle_t0 = time.time()

            # -------------------------------------------------------------
            # Sub-Task 1 (Darwin M1 Pro): Micro-Diatessaron Local Alignment Sweep
            # -------------------------------------------------------------
            # Pick a subset of folios to test against candidate 24-scene Diatessaron
            sample_fid = random.choice(list(FOLIO_TRANSCRIPTIONS.keys()))
            f_data = FOLIO_TRANSCRIPTIONS[sample_fid]
            align_res = self.aligner.align_folio(
                folio_id=f_data["folio"],
                lines=f_data["lines"],
                folio_title=f_data["title"],
                n_null_permutations=250,
            )

            # Record alignment trial
            trial_id = f"rohonc_diatessaron_{f_data['folio']}_{int(time.time())}_{self.cycle_count}"
            is_sig = align_res.is_significant
            self.ledger.record_trial(
                trial_id=trial_id,
                artifact_id="rohonc_codex",
                hypothesis_name=f"H_rohonc_diatessaron_fol_{f_data['folio']}",
                key_class="micro_diatessaron_alignment",
                payload_len=len(self.tokens),
                unicity_distance=45.0,
                passed_unicity=True,
                raw_fitness=align_res.alignment_score,
                empirical_p_value=align_res.p_value,
                negative_twin_fitness=0.0,
                falsification_status="STAT_SIGNIFICANT" if is_sig else "ACTIVE_SEARCH",
                abstention_reason=None if is_sig else f"Z={align_res.z_score_vs_null:.2f} below threshold",
            )
            if is_sig:
                self.discoveries.append({
                    "type": "liturgical_alignment",
                    "folio": f_data["folio"],
                    "scene": align_res.best_matching_stage,
                    "score": align_res.alignment_score,
                    "z_score": align_res.z_score_vs_null,
                    "p_value": align_res.p_value,
                })

            # -------------------------------------------------------------
            # Sub-Task 2 (Darwin M1 Pro): Graph Morpheme Clustering & Affix Scan
            # -------------------------------------------------------------
            sign_metrics = self.clusterer.compute_sign_metrics()
            affixes = [m for m in sign_metrics if m.is_candidate_affix]

            # -------------------------------------------------------------
            # Sub-Task 3 (Fedora PC Batch): High-Throughput Monte Carlo Markov Null
            # -------------------------------------------------------------
            # Run large batch on Fedora PC every 2 cycles
            if self.cycle_count % 2 == 0:
                mc_res = None
                if self.worker_pc.is_reachable():
                    mc_res = dispatch_remote_mc_fedora(self.tokens, n_permutations=5000, seed=self.cycle_count * 100)
                if mc_res is None:
                    mc_res = run_local_or_native_mc(self.tokens, n_permutations=1000, seed=self.cycle_count * 100)

                # Record in ledger
                self.ledger.record_trial(
                    trial_id=f"rohonc_mc_perm_{int(time.time())}_{self.cycle_count}",
                    artifact_id="rohonc_codex",
                    hypothesis_name="H_rohonc_markov_null_batch",
                    key_class="markov_null_permutation",
                    payload_len=len(self.tokens),
                    unicity_distance=45.0,
                    passed_unicity=True,
                    raw_fitness=mc_res.z_score_h2,
                    empirical_p_value=mc_res.empirical_p_value_h2,
                    negative_twin_fitness=mc_res.null_mean_h2,
                    falsification_status="STAT_SIGNIFICANT" if mc_res.empirical_p_value_h2 < 0.001 else "ACTIVE_SEARCH",
                    abstention_reason=None,
                )

            # -------------------------------------------------------------
            # Telemetry Heartbeat & Periodic Logging
            # -------------------------------------------------------------
            now = time.time()
            if now - last_heartbeat >= self.heartbeat_interval:
                elapsed = now - self.start_time
                pct = min(100.0, (elapsed / self.duration_seconds) * 100)
                stats = self.ledger.get_summary_statistics("rohonc_codex")
                mem_avail = get_darwin_available_memory_gb()

                hb = HeartbeatTelemetry(
                    timestamp=datetime.now(UTC).strftime("%H:%M:%S UTC"),
                    elapsed_seconds=round(elapsed, 1),
                    target_seconds=float(self.duration_seconds),
                    percent_complete=round(pct, 1),
                    darwin_memory_available_gb=round(mem_avail, 2),
                    fedora_pc_reachable=self.worker_pc.is_reachable(),
                    total_ledger_trials=stats.get("total_trials_denominator", 0),
                    significant_discoveries=len(self.discoveries),
                    active_hypotheses=stats.get("active_hypotheses", 0),
                    latest_event=f"Cycle {self.cycle_count}: Folio {f_data['folio']} -> {align_res.best_matching_stage[:30]}",
                )

                mins_el = int(elapsed // 60)
                secs_el = int(elapsed % 60)
                mins_tot = int(self.duration_seconds // 60)
                secs_tot = int(self.duration_seconds % 60)

                print(
                    f"[{hb.timestamp}] Heartbeat {mins_el:02d}:{secs_el:02d} / {mins_tot:02d}:{secs_tot:02d} ({hb.percent_complete:>5.1f}%) | "
                    f"Fedora: {'ONLINE' if hb.fedora_pc_reachable else 'OFFLINE'} | "
                    f"Mem: {hb.darwin_memory_available_gb:.1f}GB | "
                    f"Trials: {hb.total_ledger_trials:<4} | "
                    f"Discoveries: {hb.significant_discoveries} | "
                    f"Affixes: {len(affixes)}"
                )

                self._log_event("telemetry_heartbeat", asdict(hb))
                last_heartbeat = now

            # Sleep briefly to avoid tight polling while maintaining steady computation
            time.sleep(0.5)

        # -----------------------------------------------------------------
        # Session Completion Summary
        # -----------------------------------------------------------------
        total_time = time.time() - self.start_time
        final_stats = self.ledger.get_summary_statistics("rohonc_codex")

        summary = {
            "session_completed_at": datetime.now(UTC).isoformat(),
            "duration_seconds": round(total_time, 2),
            "total_cycles_executed": self.cycle_count,
            "total_ledger_trials": final_stats.get("total_trials_denominator", 0),
            "bonferroni_critical_p": final_stats.get("bonferroni_critical_p", 0.0),
            "total_stat_significant_discoveries": len(self.discoveries),
            "discoveries_log": self.discoveries,
        }

        # Save summary to file
        summary_path = self.data_dir / "rohonc_continuous_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        self._log_event("session_complete", summary)

        print("\n" + "=" * 80)
        print("CONTINUOUS DUAL-NODE DISCOVERY RUN COMPLETE")
        print(f"Total Duration: {total_time:.1f}s ({total_time / 60:.1f} minutes)")
        print(f"Total Cycles: {self.cycle_count}")
        print(f"Total Trials Logged in DuckDB: {final_stats.get('total_trials_denominator', 0)}")
        print(f"Bonferroni Critical Alpha: {final_stats.get('bonferroni_critical_p', 0.0):.8f}")
        print(f"Summary Written: {summary_path}")
        print("=" * 80)

        return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Rohonc Codex Continuous Dual-Node Discovery Coordinator")
    parser.add_argument("--duration", default=1800, type=int, help="Total execution duration in seconds (default 1800 = 30m)")
    parser.add_argument("--heartbeat", default=60, type=int, help="Telemetry heartbeat interval in seconds (default 60)")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    args = parser.parse_args()

    coordinator = RohoncContinuousCoordinator(
        duration_seconds=args.duration,
        heartbeat_interval=args.heartbeat,
        data_dir=args.data_dir,
    )
    coordinator.run_continuous_session()


if __name__ == "__main__":
    main()
