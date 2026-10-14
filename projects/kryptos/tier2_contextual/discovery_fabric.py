"""Compute Fabric Integration for Kryptos K4.

Orchestrates distributed execution across:
1. Fedora PC (pc: 192.168.1.172) via remote_worker.sh for heavy Python batch sweeps.
2. Kate's MacBook Air (macbook-mobile) via local-harness coordinator queue for text_stats and model scoring.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


LOCAL_HARNESS_CLI = Path.home() / "Developer" / "local-models" / ".venv" / "bin" / "local-harness"
REMOTE_WORKER_SH = Path(__file__).parent.parent.parent.parent / "scripts" / "remote_worker.sh"


def submit_job_to_kate_macbook_air(input_file: Path, priority: str = "opportunistic") -> Dict[str, Any]:
    """Submit a text_stats job to Kate's MacBook Air via local-harness."""
    if not LOCAL_HARNESS_CLI.exists():
        return {"status": "error", "error": f"local-harness CLI not found at {LOCAL_HARNESS_CLI}"}

    cmd = [
        str(LOCAL_HARNESS_CLI),
        "submit",
        "--type", "text_stats",
        "--input-file", str(input_file),
        "--priority", priority,
        "--allow-node", "macbook-mobile",
        "--share-with-mobile",
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "submitted", "output": proc.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr.strip()}


def execute_fedora_pc_batch_run(budget_mins: float = 1.0) -> Dict[str, Any]:
    """Execute discovery_pc.py on Fedora PC worker via remote_worker.sh."""
    if not REMOTE_WORKER_SH.exists():
        return {"status": "error", "error": f"remote_worker.sh not found at {REMOTE_WORKER_SH}"}

    command_to_run = f"uv run python -m projects.kryptos.tier2_contextual.discovery_pc --budget {budget_mins}"
    cmd = [str(REMOTE_WORKER_SH), "pc", command_to_run]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "success", "stdout": proc.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": e.stderr.strip()}


if __name__ == "__main__":
    print("Testing compute fabric coordination...")
    test_file = Path(__file__).parent.parent / "datasets" / "blind" / "k4_ciphertext.json"
    res = submit_job_to_kate_macbook_air(test_file)
    print("Kate MacBook Air Submission:", res)
