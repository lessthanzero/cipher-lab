"""Autonomous Epistemic Discovery Loop for Historical Ciphers."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Optional

from cipher_lab.harness import ModelRefereeHarness, RemoteComputeWorker
from cipher_lab.ledger import EpistemicLedger
from cipher_lab.models import CandidateEvaluation
from cipher_lab.stats import (
    QuadgramScorer,
    calculate_chi_squared,
    calculate_empirical_p_value,
    calculate_index_of_coincidence,
    check_unicity_distance,
    order_shuffle_null,
)
from cipher_lab.telemetry import TelemetryGuard


class CipherDiscoveryLoop:
    """Self-improving autonomous discovery loop with telemetry stress guardrails and time budgeting."""

    def __init__(
        self,
        artifact_id: str,
        ciphertext: str,
        alphabet_size: int,
        key_space_bits: float,
        historical_context: str,
        data_dir: Path,
        time_budget_secs: Optional[float] = None,
        min_available_ram_gb: float = 2.0,
        max_cpu_load: float = 1.20,
    ) -> None:
        self.artifact_id = artifact_id
        self.ciphertext = ciphertext
        self.alphabet_size = alphabet_size
        self.key_space_bits = key_space_bits
        self.context = historical_context
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.time_budget_secs = time_budget_secs
        self.start_time = time.time()
        
        self.telemetry = TelemetryGuard(
            min_available_ram_gb=min_available_ram_gb,
            max_cpu_load=max_cpu_load,
        )
        self.ledger = EpistemicLedger(self.data_dir)
        self.scorer = QuadgramScorer()
        self.referee_harness = ModelRefereeHarness()
        self.remote_worker = RemoteComputeWorker()
        self.checkpoint_file = self.data_dir / f"checkpoint_{artifact_id}.json"

        self.best_candidate: Optional[CandidateEvaluation] = None

    def is_time_exhausted(self) -> bool:
        """Check if active wall-clock time limit has been reached."""
        if self.time_budget_secs is None:
            return False
        elapsed = time.time() - self.start_time
        return elapsed >= self.time_budget_secs

    def save_checkpoint(self) -> None:
        """Persist loop state to disk."""
        elapsed = time.time() - self.start_time
        summary = self.ledger.get_summary_statistics(self.artifact_id)
        ckpt = {
            "artifact_id": self.artifact_id,
            "elapsed_seconds": round(elapsed, 2),
            "time_budget_seconds": self.time_budget_secs,
            "best_candidate": self.best_candidate.model_dump() if self.best_candidate else None,
            "ledger_summary": summary,
        }
        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(ckpt, f, indent=2)

    def evaluate_candidate(
        self,
        hypothesis_name: str,
        key_class: str,
        key_desc: str,
        candidate_pt: str,
        candidate_key_bits: Optional[float] = None,
    ) -> CandidateEvaluation:
        """Run two-tier evaluation on candidate plaintext under telemetry and unicity bounds."""
        trial_id = str(uuid.uuid4())[:8]
        effective_bits = candidate_key_bits if candidate_key_bits is not None else self.key_space_bits
        
        # Resource health and cooperative cooldown check
        healthy, msg = self.telemetry.check_health_and_cooldown()
        if not healthy:
            # Throttle or pause if RAM is critical
            print(f"[!] {msg}")

        # Gate 0: Shannon Unicity Distance
        unicity = check_unicity_distance(
            payload_len=len(candidate_pt),
            alphabet_size=self.alphabet_size,
            key_space_bits=effective_bits,
        )
        
        if unicity.is_underdetermined:
            self.ledger.record_trial(
                trial_id=trial_id,
                artifact_id=self.artifact_id,
                hypothesis_name=hypothesis_name,
                key_class=key_class,
                payload_len=len(candidate_pt),
                unicity_distance=unicity.unicity_distance_chars,
                passed_unicity=False,
                raw_fitness=0.0,
                empirical_p_value=1.0,
                negative_twin_fitness=0.0,
                falsification_status="ABSTAIN",
                abstention_reason=unicity.warning,
            )
            return CandidateEvaluation(
                candidate_id=trial_id,
                artifact_id=self.artifact_id,
                hypothesis_name=hypothesis_name,
                key_description=key_desc,
                plaintext_preview=candidate_pt[:60],
                quadgram_score=self.scorer.score(candidate_pt),
                index_of_coincidence=calculate_index_of_coincidence(candidate_pt),
                empirical_p_value=1.0,
                passed_unicity_gate=False,
                negative_twin_score=0.0,
                is_statistically_viable=False,
                abstention_reason=unicity.warning,
            )

        # Gate 1: Deterministic 0-Token Math Gating
        raw_fitness = self.scorer.score(candidate_pt)
        ic_val = calculate_index_of_coincidence(candidate_pt)
        chi_sq_val = calculate_chi_squared(candidate_pt)

        # Generate null surrogate distribution (Offload to Fedora PC worker if reachable)
        null_scores = None
        if self.remote_worker.is_reachable():
            null_scores = self.remote_worker.run_remote_monte_carlo(candidate_pt, n_samples=500)
            
        if not null_scores:
            null_surrogates = order_shuffle_null(list(candidate_pt), n_samples=200)
            null_scores = [self.scorer.score("".join(s)) for s in null_surrogates]

        empirical_p = calculate_empirical_p_value(raw_fitness, null_scores, higher_is_better=True)
        twin_fitness = null_scores[0] if null_scores else -12.0

        # Statistical viability criteria:
        # 1. p < 0.005 against null surrogates
        # 2. Chi-squared < 45.0
        # 3. IC > 0.055
        is_statistically_viable = (empirical_p < 0.005) and (chi_sq_val < 45.0) and (ic_val > 0.055)

        referee_verdict = None
        referee_conf = None

        # Gate 2: Double-Blind Foil Referee (only for statistically viable candidates)
        if is_statistically_viable and self.telemetry.can_invoke_model(estimated_tokens=600):
            null_surrogates = order_shuffle_null(list(candidate_pt), n_samples=5)
            decoys = ["".join(s) for s in null_surrogates[:3]]
            ref_res = self.referee_harness.evaluate_with_blinded_foils(
                candidate_plaintext=candidate_pt,
                decoy_plaintexts=decoys,
                artifact_context=self.context,
            )
            self.telemetry.record_tokens(600)
            if ref_res.get("status") == "success":
                if ref_res.get("candidate_selected"):
                    referee_verdict = f"APPROVED (confidence={ref_res.get('confidence')})"
                elif ref_res.get("decoy_selected"):
                    referee_verdict = "REJECTED (foil pareidolia detected)"
                else:
                    referee_verdict = "INCONCLUSIVE (all marked noise)"
                referee_conf = ref_res.get("confidence")

        status_str = "CANDIDATE" if (is_statistically_viable and referee_verdict and "APPROVED" in referee_verdict) else (
            "STAT_SIGNIFICANT" if is_statistically_viable else "REJECTED"
        )

        self.ledger.record_trial(
            trial_id=trial_id,
            artifact_id=self.artifact_id,
            hypothesis_name=hypothesis_name,
            key_class=key_class,
            payload_len=len(candidate_pt),
            unicity_distance=unicity.unicity_distance_chars,
            passed_unicity=True,
            raw_fitness=raw_fitness,
            empirical_p_value=empirical_p,
            negative_twin_fitness=twin_fitness,
            falsification_status=status_str,
            abstention_reason=None,
            referee_evaluated=bool(referee_verdict),
            referee_verdict=referee_verdict,
        )

        eval_obj = CandidateEvaluation(
            candidate_id=trial_id,
            artifact_id=self.artifact_id,
            hypothesis_name=hypothesis_name,
            key_description=key_desc,
            plaintext_preview=candidate_pt[:60],
            quadgram_score=raw_fitness,
            index_of_coincidence=ic_val,
            empirical_p_value=empirical_p,
            passed_unicity_gate=True,
            negative_twin_score=twin_fitness,
            is_statistically_viable=is_statistically_viable,
            referee_verdict=referee_verdict,
            referee_confidence=referee_conf,
            metadata={
                "chi_squared": chi_sq_val,
                "remote_worker_used": self.remote_worker.is_reachable(),
            },
        )

        if self.best_candidate is None or eval_obj.quadgram_score > self.best_candidate.quadgram_score:
            self.best_candidate = eval_obj

        return eval_obj
