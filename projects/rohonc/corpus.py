"""Rohonc Codex catalog definitions, sign systems, and structural metadata."""

from __future__ import annotations

from cipher_lab.models import CipherProvenance

ROHONC_PROVENANCE = CipherProvenance(
    artifact_id="rohonc_codex",
    catalog_version="kiraly_tokai_2018",
    source_citation="Király, L. Z., & Tokai, G. (2018). The Rohonc Codex: A New Perspective.",
    source_sha256="synthetic_fixture_v1",
    creator_attribution="Central European early-modern scribe/monk",
    historical_date_range="c. 1530-1550",
)

CORE_SIGN_COUNT = 150
EXTENDED_SIGN_COUNT = 792
TOTAL_CHARACTERS_ESTIMATE = 87000
