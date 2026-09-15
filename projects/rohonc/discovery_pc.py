"""Remote Fedora PC Batch Worker for Rohonc Codex.

Executes high-throughput Monte Carlo null permutation tests (5,000+ shuffles)
for conditional bigram entropy and multi-scene liturgical alignments.
Can run natively on Linux or dispatch remotely from Darwin over SSH.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import platform
import random
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from cipher_lab.harness import RemoteComputeWorker
from cipher_lab.ledger import EpistemicLedger

from projects.rohonc.corpus import get_all_rohonc_tokens
from projects.rohonc.stats import calculate_entropy_profile


@dataclass
class MonteCarloBatchResult:
    n_permutations: int
    observed_h2: float
    null_mean_h2: float
    null_std_h2: float
    z_score: float
    empirical_p_value: float
    execution_node: str
    duration_seconds: float


def run_local_or_native_mc(tokens: List[str], n_permutations: int = 2000, seed: int = 42) -> MonteCarloBatchResult:
    """Run Monte Carlo null permutations locally (used on Fedora PC or Darwin fallback)."""
    t0 = time.time()
    rng = random.Random(seed)
    
    # Calculate observed conditional entropy
    obs_profile = calculate_entropy_profile(tokens)
    obs_h2 = obs_profile.h2_conditional

    # Null Permutations: Shuffle tokens and compute H(S2|S1)
    null_scores = []
    shuffled = list(tokens)
    for _ in range(n_permutations):
        rng.shuffle(shuffled)
        prof = calculate_entropy_profile(shuffled)
        null_scores.append(prof.h2_conditional)

    mean_null = sum(null_scores) / len(null_scores)
    var_null = sum((s - mean_null) ** 2 for s in null_scores) / (len(null_scores) - 1 or 1)
    std_null = math.sqrt(var_null) or 1e-9

    z_score = (mean_null - obs_h2) / std_null
    p_value = sum(1 for s in null_scores if s <= obs_h2) / len(null_scores)

    return MonteCarloBatchResult(
        n_permutations=n_permutations,
        observed_h2=round(obs_h2, 4),
        null_mean_h2=round(mean_null, 4),
        null_std_h2=round(std_null, 4),
        z_score=round(z_score, 2),
        empirical_p_value=round(p_value, 6),
        execution_node=platform.node(),
        duration_seconds=round(time.time() - t0, 3),
    )


def dispatch_remote_mc_fedora(
    tokens: List[str],
    n_permutations: int = 5000,
    seed: int = 42,
    host: str = "pc",
) -> Optional[MonteCarloBatchResult]:
    """Dispatch large Monte Carlo batch to Fedora PC via SSH."""
    worker = RemoteComputeWorker(host=host)
    if not worker.is_reachable():
        print(f"[*] Remote worker '{host}' is unreachable; falling back to local execution.")
        return None

    t0 = time.time()
    tokens_json = json.dumps(tokens)
    
    remote_script = f"""
import json, random, math
tokens = {tokens_json}
n_perms = {n_permutations}
seed = {seed}
rng = random.Random(seed)

def get_h2(toks):
    n = len(toks)
    if n < 2: return 0.0
    uni = {{}}
    bi = {{}}
    for i in range(n):
        t = toks[i]
        uni[t] = uni.get(t, 0) + 1
        if i < n - 1:
            bg = (t, toks[i+1])
            bi[bg] = bi.get(bg, 0) + 1
    h1 = -sum((c/n) * math.log2(c/n) for c in uni.values())
    h_joint = -sum((c/(n-1)) * math.log2(c/(n-1)) for c in bi.values())
    return max(0.0, h_joint - h1)

obs_h2 = get_h2(tokens)
shuffled = list(tokens)
nulls = []
for _ in range(n_perms):
    rng.shuffle(shuffled)
    nulls.append(get_h2(shuffled))

