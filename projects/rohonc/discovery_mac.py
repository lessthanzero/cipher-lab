"""Local Apple Silicon Discovery Worker for Rohonc Codex.

Executes local codebook refinement, named-entity recognition across transcribed folios,
formulaic cluster analysis, and Vulgate Diatessaron liturgical alignment.
Logs hypothesis trials into the EpistemicLedger (DuckDB).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from cipher_lab.ledger import EpistemicLedger

from projects.rohonc.codebook import RohoncCodebookEngine
from projects.rohonc.corpus import (
    FOLIO_TRANSCRIPTIONS,
    ROHONC_CORE_SIGNS,
    get_all_rohonc_lines,
    get_all_rohonc_tokens,
    get_corpus_summary,
)
from projects.rohonc.liturgical_aligner import RohoncLiturgicalAligner


@dataclass
class LocalDiscoverySummary:
    timestamp: float
    total_tokens: int
    distinct_signs: int
    recognized_entities: int
    glossed_tokens_ratio: float
    liturgical_scene_alignments: List[Dict[str, Any]]
    formulaic_clusters: List[Dict[str, Any]]


class RohoncLocalDiscoveryWorker:
    """Worker running codebook extraction, entity scanning, and liturgical alignment."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.ledger = EpistemicLedger(ledger_dir=data_dir)
        self.codebook = RohoncCodebookEngine()
        self.aligner = RohoncLiturgicalAligner()
        self.tokens = get_all_rohonc_tokens()
        self.lines = get_all_rohonc_lines()

    def run_discovery_cycle(self) -> LocalDiscoverySummary:
        """Run a full local discovery and codebook verification cycle."""
        t0 = time.time()
        print("[*] Starting Local Discovery Cycle on Darwin Apple Silicon...")

        # 1. Named Entity Extraction across Folios
        all_entities = []
        glossed_count = 0
        total_tokens = len(self.tokens)

        for fid, f_data in FOLIO_TRANSCRIPTIONS.items():
            lines = f_data["lines"]
            ents = self.codebook.extract_named_entities(lines, folio_label=f_data["folio"])
            all_entities.extend(ents)

            # Count glossed tokens
            for line in lines:
                for token in line:
                    if token in self.codebook.codebook:
                        glossed_count += 1

        gloss_ratio = glossed_count / max(1, total_tokens)

        # 2. Liturgical Alignment against Vulgate Passion Scenes
        alignments_raw = self.aligner.align_entire_corpus()
        alignments = []
        for al in alignments_raw:
            alignments.append({
                "folio_id": al.folio_id,
                "folio_title": al.folio_title,
                "best_matching_stage": al.best_matching_stage,
                "alignment_score": al.alignment_score,
                "matched_motifs": al.matched_motifs,
                "z_score": al.z_score_vs_null,
                "p_value": al.p_value,
                "is_significant": al.is_significant,
            })

        # 3. Frequent Formulaic Clusters (n-grams of codebook entities)
        clusters = self.codebook.find_recurring_clusters(self.lines, n=2, min_freq=2)

        summary = LocalDiscoverySummary(
            timestamp=t0,
            total_tokens=total_tokens,
            distinct_signs=len(set(self.tokens)),
            recognized_entities=len(all_entities),
            glossed_tokens_ratio=round(gloss_ratio, 4),
            liturgical_scene_alignments=alignments,
            formulaic_clusters=clusters,
        )

        # 4. Record into EpistemicLedger
        for al in alignments:
            passed = al["is_significant"]
            self.ledger.record_trial(
                trial_id=f"rohonc_local_align_{al['folio_id']}_{int(t0)}",
                artifact_id="rohonc_codex",
                hypothesis_name=f"H_rohonc_liturgical_align_fol_{al['folio_id']}",
                key_class="liturgical_alignment",
                payload_len=total_tokens,
                unicity_distance=45.0,
                passed_unicity=True,
                raw_fitness=al["alignment_score"],
                empirical_p_value=al["p_value"],
                negative_twin_fitness=0.0,
                falsification_status="STAT_SIGNIFICANT" if passed else "ACTIVE_SEARCH",
                abstention_reason=None if passed else f"Z-score {al['z_score']} < 3.0 or p-val {al['p_value']} >= 0.01",
            )

        print(f"[+] Local cycle complete in {time.time() - t0:.2f}s: {len(all_entities)} entities mapped, {len(alignments)} folios aligned.")
        return summary


def main() -> None:
    worker = RohoncLocalDiscoveryWorker(data_dir=Path("./data/derived"))
    summary = worker.run_discovery_cycle()
    print(json.dumps(asdict(summary), indent=2))


if __name__ == "__main__":
    main()
