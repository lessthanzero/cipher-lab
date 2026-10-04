"""Dual-catalog concordance normalization engine for Indus Valley script signs.

Provides bidirectional grapheme mapping between Parpola (CISI), Mahadevan (M77),
and Wells (ICIT) signaries to ensure statistical metrics remain catalog-invariant.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence


@dataclass(frozen=True, slots=True)
class ConcordanceEntry:
    parpola_id: str
    description: str
    mahadevan_ids: tuple[str, ...]
    wells_ids: tuple[str, ...]


class IndusConcordance:
    """Manages cross-catalog mappings between Parpola, Mahadevan, and Wells sign lists."""

    def __init__(self, data_path: Optional[Path] = None) -> None:
        if data_path is None:
            # Default location
            data_path = Path(__file__).resolve().parent.parent.parent / "data" / "indus" / "sign_concordance.json"
        
        self.data_path = Path(data_path)
        self._parpola_map: dict[str, ConcordanceEntry] = {}
        self._mahadevan_to_parpola: dict[str, list[str]] = {}
        self._wells_to_parpola: dict[str, list[str]] = {}
        self._load()

    def _load(self) -> None:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Concordance file not found: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for p_id, info in data.items():
            entry = ConcordanceEntry(
                parpola_id=p_id,
                description=info.get("description", ""),
                mahadevan_ids=tuple(info.get("mahadevan_ids", [])),
                wells_ids=tuple(info.get("wells_ids", [])),
            )
            self._parpola_map[p_id] = entry

            for m_id in entry.mahadevan_ids:
                self._mahadevan_to_parpola.setdefault(m_id, []).append(p_id)
            for w_id in entry.wells_ids:
                self._wells_to_parpola.setdefault(w_id, []).append(p_id)

    def get_entry(self, parpola_id: str) -> Optional[ConcordanceEntry]:
        return self._parpola_map.get(parpola_id)

    def parpola_to_mahadevan(self, parpola_id: str) -> Optional[str]:
        """Map Parpola ID (e.g. 'P324') to primary Mahadevan ID (e.g. 'M342')."""
        entry = self._parpola_map.get(parpola_id)
        if entry and entry.mahadevan_ids:
            return entry.mahadevan_ids[0]
        return None

    def mahadevan_to_parpola(self, mahadevan_id: str) -> Optional[str]:
        """Map Mahadevan ID (e.g. 'M342') to primary Parpola ID (e.g. 'P324')."""
        p_list = self._mahadevan_to_parpola.get(mahadevan_id)
        if p_list:
            return p_list[0]
        return None

    def parpola_to_wells(self, parpola_id: str) -> Optional[str]:
        """Map Parpola ID to primary Wells ID."""
        entry = self._parpola_map.get(parpola_id)
        if entry and entry.wells_ids:
            return entry.wells_ids[0]
        return None

    def normalize_sequence(
        self,
        sequence: Sequence[str],
        target_catalog: str = "mahadevan",
        unmapped_policy: str = "keep",
    ) -> list[str]:
        """Convert a sequence of sign IDs to the requested catalog.
        
        Parameters
        ----------
        sequence : Sequence[str]
            List of sign identifiers (default assume Parpola format 'P###').
        target_catalog : str
            One of 'mahadevan', 'parpola', or 'wells'.
        unmapped_policy : str
            'keep' preserves the original ID if unmapped; 'drop' excludes it.
        """
        target = target_catalog.lower()
        normalized: list[str] = []

        for sign in sequence:
            mapped_sign: Optional[str] = None
            if target == "mahadevan":
                if sign.startswith("P"):
                    mapped_sign = self.parpola_to_mahadevan(sign)
                elif sign.startswith("M"):
                    mapped_sign = sign
            elif target == "wells":
                if sign.startswith("P"):
                    mapped_sign = self.parpola_to_wells(sign)
                elif sign.startswith("W"):
                    mapped_sign = sign
            elif target == "parpola":
                if sign.startswith("M"):
                    mapped_sign = self.mahadevan_to_parpola(sign)
                elif sign.startswith("P"):
                    mapped_sign = sign

            if mapped_sign:
                normalized.append(mapped_sign)
            elif unmapped_policy == "keep":
                normalized.append(sign)

        return normalized

    def get_summary(self) -> dict[str, int]:
        """Return catalog size and concordance coverage metrics."""
        mapped_to_m = sum(1 for e in self._parpola_map.values() if e.mahadevan_ids)
        mapped_to_w = sum(1 for e in self._parpola_map.values() if e.wells_ids)
        return {
            "total_parpola_signs": len(self._parpola_map),
            "mapped_to_mahadevan": mapped_to_m,
            "mapped_to_wells": mapped_to_w,
            "unique_mahadevan_targets": len(self._mahadevan_to_parpola),
            "unique_wells_targets": len(self._wells_to_parpola),
        }