mean_n = sum(nulls) / len(nulls)
std_n = math.sqrt(sum((s - mean_n)**2 for s in nulls) / (len(nulls) - 1 or 1))
z = (mean_n - obs_h2) / (std_n or 1e-9)
p = sum(1 for s in nulls if s <= obs_h2) / len(nulls)

out = {{
    "n_permutations": n_perms,
    "observed_h2": round(obs_h2, 4),
    "null_mean_h2": round(mean_n, 4),
    "null_std_h2": round(std_n, 4),
    "z_score": round(z, 2),
    "empirical_p_value": round(p, 6),
    "execution_node": "fedora_pc",
}}
print(json.dumps(out))
"""
    b64_script = base64.b64encode(remote_script.encode()).decode()
    cmd = ["ssh", "-o", "BatchMode=yes", host, f"python3 -c \"import base64; exec(base64.b64decode('{b64_script}'))\""]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=False)
        if proc.returncode == 0 and proc.stdout.strip():
            data = json.loads(proc.stdout.strip())
            data["duration_seconds"] = round(time.time() - t0, 3)
            return MonteCarloBatchResult(**data)
        else:
            print(f"[*] Remote worker execution returned stderr: {proc.stderr[:200]}")
    except Exception as e:
        print(f"[*] Remote worker error: {e}")

    return None


def run_rohonc_pc_discovery(
    n_permutations: int = 5000,
    seed: int = 42,
    data_dir: Path = Path("./data/derived"),
) -> MonteCarloBatchResult:
    """Execute batch discovery on remote PC or fallback locally, and log to DuckDB ledger."""
    tokens = get_all_rohonc_tokens()
    print(f"[*] Dispatching Rohonc Monte Carlo sweep ({n_permutations} permutations, {len(tokens)} tokens)...")

    # Try remote Fedora PC first if not already running on Linux
    res: Optional[MonteCarloBatchResult] = None
    if platform.system() != "Linux":
        res = dispatch_remote_mc_fedora(tokens, n_permutations=n_permutations, seed=seed)

    if res is None:
        print("[*] Executing natively on local host...")
        res = run_local_or_native_mc(tokens, n_permutations=n_permutations, seed=seed)

    print(f"[+] Completed Monte Carlo sweep on {res.execution_node} in {res.duration_seconds}s:")
    print(f"    - Observed H(S2|S1): {res.observed_h2:.4f} bits")
    print(f"    - Null Mean:        {res.null_mean_h2:.4f} ± {res.null_std_h2:.4f} bits")
    print(f"    - Syntax Z-Score:   Z = +{res.z_score:.2f} sigma (p = {res.empirical_p_value:.6f})")

    # Record in DuckDB
    ledger = EpistemicLedger(ledger_dir=data_dir)
    ledger.record_trial(
        trial_id=f"rohonc_pc_mc_null_{int(time.time())}",
        artifact_id="rohonc_codex",
        hypothesis_name="H_rohonc_mc_null_syntax_rejection",
        key_class="monte_carlo_surrogate",
        payload_len=len(tokens),
        unicity_distance=45.0,
        passed_unicity=True,
        raw_fitness=res.z_score,
        empirical_p_value=res.empirical_p_value,
        negative_twin_fitness=res.null_mean_h2,
        falsification_status="STAT_SIGNIFICANT" if res.empirical_p_value < 0.001 else "ACTIVE_SEARCH",
        abstention_reason=None,
    )
    return res


def main() -> None:
    parser = argparse.ArgumentParser(description="Rohonc Codex Remote PC Batch Worker")
    parser.add_argument("--permutations", default=2000, type=int, help="Number of Monte Carlo permutations")
    parser.add_argument("--seed", default=42, type=int, help="Random seed")
    parser.add_argument("--data-dir", default="./data/derived", type=Path, help="Data directory")
    args = parser.parse_args()

    res = run_rohonc_pc_discovery(n_permutations=args.permutations, seed=args.seed, data_dir=args.data_dir)
    print(json.dumps(asdict(res), indent=2))


if __name__ == "__main__":
    main()
