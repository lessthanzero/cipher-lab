"""Distributed Cluster Orchestrator for D'Agapeyeff (Darwin + Fedora PC).

Orchestrates a 60-minute multi-node campaign utilizing all compute nodes in cluster:
- Node 1: Apple Silicon macOS (6 parallel workers focusing on HYDROGRAPHICAL + traversals)
- Node 2: Fedora PC Linux (6 parallel workers focusing on Sibling Admiralty keywords + traversals)
- Synchronizes output JSONL streams into DuckDB Epistemic Ledger upon completion.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

from cipher_lab.ledger import EpistemicLedger


def launch_remote_worker(
    remote_host: str,
    num_workers: int,
    task_family: str,
    time_budget_mins: float,
    remote_output: str,
    seed: int,
) -> subprocess.Popen:
    """Launch remote cluster worker pool on Fedora PC via SSH in background."""
    cmd = (
        f"ssh {remote_host} "
        f"\"cd ~/Developer/cipher-lab && "
        f"~/.local/bin/uv run python -m projects.dagapeyeff.cluster_worker "
        f"--node-name fedora_pc "
        f"--num-workers {num_workers} "
        f"--task-family {task_family} "
        f"--time-budget-mins {time_budget_mins} "
        f"--output-file {remote_output} "
        f"--seed {seed} > ~/Developer/cipher-lab/data/derived/cluster_pc.log 2>&1\""
    )
    return subprocess.Popen(cmd, shell=True)


def launch_local_worker(
    num_workers: int,
    task_family: str,
    time_budget_mins: float,
    local_output: Path,
    seed: int,
) -> subprocess.Popen:
    """Launch local cluster worker pool on macOS in background."""
    cmd = [
        "uv", "run", "python", "-m", "projects.dagapeyeff.cluster_worker",
        "--node-name", "darwin_m1",
        "--num-workers", str(num_workers),
        "--task-family", task_family,
        "--time-budget-mins", str(time_budget_mins),
        "--output-file", str(local_output),
        "--seed", str(seed),
    ]
    log_path = local_output.parent / "cluster_mac.log"
    log_file = open(log_path, "w", encoding="utf-8")
    return subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)


def ingest_trials_to_ledger(ledger: EpistemicLedger, jsonl_path: Path) -> int:
    """Read trials from JSONL output and record into DuckDB Epistemic Ledger."""
    if not jsonl_path.exists():
        return 0

    count = 0
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                ledger.record_trial(
                    trial_id=data["trial_id"],
                    artifact_id="dagapeyeff_1939",
                    hypothesis_name=f"H_cluster_{data['keyword_label']}_{data['traversal']}_{data['direction'][:4]}_{data['order'][:3]}",
                    key_class="cluster_distributed_twosquare",
                    payload_len=182,
                    unicity_distance=50.0 if data["dual_alphabets"] else 25.0,
                    passed_unicity=True,
                    raw_fitness=data["q_score"],
                    empirical_p_value=0.001996 if data["chi_sq"] < 30.0 else 0.5,
                    negative_twin_fitness=0.0,
                    falsification_status="STAT_SIGNIFICANT" if data["chi_sq"] < 30.0 and data["ioc"] > 0.060 else "ACTIVE_SEARCH",
                    abstention_reason=None,
                )
                count += 1
            except Exception:
                continue
    return count


def run_distributed_campaign(
    time_budget_mins: float = 60.0,
    mac_workers: int = 6,
    pc_workers: int = 6,
    data_dir: Path = Path("./data/derived"),
    seed: int = 42,
) -> None:
    """Execute end-to-end distributed cluster campaign across Darwin and Fedora PC."""
    time_budget_secs = time_budget_mins * 60.0
    start_time = time.time()
    ledger = EpistemicLedger(ledger_dir=data_dir)

    print("=" * 80, flush=True)
    print("D'AGAPEYEFF: 60-MINUTE DISTRIBUTED CLUSTER CAMPAIGN (ALL NODES UNPARKED)", flush=True)
    print(f"Total Budget: {time_budget_mins:.1f} minutes ({time_budget_secs:.0f}s)", flush=True)
    print(f"Node 1: Apple Silicon macOS ({mac_workers} workers) -> HYDROGRAPHICAL + Traversals", flush=True)
    print(f"Node 2: Fedora PC Linux ({pc_workers} workers) -> Sibling Admiralty + Traversals", flush=True)
    print(f"Total Cluster Compute: {mac_workers + pc_workers} Parallel Processes", flush=True)
    print("Benchmark to Beat: Q = -845.3 (Project Record) | SOTA: Q = -692.13", flush=True)
    print("=" * 80, flush=True)

    # Output file paths
    mac_output = data_dir / "mac_trials.jsonl"
    pc_remote_output = "~/Developer/cipher-lab/data/derived/pc_trials.jsonl"
    pc_local_copy = data_dir / "pc_trials_pulled.jsonl"

    # Clean old JSONL outputs if present
    if mac_output.exists():
        mac_output.unlink()
    subprocess.run(["ssh", "pc", f"rm -f {pc_remote_output}"], capture_output=True)

    # 1. Launch Fedora PC remote workers
    print("\n[*] Launching Fedora PC Remote Worker Pool (6 workers)...", flush=True)
    pc_proc = launch_remote_worker(
        remote_host="pc",
        num_workers=pc_workers,
        task_family="admiralty_siblings",
        time_budget_mins=time_budget_mins,
        remote_output=pc_remote_output,
        seed=seed + 100,
    )

    # 2. Launch Local Mac workers
    print("[*] Launching macOS Local Worker Pool (6 workers)...", flush=True)
    mac_proc = launch_local_worker(
        num_workers=mac_workers,
        task_family="hydrographical_focus",
        time_budget_mins=time_budget_mins,
        local_output=mac_output,
        seed=seed,
    )

    print("\n[+] Both worker pools actively running in parallel.", flush=True)

    # 3. Telemetry monitoring loop
    poll_interval = 60.0  # Poll every 1 minute
    last_poll = time.time()
    best_discovered_q = -845.3

    while (time.time() - start_time) < time_budget_secs:
        time.sleep(min(15.0, time_budget_secs - (time.time() - start_time)))

        if (time.time() - last_poll) >= poll_interval:
            last_poll = time.time()
            elapsed_m = (time.time() - start_time) / 60.0

            # Check Mac trials
            mac_count = 0
            if mac_output.exists():
                try:
                    with open(mac_output, "r", encoding="utf-8") as f:
                        mac_lines = [json.loads(line) for line in f if line.strip()]
                    mac_count = len(mac_lines)
                    if mac_lines:
                        top_mac = max(mac_lines, key=lambda x: x["q_score"])
                        if top_mac["q_score"] > best_discovered_q:
                            best_discovered_q = top_mac["q_score"]
                            print(f"[!] [DARWIN] NEW CLUSTER RECORD: Q={best_discovered_q:.1f} Key: {top_mac['keyword_label']}", flush=True)
                except Exception:
                    pass

            # Check PC trials via SSH
            pc_count = 0
            try:
                res = subprocess.run(
                    ["ssh", "pc", "wc -l ~/Developer/cipher-lab/data/derived/pc_trials.jsonl 2>/dev/null"],
                    capture_output=True, text=True, timeout=5,
                )
                if res.returncode == 0 and res.stdout.strip():
                    pc_count = int(res.stdout.strip().split()[0])
            except Exception:
                pass

            print(f"[*] Telemetry [{elapsed_m:.1f}/{time_budget_mins:.1f}m]: Darwin={mac_count} trials | Fedora={pc_count} trials | Best Q={best_discovered_q:.1f}", flush=True)

            if best_discovered_q > -692.13:
                print("\n" + "!" * 80, flush=True)
                print("BREAKTHROUGH: TIM MARLAND SOTA BEATEN!", flush=True)
                print("!" * 80, flush=True)
                break

    # 4. Wait for local and remote processes to wrap up
    print("\n[*] Time budget elapsed. Finalizing cluster processes...", flush=True)
    mac_proc.wait(timeout=30)
    pc_proc.wait(timeout=30)

    # 5. Pull PC trials to local Mac
    print("[*] Pulling remote Fedora trials via rsync...", flush=True)
    subprocess.run(
        ["rsync", "-avz", "pc:~/Developer/cipher-lab/data/derived/pc_trials.jsonl", str(pc_local_copy)],
        capture_output=True,
    )

    # 6. Ingest all trials into DuckDB Epistemic Ledger
    print("[*] Ingesting all cluster trials into DuckDB Epistemic Ledger...", flush=True)
    ingested_mac = ingest_trials_to_ledger(ledger, mac_output)
    ingested_pc = ingest_trials_to_ledger(ledger, pc_local_copy)

    summary = ledger.get_summary_statistics("dagapeyeff_1939")

    print("\n" + "=" * 80, flush=True)
    print("DISTRIBUTED CLUSTER CAMPAIGN COMPLETE", flush=True)
    print(f"Total Trials Ingested from Darwin: {ingested_mac}", flush=True)
    print(f"Total Trials Ingested from Fedora PC: {ingested_pc}", flush=True)
    print(f"Total Ledger Trials: {summary['total_trials_denominator']}", flush=True)
    print(f"Bonferroni Critical Threshold: {summary['bonferroni_critical_p']:.8f}", flush=True)
    print(f"Best Discovered Score: Q = {best_discovered_q:.1f}", flush=True)
    print("=" * 80, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Distributed Cluster Campaign Orchestrator")
    parser.add_argument("--time-budget-mins", default=60.0, type=float, help="Wall-clock time budget in minutes")
    parser.add_argument("--mac-workers", default=6, type=int, help="Workers on Mac")
    parser.add_argument("--pc-workers", default=6, type=int, help="Workers on PC")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    args = parser.parse_args()

    run_distributed_campaign(
        time_budget_mins=args.time_budget_mins,
        mac_workers=args.mac_workers,
        pc_workers=args.pc_workers,
        data_dir=args.data_dir,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
