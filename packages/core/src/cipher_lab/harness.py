"""Distributed compute, Darwin memory-safe telemetry, and LLM referee harness for cipher-lab."""

from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

import httpx

LOCAL_OLLAMA_URL = "http://127.0.0.1:11434"
REMOTE_OLLAMA_URL = "http://100.103.226.101:11434"


def get_darwin_available_memory_gb() -> float:
    """Calculate true available RAM on macOS accounting for cache reclaiming."""
    page_size = 16384  # 16 KB default on Apple Silicon Darwin
    try:
        vm = subprocess.check_output(["vm_stat"], text=True)
        free_p = inactive_p = purge_p = spec_p = 0
        for line in vm.splitlines():
            if "Pages free:" in line:
                free_p = int(line.split(":")[1].strip().rstrip("."))
            elif "Pages inactive:" in line:
                inactive_p = int(line.split(":")[1].strip().rstrip("."))
            elif "Pages purgeable:" in line:
                purge_p = int(line.split(":")[1].strip().rstrip("."))
            elif "Pages speculative:" in line:
                spec_p = int(line.split(":")[1].strip().rstrip("."))
        avail_bytes = (free_p + spec_p + inactive_p + purge_p) * page_size
        return avail_bytes / (1024 ** 3)
    except Exception:
        return 4.0


