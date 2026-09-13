"""Comprehensive Epistemic Ledger Runner for the Shugborough Inscription Project.

Executes all analytical modalities:
1. Information Theory & Shannon Unicity Distance calculation.
2. Codicological & Stone Epigraphy validation (Scheemakers 1748–1756, interpuncts, U vs V, D.M.).
3. Bayesian Latin Language Model initialism scoring.
4. Mathematical debunker of pseudohistoric/polyalphabetic claims.
5. Multi-node trial logging to DuckDB and JSONL.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import duckdb

from projects.shugborough.epigraphy import ShugboroughEpigraphy
from projects.shugborough.information_theory import ShugboroughInformationTheory
from projects.shugborough.initialism_model import ShugboroughInitialismEvaluator
from projects.shugborough.pseudohistory_debunker import ShugboroughPseudohistoryDebunker


class ShugboroughExperimentRunner:
    """Orchestrates comprehensive evaluations and persists epistemic trial ledger."""

    def __init__(self, db_path: Path | None = None, jsonl_path: Path | None = None) -> None:
        derived_dir = Path(__file__).resolve().parent.parent.parent / "data" / "derived"
        derived_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path or (derived_dir / "shugborough_trials.duckdb")
        self.jsonl_path = jsonl_path or (derived_dir / "shugborough_trials.jsonl")
        self._init_db()

    def _init_db(self) -> None:
        con = duckdb.connect(str(self.db_path))
        con.execute("""
            CREATE TABLE IF NOT EXISTS shugborough_trials (
                trial_id VARCHAR PRIMARY KEY,
                timestamp_utc VARCHAR,
                modality VARCHAR,
                candidate_or_claim VARCHAR,
                shannon_entropy_bits DOUBLE,
                unicity_satisfied BOOLEAN,
                joint_log_likelihood DOUBLE,
                epigraphic_concord BOOLEAN,
                verdict VARCHAR,
                details JSON
            )
        """)
        con.close()

    def log_trial(
        self,
        trial_id: str,
        modality: str,
        candidate_or_claim: str,
        shannon_entropy_bits: float,
        unicity_satisfied: bool,
        joint_log_likelihood: float,
        epigraphic_concord: bool,
        verdict: str,
        details: Dict[str, Any],
    ) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        con = duckdb.connect(str(self.db_path))
        con.execute(
            """
            INSERT OR REPLACE INTO shugborough_trials
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                trial_id,
                ts,
                modality,
                candidate_or_claim,
                shannon_entropy_bits,
                unicity_satisfied,
                joint_log_likelihood,
                epigraphic_concord,
                verdict,
                json.dumps(details),
            ],
        )
        con.close()

        # Append to JSONL
        record = {
            "trial_id": trial_id,
            "timestamp_utc": ts,
            "modality": modality,
            "candidate_or_claim": candidate_or_claim,
            "shannon_entropy_bits": shannon_entropy_bits,
            "unicity_satisfied": unicity_satisfied,
            "joint_log_likelihood": joint_log_likelihood,
            "epigraphic_concord": epigraphic_concord,
            "verdict": verdict,
            "details": details,
        }
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def run_full_campaign(self) -> Dict[str, Any]:
        """Execute complete epistemic investigation and return structured report."""
        # 1. Information theory profile
        info_profile = ShugboroughInformationTheory.get_entropy_profile()
        self.log_trial(
            trial_id="shugborough_info_theory_baseline",
            modality="information_theory",
            candidate_or_claim="OUOSVAVV (N=8)",
            shannon_entropy_bits=info_profile.total_entropy_bits,
            unicity_satisfied=info_profile.is_unicity_satisfied,
            joint_log_likelihood=0.0,
            epigraphic_concord=True,
            verdict="Underdetermined (Violates Unicity Distance N << U_0)",
            details={
                "mono_u0": info_profile.unicity_monoalphabetic_chars,
                "poly_u0": info_profile.unicity_polyalphabetic_period_5_chars,
                "entropy_per_symbol": info_profile.shannon_entropy_bits_per_symbol,
            },
        )

        # 2. Epigraphy profile
        epigraphy = ShugboroughEpigraphy.get_canonical_profile()
        self.log_trial(
            trial_id="shugborough_epigraphic_stone_audit",
            modality="epigraphy",
            candidate_or_claim="Shepherd's Monument Physical Inscription",
            shannon_entropy_bits=info_profile.total_entropy_bits,
            unicity_satisfied=False,
            joint_log_likelihood=0.0,
            epigraphic_concord=True,
            verdict="Initialism Confirmed by Carved Interpuncts and U/V Distinction",
            details={
                "monument": epigraphy.monument_name,
                "sculptor": epigraphy.sculptor,
                "interpuncts_confirmed": epigraphy.is_initialism_confirmed_by_interpuncts,
                "dedication": epigraphy.funerary_dedication,
            },
        )

        # 3. Initialism candidates evaluation
        evaluator = ShugboroughInitialismEvaluator()
        candidates = evaluator.evaluate_all()
        for cand in candidates:
            self.log_trial(
                trial_id=f"cand_{cand.candidate_id}",
                modality="latin_initialism_bayesian",
                candidate_or_claim=cand.raw_text,
                shannon_entropy_bits=info_profile.total_entropy_bits,
                unicity_satisfied=False,
                joint_log_likelihood=cand.joint_log_likelihood,
                epigraphic_concord=cand.epigraphic_u_v_concord,
                verdict=cand.verdict,
                details={
                    "author": cand.author,
                    "year": cand.year,
                    "language": cand.language,
                    "translation": cand.translation,
                    "grammar": cand.grammatical_validity,
                    "historical": cand.historical_coherence,
                    "dis_manibus": cand.dis_manibus_compatibility,
                },
            )

        # 4. Pseudohistory and polyalphabetic debunker
        debunker = ShugboroughPseudohistoryDebunker()
        magdalen_proof = debunker.prove_polyalphabetic_triviality("MAGDALEN")
        self.log_trial(
            trial_id="debunk_polyalphabetic_magdalen",
            modality="cryptanalytic_falsification",
            candidate_or_claim="Ramsden 2014 Polyalphabetic 'Magdalen'",
            shannon_entropy_bits=info_profile.total_entropy_bits,
            unicity_satisfied=False,
            joint_log_likelihood=-999.0,
            epigraphic_concord=False,
            verdict="Falsified (Shannon Perfect Secrecy Triviality: Any 8-letter word is producible)",
            details={
                "ciphertext": magdalen_proof.ciphertext,
                "target": magdalen_proof.target_plaintext,
                "derived_key": magdalen_proof.derived_vigenere_key,
                "proof": magdalen_proof.mathematical_implication,
            },
        )

        treasure_proof = debunker.evaluate_anson_treasure_coordinates()
        self.log_trial(
            trial_id="debunk_anson_treasure_coordinates",
            modality="cryptanalytic_falsification",
            candidate_or_claim="Edmunds 2016 Anson Treasure Coordinates",
            shannon_entropy_bits=info_profile.total_entropy_bits,
            unicity_satisfied=False,
            joint_log_likelihood=-999.0,
            epigraphic_concord=False,
            verdict=treasure_proof["verdict"],
            details=treasure_proof,
        )

        return {
            "info_profile": info_profile,
            "epigraphy": epigraphy,
            "candidates": candidates,
            "trials_logged_duckdb": str(self.db_path),
            "trials_logged_jsonl": str(self.jsonl_path),
        }


if __name__ == "__main__":
    runner = ShugboroughExperimentRunner()
    results = runner.run_full_campaign()
    print("=== SHUGBOROUGH CAMPAIGN COMPLETED SUCCESSFULLY ===")
    print(f"Trials persisted to: {results['trials_logged_duckdb']}")
    print(f"Candidate count evaluated: {len(results['candidates'])}")
    for c in results["candidates"]:
        print(f"- [{c.candidate_id}]: {c.joint_log_likelihood} -> {c.verdict}")
