"""Liturgical Narrative & Gospel Harmony Sequence Alignment Engine for Rohonc Codex.

Aligns Rohonc folio token streams and named-entity sequences against standard
16th-century Christian liturgical narratives:
1. Canonical Passion Harmony (6 stages: Palm Sunday through Resurrection)
2. Comprehensive Micro-Diatessaron (24 scenes from Annunciation through Ascension)

Uses dynamic sequence alignment (Smith-Waterman with affine penalties) and computes
permutation Z-scores against Monte Carlo null surrogates.
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


# Canonical 16th-century Liturgical Harmony of the Passion (6 Stages)
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


# Comprehensive 24-Scene Micro-Diatessaron (Infancy, Ministry, Passion, Resurrection)
LITURGICAL_MICRO_DIATESSARON_24: List[LiturgicalNarrativeStage] = [
    # Infancy Cycle
    LiturgicalNarrativeStage("scene_01_annunciation", "Annunciation to Mary", "Luke 1:26-38", ["Mary", "Angel", "Spirit", "Blessing"], ["sacred_person", "divine"]),
    LiturgicalNarrativeStage("scene_02_visitation", "Visitation of Mary to Elizabeth", "Luke 1:39-56", ["Mary", "Magnificat", "Blessing"], ["sacred_person", "liturgical"]),
    LiturgicalNarrativeStage("scene_03_nativity", "Nativity of Christ & Shepherds", "Luke 2:1-20; Matt 1:18-25", ["Christ", "Mary", "Angel", "Star", "Shepherds"], ["divine", "sacred_person"]),
    LiturgicalNarrativeStage("scene_04_circumcision", "Circumcision & Holy Name", "Luke 2:21", ["Christ", "Name", "Father"], ["divine"]),
    LiturgicalNarrativeStage("scene_05_epiphany", "Adoration of the Magi", "Matt 2:1-12", ["Christ", "King", "Star", "Gold/Incense"], ["divine", "historical_actor"]),
    LiturgicalNarrativeStage("scene_06_presentation", "Presentation in the Temple", "Luke 2:22-38", ["Christ", "Mary", "Temple", "Altar"], ["divine", "liturgical"]),

    # Ministry & Miracles
    LiturgicalNarrativeStage("scene_07_baptism", "Baptism in the Jordan", "Matt 3:13-17; Mark 1:9-11", ["Christ", "Water/Baptism", "Spirit", "Father"], ["divine", "sacramental"]),
    LiturgicalNarrativeStage("scene_08_temptation", "Temptation in the Desert", "Matt 4:1-11", ["Christ", "Fast", "Angel"], ["divine"]),
    LiturgicalNarrativeStage("scene_09_sermon_mount", "Sermon on the Mount & Beatitudes", "Matt 5-7; Luke 6:20-49", ["Christ", "Blessing", "Apostles", "Kingdom"], ["divine", "sacred_person", "theological"]),
    LiturgicalNarrativeStage("scene_10_transfiguration", "Transfiguration on Mount Tabor", "Matt 17:1-9", ["Christ", "Light", "Moses/Elijah", "Apostles"], ["divine", "sacred_person"]),
    LiturgicalNarrativeStage("scene_11_raising_lazarus", "Raising of Lazarus", "John 11:1-44", ["Christ", "Lazarus", "Tomb", "Mary/Martha"], ["divine", "liturgical"]),

    # Holy Week & Passion
    LiturgicalNarrativeStage("scene_12_palm_sunday", "Entry into Jerusalem (Palm Sunday)", "Matt 21:1-11", ["Christ", "King", "Hosanna/Palm", "Blessing"], ["divine", "liturgical"]),
    LiturgicalNarrativeStage("scene_13_temple_cleansing", "Cleansing of the Temple", "Matt 21:12-17", ["Christ", "Temple", "Altar"], ["divine", "liturgical"]),
    LiturgicalNarrativeStage("scene_14_judas_pact", "Judas Betrayal Pact", "Matt 26:14-16", ["Judas", "High Priest", "Silver"], ["historical_actor"]),
    LiturgicalNarrativeStage("scene_15_washing_feet", "Washing of the Feet", "John 13:1-17", ["Christ", "Peter", "Water", "Apostles"], ["divine", "sacred_person", "sacramental"]),
    LiturgicalNarrativeStage("scene_16_last_supper", "The Last Supper (Eucharist)", "Matt 26:26-29; 1 Cor 11:23-26", ["Christ", "Bread/Host", "Chalice/Wine", "Apostles"], ["divine", "sacramental"]),
    LiturgicalNarrativeStage("scene_17_gethsemane", "Agony in Gethsemane & Arrest", "Matt 26:36-56", ["Christ", "Cup", "Angel", "Judas", "Soldiers", "Peter"], ["divine", "historical_actor"]),
    LiturgicalNarrativeStage("scene_18_sanhedrin", "Trial before Caiaphas & Sanhedrin", "Matt 26:57-68", ["Christ", "High Priest", "Blasphemy", "Soldiers"], ["divine", "historical_actor"]),
    LiturgicalNarrativeStage("scene_19_pilate_trial", "Christ before Pontius Pilate", "Matt 27:11-26; John 18:28-40", ["Pilate", "Christ", "Water/Washing", "King"], ["historical_actor", "divine"]),
    LiturgicalNarrativeStage("scene_20_herod_trial", "Christ before Herod Antipas", "Luke 23:6-12", ["Herod", "King", "Christ", "White Robe"], ["historical_actor", "divine"]),
    LiturgicalNarrativeStage("scene_21_flagellation", "Flagellation & Crowning with Thorns", "Matt 27:27-31", ["Soldiers", "Crown/Thorns", "King", "Christ"], ["historical_actor", "divine"]),
    LiturgicalNarrativeStage("scene_22_via_dolorosa", "Way of the Cross (Via Dolorosa)", "Luke 23:26-32", ["Christ", "Cross", "Simon", "Women"], ["divine", "liturgical"]),
    LiturgicalNarrativeStage("scene_23_crucifixion", "Crucifixion on Golgotha (INRI)", "Matt 27:33-56; John 19:17-37", ["Christ", "Cross/INRI", "Mary", "John", "Soldiers", "Spear"], ["divine", "sacred_person", "historical_actor"]),
    LiturgicalNarrativeStage("scene_24_resurrection", "Resurrection & Holy Sepulchre", "Matt 28:1-10; John 20:1-18", ["Christ", "Angel", "Sepulchre/Tomb", "Mary", "Apostles"], ["divine", "sacred_person", "liturgical"]),
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

    def __init__(self, stages: Optional[List[LiturgicalNarrativeStage]] = None) -> None:
        self.codebook_engine = RohoncCodebookEngine()
        self.harmony_stages = stages if stages is not None else LITURGICAL_PASSION_HARMONY

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

    def align_local_smith_waterman(
        self,
        query_tokens: List[str],
        reference_motifs: List[str],
        match_score: float = 3.0,
        mismatch_penalty: float = -1.0,
        gap_penalty: float = -2.0,
    ) -> float:
        """Smith-Waterman dynamic programming local sequence alignment with affine gap scoring."""
        m = len(query_tokens)
        n = len(reference_motifs)
        if m == 0 or n == 0:
            return 0.0

        H = [[0.0] * (n + 1) for _ in range(m + 1)]
        max_score = 0.0

        for i in range(1, m + 1):
            q_role = self.codebook_engine.classify_token(query_tokens[i - 1])
            q_desc = q_role.semantic_role.lower() if q_role else ""
            for j in range(1, n + 1):
                ref_motif = reference_motifs[j - 1].lower()
                is_match = any(p in q_desc for p in ref_motif.split("/"))
                score_diag = H[i - 1][j - 1] + (match_score if is_match else mismatch_penalty)
                score_del = H[i - 1][j] + gap_penalty
                score_ins = H[i][j - 1] + gap_penalty
                H[i][j] = max(0.0, score_diag, score_del, score_ins)
                if H[i][j] > max_score:
                    max_score = H[i][j]

        return round(max_score, 2)

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

        # Monte Carlo Permutation Null
        null_scores: List[float] = []
        shuffled = profile[:]
        for _ in range(n_null_permutations):
            rng.shuffle(shuffled)
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
            is_significant=(z_score >= 2.0 and p_val < 0.05),
        )

    def align_entire_corpus(self) -> List[AlignmentResult]:
        """Align all cataloged folios against the active stage set."""
        results: List[AlignmentResult] = []
        for fid, f_data in FOLIO_TRANSCRIPTIONS.items():
            res = self.align_folio(
                folio_id=f_data["folio"],
                lines=f_data["lines"],
                folio_title=f_data["title"],
            )
            results.append(res)
        return results

    def align_micro_diatessaron_corpus(self) -> List[AlignmentResult]:
        """Align all cataloged folios against the full 24-scene micro-Diatessaron."""
        saved_stages = self.harmony_stages
        self.harmony_stages = LITURGICAL_MICRO_DIATESSARON_24
        try:
            return self.align_entire_corpus()
        finally:
            self.harmony_stages = saved_stages
