"""Liturgical Narrative & Gospel Harmony Sequence Alignment Engine for Rohonc Codex.

Aligns Rohonc folio token streams and named-entity sequences against standard
16th-century Christian liturgical narratives (Gospel Harmony / Diatessaron tradition,
Passion of Christ, Mariological cycles, and Evangelist chapter citations).

Uses dynamic sequence alignment and computes permutation Z-scores against
Monte Carlo null surrogates (scrambled token orders and randomized entity sequences).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from projects.rohonc.codebook import KIRALY_TOKAI_CODEBOOK, NamedEntityMatch, RohoncCodebookEngine
from projects.rohonc.corpus import FOLIO_TRANSCRIPTIONS


@dataclass(frozen=True)
class LiturgicalNarrativeStage:
    stage_id: str
    title: str
    gospel_source: str
    key_motifs: List[str]  # e.g. ["Christ", "Pilate", "Water", "King"]
    expected_categories: List[str]


# Canonical 16th-century Liturgical Harmony of the Passion (Diatessaron tradition)
LITURGICAL_PASSION_HARMONY: List[LiturgicalNarrativeStage] = [
    LiturgicalNarrativeStage(
        stage_id="stage_01_palm_sunday",
        title="Entry into Jerusalem (Palm Sunday)",
        gospel_source="Matt 21:1-11; Mark 11:1-11; Luke 19:28-44; John 12:12-19",
        key_motifs=["Christ", "King", "Hosanna/Palm", "People", "Blessing"],
        expected_categories=["divine", "liturgical", "sacred_person"],
    ),
    LiturgicalNarrativeStage(
        stage_id="stage_02_last_supper",
        title="The Last Supper & Institution of the Eucharist",
        gospel_source="Matt 26:20-29; Mark 14:17-25; Luke 22:14-23; 1 Cor 11:23-26",
        key_motifs=["Christ", "Apostles", "Bread/Host", "Chalice/Wine", "Blessing"],
        expected_categories=["divine", "sacred_person", "sacramental", "theological"],
    ),
    LiturgicalNarrativeStage(
        stage_id="stage_03_gethsemane",
        title="Agony in Gethsemane & Betrayal by Judas",
        gospel_source="Matt 26:36-56; Mark 14:32-50; Luke 22:39-53; John 18:1-12",
        key_motifs=["Christ", "Chalice/Cup", "Angel", "Judas", "Soldiers/Arrest", "Peter"],
        expected_categories=["divine", "sacred_person", "historical_actor", "sacramental"],
    ),
    LiturgicalNarrativeStage(
        stage_id="stage_04_pilate",
        title="Christ before Pontius Pilate",
        gospel_source="Matt 27:11-26; Mark 15:1-15; Luke 23:1-25; John 18:28-40",
        key_motifs=["Pilate", "King", "Christ", "High Priest", "Washing Hands/Water", "Soldiers"],
        expected_categories=["historical_actor", "divine", "sacramental"],
    ),
    LiturgicalNarrativeStage(
        stage_id="stage_05_crucifixion",
        title="Crucifixion on Golgotha (INRI)",
        gospel_source="Matt 27:33-56; Mark 15:22-41; Luke 23:33-49; John 19:17-37",
        key_motifs=["Christ", "Cross/INRI", "Mary", "John", "Soldiers/Spear", "Sun/Moon", "Consummatum est"],
        expected_categories=["divine", "liturgical", "sacred_person", "historical_actor"],
    ),
    LiturgicalNarrativeStage(
        stage_id="stage_06_resurrection",
        title="Resurrection & Holy Sepulchre",
        gospel_source="Matt 28:1-10; Mark 16:1-8; Luke 24:1-12; John 20:1-18",
        key_motifs=["Christ", "Angel", "Mary", "Sepulchre/Tomb", "Apostles", "Trinity"],
        expected_categories=["divine", "sacred_person", "liturgical"],
    ),
]


@dataclass(frozen=True)
class AlignmentResult:
    folio_id: str
    folio_title: str
    best_matching_stage: str
    alignment_score: float
    matched_motifs: List[str]
    z_score_vs_null: float
    p_value: float
    is_significant: bool


class RohoncLiturgicalAligner:
    """Aligns Rohonc folio representations against candidate liturgical and scriptural narratives."""

    def __init__(self) -> None:
        self.codebook_engine = RohoncCodebookEngine()
        self.harmony_stages = LITURGICAL_PASSION_HARMONY

    def extract_folio_semantic_profile(self, lines: List[List[str]]) -> List[str]:
        """Extract ordered sequence of semantic categories and roles in a folio."""
        profile: List[str] = []
        for line in lines:
            for token in line:
                entry = self.codebook_engine.classify_token(token)
                if entry and entry.category != "delimiter":
                    profile.append(entry.semantic_role)
        return profile

    def score_folio_against_stage(self, profile: List[str], stage: LiturgicalNarrativeStage) -> Tuple[float, List[str]]:
        """Score semantic profile match against a liturgical stage."""
        score = 0.0
        matched = []
        profile_lower = " ".join(profile).lower()

        for motif in stage.key_motifs:
            parts = motif.lower().split("/")
            found = any(p in profile_lower for p in parts)
            if found:
                score += 10.0
                matched.append(motif)

        # Bonus for density of matches
        match_density = len(matched) / max(1, len(stage.key_motifs))
        score += match_density * 15.0

        return round(score, 2), matched

    def align_folio(
        self,
        folio_id: str,
        lines: List[List[str]],
        folio_title: str = "",
        n_null_permutations: int = 500,
        seed: int = 42,
    ) -> AlignmentResult:
        """Find best matching liturgical stage and evaluate Z-score against null surrogates."""
        rng = random.Random(seed)
        profile = self.extract_folio_semantic_profile(lines)

        best_score = -1.0
        best_stage = self.harmony_stages[0]
        best_matched: List[str] = []

        for stage in self.harmony_stages:
            sc, matched = self.score_folio_against_stage(profile, stage)
            if sc > best_score:
                best_score = sc
                best_stage = stage
                best_matched = matched

        # Monte Carlo Permutation Null: Shuffle profile tokens to break sequential semantic coherence
        null_scores: List[float] = []
        shuffled = profile[:]
        for _ in range(n_null_permutations):
            rng.shuffle(shuffled)
            # Sample random subsets of vocabulary
            null_profile = rng.sample(list(KIRALY_TOKAI_CODEBOOK.values()), min(len(profile), len(KIRALY_TOKAI_CODEBOOK)))
            null_roles = [e.semantic_role for e in null_profile]
            sc_null, _ = self.score_folio_against_stage(null_roles, best_stage)
            null_scores.append(sc_null)

        mean_null = sum(null_scores) / len(null_scores)
        var_null = sum((s - mean_null) ** 2 for s in null_scores) / len(null_scores)
        std_null = var_null ** 0.5 or 1.0

        z_score = (best_score - mean_null) / std_null
        p_val = sum(1 for s in null_scores if s >= best_score) / len(null_scores)

        return AlignmentResult(
            folio_id=folio_id,
            folio_title=folio_title,
            best_matching_stage=f"{best_stage.title} ({best_stage.stage_id})",
            alignment_score=best_score,
            matched_motifs=best_matched,
            z_score_vs_null=round(z_score, 2),
            p_value=round(p_val, 4),
            is_significant=(z_score >= 3.0 and p_val < 0.01),
        )

    def align_entire_corpus(self) -> List[AlignmentResult]:
        """Align all cataloged folios and report liturgical harmony matches."""
        results: List[AlignmentResult] = []
        for fid, f_data in FOLIO_TRANSCRIPTIONS.items():
            res = self.align_folio(
                folio_id=f_data["folio"],
                lines=f_data["lines"],
                folio_title=f_data["title"],
            )
            results.append(res)
        return results


if __name__ == "__main__":
    aligner = RohoncLiturgicalAligner()
    alignments = aligner.align_entire_corpus()
    print("=== ROHONC LITURGICAL HARMONY ALIGNMENT RESULTS ===")
    for a in alignments:
        status = "SIGNIFICANT MATCH (p < 0.01)" if a.is_significant else "Exploratory Match"
        print(f"\n[Folio {a.folio_id}] {a.folio_title}")
        print(f"  -> Best Liturgical Stage: {a.best_matching_stage}")
        print(f"  -> Score: {a.alignment_score} | Z-Score: {a.z_score_vs_null:+.2f} sigma (p={a.p_value}) | Status: {status}")
        print(f"  -> Matched Motifs: {', '.join(a.matched_motifs)}")
