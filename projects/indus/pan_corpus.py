"""Pan-Indus Corpus Ingestion and Stratification Engine across all archaeological sites and media.

Loads, harmonizes, and stratifies 3,219 inscriptions (12,910 tokens) across:
- Sites: Harappa, Mohenjo-Daro, Lothal, Dholavira, Kalibangan, Chanhu-daro, etc.
- Media: Seals, Incised/Molded Tablets, Pottery Graffiti, Clay Tags/Sealings.
- Motifs: Unicorn, Bull/Zebu, Elephant, Tiger, Rhinoceros, Gaur, Aniconic.
- Directionality: Right-to-Left (R/L) vs Left-to-Right (L/R).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from projects.indus.concordance import IndusConcordance


@dataclass(frozen=True, slots=True)
class PanInscription:
    artifact_id: str
    cisi_id: str
    line: int
    site: str
    region: str
    type_code: str
    broad_type: str
    symbol: str
    cult: str
    complete: str
    direction: str
    raw_signs: tuple[str, ...]
    signs_parpola: tuple[str, ...]
    signs_mahadevan: tuple[str, ...]
    signs_wells: tuple[str, ...]
    length: int


class PanIndusCorpus:
    """Manages the full pan-Indus corpus spanning 3,219 inscriptions from all archaeological sites."""

    def __init__(
        self,
        csv_path: Optional[Path] = None,
        concordance: Optional[IndusConcordance] = None,
    ) -> None:
        if csv_path is None:
            csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "indus" / "analytic_lines.csv"
        self.csv_path = Path(csv_path)
        self.concordance = concordance or IndusConcordance()
        self.inscriptions: list[PanInscription] = []
        self._load()

    def _load(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Pan-Indus dataset not found at: {self.csv_path}")

        inscriptions: list[PanInscription] = []
        with open(self.csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seq_key = row.get("sequence_key", "").strip()
                if not seq_key:
                    continue

                raw_tokens = tuple(s.strip() for s in seq_key.split("-") if s.strip())
                if not raw_tokens:
                    continue

                p_seq = tuple(self.concordance.normalize_sequence(raw_tokens, target_catalog="parpola"))
                m_seq = tuple(self.concordance.normalize_sequence(raw_tokens, target_catalog="mahadevan"))
                w_seq = tuple(self.concordance.normalize_sequence(raw_tokens, target_catalog="wells"))

                ins = PanInscription(
                    artifact_id=row.get("artifact_id", ""),
                    cisi_id=row.get("cisi_id", ""),
                    line=int(row.get("line", "1") or 1),
                    site=row.get("site", "Unknown").strip(),
                    region=row.get("region", "").strip(),
                    type_code=row.get("type", "").strip(),
                    broad_type=row.get("broad_type", "other").strip() or "other",
                    symbol=row.get("symbol", "").strip(),
                    cult=row.get("cult", "").strip(),
                    complete=row.get("complete", "Y").strip(),
                    direction=row.get("direction", "R/L").strip(),
                    raw_signs=raw_tokens,
                    signs_parpola=p_seq,
                    signs_mahadevan=m_seq,
                    signs_wells=w_seq,
                    length=len(raw_tokens),
                )
                inscriptions.append(ins)

        self.inscriptions = inscriptions

    def filter(self, predicate: Callable[[PanInscription], bool]) -> list[PanInscription]:
        return [ins for ins in self.inscriptions if predicate(ins)]

    def filter_by_site(self, site: str) -> list[PanInscription]:
        site_lower = site.lower()
        return [ins for ins in self.inscriptions if ins.site.lower() == site_lower]

    def filter_by_broad_type(self, broad_type: str) -> list[PanInscription]:
        bt_lower = broad_type.lower()
        return [ins for ins in self.inscriptions if ins.broad_type.lower() == bt_lower]

    def filter_by_direction(self, direction: str) -> list[PanInscription]:
        dir_upper = direction.upper()
        return [ins for ins in self.inscriptions if ins.direction.upper() == dir_upper]

    def get_sequences(
        self,
        target_catalog: str = "parpola",
        inscriptions_subset: Optional[Sequence[PanInscription]] = None,
        **kwargs: Any,
    ) -> list[list[str]]:
        catalog = kwargs.get("catalog", target_catalog)
        subset = self.inscriptions if inscriptions_subset is None else inscriptions_subset
        cat = catalog.lower()
        if cat == "parpola":
            return [list(ins.signs_parpola) for ins in subset]
        elif cat == "mahadevan":
            return [list(ins.signs_mahadevan) for ins in subset]
        elif cat == "wells":
            return [list(ins.signs_wells) for ins in subset]
        else:
            return [list(ins.raw_signs) for ins in subset]

    def get_summary(self, inscriptions_subset: Optional[Sequence[PanInscription]] = None) -> dict[str, Any]:
        subset = self.inscriptions if inscriptions_subset is None else inscriptions_subset
        all_tokens = [s for ins in subset for s in ins.signs_parpola]
        unique_signs = set(all_tokens)
        lengths = [len(ins.raw_signs) for ins in subset]

        from collections import Counter
        site_counts = dict(Counter(ins.site for ins in subset).most_common(10))
        type_counts = dict(Counter(ins.broad_type for ins in subset).most_common(10))
        dir_counts = dict(Counter(ins.direction for ins in subset).most_common(5))

        return {
            "total_inscriptions": len(subset),
            "total_tokens": len(all_tokens),
            "signary_types": len(unique_signs),
            "mean_length": round(sum(lengths) / max(len(lengths), 1), 2),
            "max_length": max(lengths) if lengths else 0,
            "min_length": min(lengths) if lengths else 0,
            "sites": site_counts,
            "broad_types": type_counts,
            "directions": dir_counts,
        }
