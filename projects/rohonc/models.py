"""Data models and statistical metrics for Rohonc Codex epigraphic analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ZipfFitResult:
    """Parameters and goodness-of-fit for Zipf-Mandelbrot rank-frequency distribution.
    
    Formula: f(r) = C / (r + beta)^gamma
    """
    gamma: float  # Exponent (natural language typical: 0.9 - 1.3)
    beta: float   # Offset parameter (natural language typical: 1.0 - 5.0)
    c_factor: float
    r_squared: float  # Goodness of fit (1.0 = perfect fit)
    is_natural_linguistic_fit: bool
    diagnostic: str


@dataclass(frozen=True)
class EntropyProfile:
    """Shannon entropy and conditional n-gram entropy profile."""
    h0_hartley: float       # log2(|V|) maximum unigram entropy
    h1_unigram: float       # H(S_1) unigram entropy
    h2_conditional: float   # H(S_2 | S_1) bigram conditional entropy
    h3_conditional: float   # H(S_3 | S_1, S_2) trigram conditional entropy
    redundancy: float       # 1 - (H_1 / H_0)
    effective_signary_size: float  # 2^H_1
    diagnostic: str


@dataclass(frozen=True)
class DirectionalityMetrics:
    """Epigraphic directionality metrics verifying Right-to-Left (RTL) writing."""
    initial_sign_entropy: float
    terminal_sign_entropy: float
    entropy_ratio_initial_to_terminal: float
    terminal_justification_clustering: float
    inferred_direction: str  # 'RTL' or 'LTR'
    p_directionality_significance: float


@dataclass(frozen=True)
class CodebookMorphology:
    """Tachygraphic codebook morphology and sign distribution metrics."""
    core_sign_ratio: float
    extended_ligature_ratio: float
    hapax_legomena_ratio: float
    yule_k_characteristic: float
    lempel_ziv_complexity: float
    hypothesized_system: str


@dataclass
class RohoncEpigraphicReport:
    """Comprehensive statistical epigraphic report for Rohonc Codex."""
    artifact_id: str
    total_tokens: int
    distinct_types: int
    zipf_fit: ZipfFitResult
    entropy: EntropyProfile
    directionality: DirectionalityMetrics
    morphology: CodebookMorphology
    linguistic_family_proximities: Dict[str, float] = field(default_factory=dict)
    summary_verdict: str = ""
