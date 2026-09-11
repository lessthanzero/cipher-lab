"""Append-only Epistemic Trial Ledger for tracking trials, rejections, and FDR denominators."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb


class EpistemicLedger:
    """Tracks every hypothesis trial, unicity check, and abstention in an append-only DuckDB ledger."""

    def __init__(self, ledger_dir: Path) -> None:
        self.ledger_dir = Path(ledger_dir)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.ledger_dir / "epistemic_ledger.duckdb"
        self._init_db()

    def _init_db(self) -> None:
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hypothesis_trials (
                    trial_id VARCHAR PRIMARY KEY,
                    timestamp VARCHAR,
                    artifact_id VARCHAR,
                    hypothesis_name VARCHAR,
                    key_class VARCHAR,
                    payload_len INTEGER,
                    unicity_distance DOUBLE,
                    passed_unicity BOOLEAN,
                    raw_fitness DOUBLE,
                    empirical_p_value DOUBLE,
                    negative_twin_fitness DOUBLE,
                    falsification_status VARCHAR,
                    abstention_reason VARCHAR,
                    referee_evaluated BOOLEAN,
                    referee_verdict VARCHAR
                )
            """)

    def record_trial(
        self,
        trial_id: str,
        artifact_id: str,
        hypothesis_name: str,
        key_class: str,
        payload_len: int,
        unicity_distance: float,
        passed_unicity: bool,
        raw_fitness: float,
        empirical_p_value: float,
        negative_twin_fitness: float,
        falsification_status: str,
        abstention_reason: str | None = None,
        referee_evaluated: bool = False,
        referee_verdict: str | None = None,
    ) -> None:
        """Record a trial into the append-only ledger."""
        now_str = datetime.now(UTC).isoformat()
        with duckdb.connect(str(self.db_path)) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO hypothesis_trials VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, [
                trial_id, now_str, artifact_id, hypothesis_name, key_class,
                payload_len, unicity_distance, passed_unicity, raw_fitness,
                empirical_p_value, negative_twin_fitness, falsification_status,
                abstention_reason or "", referee_evaluated, referee_verdict or ""
            ])

    def get_summary_statistics(self, artifact_id: str) -> dict[str, Any]:
        """Compute multiplicity-adjusted denominator statistics across all recorded trials."""
        with duckdb.connect(str(self.db_path)) as conn:
            total_trials = conn.execute(
                "SELECT count(*) FROM hypothesis_trials WHERE artifact_id = ?", [artifact_id]
            ).fetchone()[0]
            
            abstentions = conn.execute(
                "SELECT count(*) FROM hypothesis_trials WHERE artifact_id = ? AND falsification_status = 'ABSTAIN'",
                [artifact_id]
            ).fetchone()[0]
            
            candidates = conn.execute(
                "SELECT count(*) FROM hypothesis_trials WHERE artifact_id = ? AND falsification_status = 'CANDIDATE'",
                [artifact_id]
            ).fetchone()[0]
            
            best_p = conn.execute(
                "SELECT min(empirical_p_value) FROM hypothesis_trials WHERE artifact_id = ?",
                [artifact_id]
            ).fetchone()[0] or 1.0

        # Bonferroni adjusted threshold
        bonferroni_thresh = 0.05 / max(total_trials, 1)

        return {
            "total_trials_denominator": total_trials,
            "abstention_count": abstentions,
            "candidate_count": candidates,
            "minimum_empirical_p": best_p,
            "bonferroni_critical_p": bonferroni_thresh,
            "has_survived_multiplicity": best_p < bonferroni_thresh,
        }