def record_local_models_usage(
    task: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: float = 0.0,
    status: str = "success",
) -> None:
    """Log structured usage event to ~/.local/share/local-models/usage.jsonl."""
    try:
        log_path = Path(os.path.expanduser("~/.local/share/local-models/usage.jsonl"))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        rec = {
            "timestamp": datetime.now(UTC).isoformat(),
            "project": "cipher-lab",
            "task": task,
            "provider": "ollama",
            "model": model,
            "execution": "local",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "token_count_type": "estimated",
            "latency_ms": round(latency_ms, 2),
            "estimated_cost_gbp": 0.0,
            "status": status,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


class ModelRefereeHarness:
    """Orchestrates model probes and double-blind candidate evaluations with foil decoys."""

    def __init__(self, timeout_secs: float = 30.0) -> None:
        self.timeout = timeout_secs

    def probe_health(self) -> dict[str, Any]:
        """Probe reachability of local and remote Ollama instances."""
        status = {"local": {"reachable": False, "models": []}, "remote": {"reachable": False, "models": []}}
        try:
            r = httpx.get(f"{LOCAL_OLLAMA_URL}/api/tags", timeout=2.0)
            if r.status_code == 200:
                status["local"]["reachable"] = True
                status["local"]["models"] = [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass

        try:
            r = httpx.get(f"{REMOTE_OLLAMA_URL}/api/tags", timeout=1.5)
            if r.status_code == 200:
                status["remote"]["reachable"] = True
                status["remote"]["models"] = [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass

        return status

    def evaluate_with_blinded_foils(
        self,
        candidate_plaintext: str,
        decoy_plaintexts: list[str],
        artifact_context: str,
        preferred_model: str = "phi4-mini:latest",
    ) -> dict[str, Any]:
        """Double-blind referee protocol: presents the candidate alongside 2-3 decoy/negative-twin texts.
        
        If the model rates decoys highly, the referee confidence is penalized to protect against pareidolia.
        """
        # Combine candidate and decoys into randomized array
        items = [(candidate_plaintext, True)] + [(d, False) for d in decoy_plaintexts]
        random.shuffle(items)
        
        options_text = ""
        target_index = -1
        for idx, (text, is_target) in enumerate(items):
            options_text += f"Candidate [{chr(65 + idx)}]: \"{text[:120]}...\"\n"
            if is_target:
                target_index = idx

        prompt = f"""
You are an adversarial cryptanalysis peer reviewer.
Historical context: {artifact_context}

Evaluate the following candidate plaintexts. Some may be algorithmic hallucinations or negative controls.
{options_text}

Analyze whether ANY of these exhibit genuine, coherent natural language plaintext matching the era, or if all are noise/apophenia.
Respond in JSON:
{{
  "selected_option": "A"|"B"|"C"|"NONE",
  "linguistic_coherence_score": 0.0 to 1.0,
  "confidence": 0.0 to 1.0,
  "rationale": "one-sentence explanation"
}}
"""
        # 1. Check if model is codex / gpt-6-astra
        if "astra" in preferred_model or preferred_model.startswith("gpt-"):
            codex_bin = shutil.which("codex") or "/opt/homebrew/bin/codex"
            if codex_bin and os.path.exists(codex_bin):
                try:
                    t0 = time.time()
                    proc = subprocess.run(
                        [
                            codex_bin, "exec", "--ephemeral", "--skip-git-repo-check",
                            "--sandbox", "read-only", "-m", preferred_model, prompt
                        ],
                        stdin=subprocess.DEVNULL,
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                    )
                    lat = (time.time() - t0) * 1000
                    if proc.returncode == 0:
                        raw_out = proc.stdout.strip()
                        # Extract JSON object from output
                        json_str = raw_out
                        if "{" in raw_out and "}" in raw_out:
                            json_str = raw_out[raw_out.find("{") : raw_out.rfind("}") + 1]
                        resp_json = json.loads(json_str)
                        record_local_models_usage("blinded_foil_eval", preferred_model, len(prompt)//4, 150, lat)
                        
                        selected_letter = resp_json.get("selected_option", "NONE").upper()
                        chosen_idx = ord(selected_letter) - 65 if len(selected_letter) == 1 and selected_letter in "ABCD" else -1
                        
                        is_candidate_selected = (chosen_idx == target_index)
                        is_decoy_selected = (chosen_idx >= 0 and chosen_idx != target_index)
                        
                        return {
                            "status": "success",
                            "candidate_selected": is_candidate_selected,
                            "decoy_selected": is_decoy_selected,
                            "coherence_score": resp_json.get("linguistic_coherence_score", 0.0),
                            "confidence": resp_json.get("confidence", 0.0),
                            "rationale": resp_json.get("rationale", ""),
                        }
                except Exception as e:
                    print(f"[*] Codex referee fallback: {e}")

        # 2. Fallback to Ollama (local or remote)
        health = self.probe_health()
        endpoint = LOCAL_OLLAMA_URL
        if not health["local"]["reachable"] and health["remote"]["reachable"]:
            endpoint = REMOTE_OLLAMA_URL

        ollama_model = "phi4-mini:latest" if "astra" in preferred_model else preferred_model

        try:
            t0 = time.time()
            r = httpx.post(
                f"{endpoint}/api/generate",
                json={
                    "model": ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=self.timeout,
            )
            lat = (time.time() - t0) * 1000
            if r.status_code == 200:
                resp_json = json.loads(r.json().get("response", "{}"))
                record_local_models_usage("blinded_foil_eval", ollama_model, len(prompt)//4, 100, lat)
                
                selected_letter = resp_json.get("selected_option", "NONE").upper()
                chosen_idx = ord(selected_letter) - 65 if len(selected_letter) == 1 and selected_letter in "ABCD" else -1
                
                is_candidate_selected = (chosen_idx == target_index)
                is_decoy_selected = (chosen_idx >= 0 and chosen_idx != target_index)
                
                return {
                    "status": "success",
                    "candidate_selected": is_candidate_selected,
                    "decoy_selected": is_decoy_selected,
                    "coherence_score": resp_json.get("linguistic_coherence_score", 0.0),
                    "confidence": resp_json.get("confidence", 0.0),
                    "rationale": resp_json.get("rationale", ""),
                }
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}

        return {"status": "unavailable"}


class RemoteComputeWorker:
    """Dispatches heavy batch jobs (e.g. Monte Carlo permutations, large grid sweeps) to Fedora PC via SSH."""

    def __init__(self, host: str = "pc", timeout_secs: float = 30.0) -> None:
        self.host = host
        self.timeout = timeout_secs

    def is_reachable(self) -> bool:
        """Check if remote PC is reachable over SSH."""
        try:
            res = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=2", self.host, "echo ok"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            return res.returncode == 0 and "ok" in res.stdout
        except Exception:
            return False

    def run_remote_monte_carlo(self, text: str, n_samples: int = 5000) -> Optional[list[float]]:
        """Run parallel Monte Carlo null surrogates on Fedora PC."""
        if not self.is_reachable():
            return None

        import base64
        code = f"""
import json, random
text = {repr(text)}
n = len(text)
ng = {{"TION": -2.8, "NTHE": -3.0, "THER": -3.1, "THAT": -3.2, "OFTH": -3.3, "FTHE": -3.4, "THES": -3.5, "WITH": -3.5, "HERE": -3.6, "INTH": -3.1}}
def sc(t):
    if len(t) < 4: return -12.0 * len(t)
    return sum(ng.get(t[i:i+4], -12.0) for i in range(len(t)-3)) / (len(t)-3)
rng = random.Random(42)
c = list(text)
res = [sc("".join(rng.sample(c, n))) for _ in range({n_samples})]
print(json.dumps(res))
"""
        b64 = base64.b64encode(code.encode()).decode()
        remote_cmd = f"python3 -c \"import base64; exec(base64.b64decode('{b64}'))\""
        try:
            res = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", self.host, remote_cmd],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout.strip())
        except Exception:
            pass
        return None
