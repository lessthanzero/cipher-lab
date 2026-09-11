"""Epistemic contracts and models for historical cryptanalysis."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EpistemicLayer(str, Enum):
    OBSERVATION = "observation"          # Raw physical glyphs, scans, character sequences
    TRANSCRIPTION = "transcription"      # Normalized token sequence under a specific catalog
    INTERPRETATION = "interpretation"    # Structural, entropic, or period hypothesis
    CANDIDATE_SOLUTION = "candidate"     # Key mapping and candidate plaintext
    FALSIFICATION = "falsification"      # Null permutation test or negative-twin outcome


class CipherProvenance(BaseModel):
    artifact_id: str
    catalog_version: str
    source_citation: str
    source_sha256: str
    creator_attribution: str | None = None
    historical_date_range: str | None = None


class UnicityCheck(BaseModel):
    payload_length: int
    alphabet_size: int
    estimated_key_space_bits: float
    unicity_distance_chars: float
    is_underdetermined: bool
    warning: str | None = None


class CandidateEvaluation(BaseModel):
    candidate_id: str
    artifact_id: str
    hypothesis_name: str
    layer: EpistemicLayer = EpistemicLayer.CANDIDATE_SOLUTION
    key_description: str
    plaintext_preview: str
    quadgram_score: float
    index_of_coincidence: float
    empirical_p_value: float
    passed_unicity_gate: bool
    negative_twin_score: float
    is_statistically_viable: bool
    referee_verdict: str | None = None
    referee_confidence: float | None = None
    abstention_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
