"""Indus Epigraphic Reader & Structural Syntax Parser.

Translates Indus inscriptions into functional administrative sentence diagrams:
- Performs deterministic multi-clause segmentation (1, 2, or 3 clauses).
- Maps each grapheme to its (Root, Modifier) decomposition and syntactic slot role:
    Class 0: [AUTHORITY / OFFICE / TITLE]
    Class 1: [ADMINISTRATIVE SPECIFIER / GUILD ATTRIBUTE]
    Class 2: [COMMODITY / TRANSACTIONAL OBJECT]
    Class 3: [NUMERICAL QUANTITY / MEASURE TALLY]
    Class 4: [TERMINAL VERIFICATION SINK / CONSIGNMENT SEAL]
- Synthesizes a formal structural English gloss respecting zero-decipherment discipline.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from projects.indus.compound_grammar import CompoundGrammarEngine, CompoundParseResult
from projects.indus.concordance import IndusConcordance
from projects.indus.ligature_algebra import LigatureDecomposer
from projects.indus.pan_analytics import PanIndusAnalyzer
from projects.indus.pan_corpus import PanIndusCorpus, PanInscription


CLASS_SLOT_DESCRIPTIONS = {
    0: "AUTHORITY / INSTITUTION / TITLE",
    1: "ADMINISTRATIVE SPECIFIER / CADRE",
    2: "COMMODITY / TRANSACTIONAL SPECIFIER",
    3: "NUMERICAL QUANTITY / MEASURE TALLY",
    4: "TERMINAL VERIFICATION SINK / CONSIGNMENT SEAL",
}

MOTIF_GUILD_MAPPING = {
    "unicorn": "Unicorn Administrative / Imperial Bureau",
    "bull": "Bovid Agrarian / Commercial Guild",
    "elephant": "High-Echelon Royal / Maritime Guild",
    "tiger": "Forestry / Resource Extraction Office",
    "rhinoceros": "Wetland / Frontier Regional Guild",
    "gaur": "Highland Bovid Trading Office",
    "aniconic": "Direct Bureaucratic Voucher (No Heraldic Emblem)",
}


@dataclass(frozen=True, slots=True)
class SignAnnotation:
    position: int
    sign_parpola: str
    sign_mahadevan: str
    sign_wells: str
    root: str
    modifier: str
    syntactic_class: int
    slot_role: str
    description: str


@dataclass(frozen=True, slots=True)
class ClausalGloss:
    clause_index: int
    start_pos: int
    end_pos: int
    is_dag_monotonic: bool
    signs: tuple[SignAnnotation, ...]
    gloss_text: str


@dataclass(frozen=True, slots=True)
class StructuralReading:
    artifact_id: str
    site: str
    medium: str
    animal_motif: str
    guild_context: str
    direction: str
    length: int
    n_clauses: int
    is_fully_compliant: bool
    clauses: tuple[ClausalGloss, ...]
    executive_summary: str


class IndusReader:
    """End-to-end structural parser and reader for Indus Valley script inscriptions."""

    def __init__(
        self,
        corpus: Optional[PanIndusCorpus] = None,
        analyzer: Optional[PanIndusAnalyzer] = None,
    ) -> None:
        self.corpus = corpus or PanIndusCorpus()
        self.analyzer = analyzer or PanIndusAnalyzer(corpus=self.corpus)
        self.engine = CompoundGrammarEngine(analyzer=self.analyzer, corpus=self.corpus)
        self.concordance = self.corpus.concordance
        self.decomposer = LigatureDecomposer()

        # Build lookup table by artifact_id and cisi_id
        self._by_id: dict[str, PanInscription] = {}
        for ins in self.corpus.inscriptions:
            if ins.artifact_id:
                self._by_id[ins.artifact_id.lower()] = ins
            if ins.cisi_id:
                self._by_id[ins.cisi_id.lower()] = ins

    def find_inscription(self, identifier: str) -> Optional[PanInscription]:
        return self._by_id.get(identifier.lower().strip())

    def annotate_sign(self, pos: int, sign_p: str) -> SignAnnotation:
        m_id = self.concordance.parpola_to_mahadevan(sign_p) or "-"
        w_list = self.concordance.get_entry(sign_p)
        w_id = w_list.wells_ids[0] if (w_list and w_list.wells_ids) else "-"

        root, mod, desc = self.decomposer.decompose(sign_p)
        cls = self.analyzer.sign_to_class.get(sign_p, 1)
        role = CLASS_SLOT_DESCRIPTIONS.get(cls, "UNKNOWN SLOT")

        return SignAnnotation(
            position=pos,
            sign_parpola=sign_p,
            sign_mahadevan=m_id,
            sign_wells=w_id,
            root=root,
            modifier=mod,
            syntactic_class=cls,
            slot_role=role,
            description=desc,
        )

    def read_sequence(
        self,
        signs: Sequence[str],
        artifact_id: str = "CUSTOM_INPUT",
        site: str = "Unspecified",
        medium: str = "seal",
        symbol: str = "unicorn",
        direction: str = "R/L",
    ) -> StructuralReading:
        signs_list = list(signs)
        # Normalize signs to Parpola catalog
        p_signs = self.concordance.normalize_sequence(signs_list, target_catalog="parpola")
        classes = self.analyzer.get_class_sequence(p_signs)

        parse: CompoundParseResult = self.engine.parse_inscription(
            classes=classes,
            signs=p_signs,
            artifact_id=artifact_id,
            max_clauses=4,
        )

        # Build annotations
        annotations = [self.annotate_sign(idx, s) for idx, s in enumerate(p_signs)]

        clausal_glosses: list[ClausalGloss] = []
        for part in parse.clauses:
            clause_annos = tuple(annotations[part.start_pos : part.end_pos])

            # Generate natural administrative gloss for this clause
            clause_terms = []
            for a in clause_annos:
                term = f"{a.slot_role} [{a.root}{' + ' + a.modifier if a.modifier != 'BARE' else ''} ({a.sign_parpola})]"
                clause_terms.append(term)

            gloss_str = "  →  ".join(clause_terms)
            clausal_glosses.append(
                ClausalGloss(
                    clause_index=part.clause_index,
                    start_pos=part.start_pos,
                    end_pos=part.end_pos,
                    is_dag_monotonic=part.is_dag_monotonic,
                    signs=clause_annos,
                    gloss_text=gloss_str,
                )
            )

        motif_clean = symbol.lower().strip()
        guild = MOTIF_GUILD_MAPPING.get(motif_clean, f"Guild Emblem: {symbol}")

        # Synthesize executive summary
        summary_lines = [
            f"Administrative Reading for {artifact_id} ({site}, {medium.upper()}, {direction}):",
            f"Authority Sphere: {guild}",
            f"Syntactic Complexity: {parse.n_clauses}-clause formulaic structure ({'Regular Monotonic' if parse.is_compliant else 'Irregular Non-Monotonic'}).",
        ]
        for c in clausal_glosses:
            summary_lines.append(f"  [Clause {c.clause_index + 1}]: {c.gloss_text}")

        return StructuralReading(
            artifact_id=artifact_id,
            site=site,
            medium=medium,
            animal_motif=symbol,
            guild_context=guild,
            direction=direction,
            length=len(p_signs),
            n_clauses=parse.n_clauses,
            is_fully_compliant=parse.is_compliant,
            clauses=tuple(clausal_glosses),
            executive_summary="\n".join(summary_lines),
        )

    def read_artifact(self, identifier: str) -> Optional[StructuralReading]:
        ins = self.find_inscription(identifier)
        if ins is None:
            return None
        return self.read_inscription(ins)

    def read_inscription(self, ins: PanInscription) -> StructuralReading:
        return self.read_sequence(
            signs=ins.signs_parpola,
            artifact_id=ins.artifact_id or ins.cisi_id,
            site=ins.site,
            medium=ins.broad_type,
            symbol=ins.symbol,
            direction=ins.direction,
        )


def format_reading_display(reading: StructuralReading) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append(f"  INDUS EPIGRAPHIC STRUCTURAL READING: {reading.artifact_id}")
    lines.append("=" * 78)
    lines.append(f"Site:        {reading.site:16s}  Medium:    {reading.medium.upper():12s} Direction: {reading.direction}")
    lines.append(f"Emblem:      {reading.animal_motif:16s}  Authority: {reading.guild_context}")
    lines.append(f"Length:      {reading.length} signs{'':10s}  Structure: {reading.n_clauses} Clauses (Compliant={reading.is_fully_compliant})")
    lines.append("-" * 78)

    for c in reading.clauses:
        status = "✓ MONOTONIC" if c.is_dag_monotonic else "⚠ IRREGULAR"
        lines.append(f"\n▶ CLAUSE {c.clause_index + 1} (Positions {c.start_pos}..{c.end_pos - 1}) [{status}]:")
        for a in c.signs:
            lines.append(
                f"  [{a.position}] {a.sign_parpola:5s} | M:{a.sign_mahadevan:5s} | W:{a.sign_wells:5s} | "
                f"Class {a.syntactic_class} | {a.root:7s} ({a.modifier:14s}) -> {a.slot_role}"
            )
        lines.append(f"  GLOSS: {c.gloss_text}")

    lines.append("-" * 78)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Indus Script Epigraphic Structural Reader.")
    parser.add_argument("query", nargs="*", help="Artifact ID (e.g. 144.1, 5.1, M-1) or sign IDs (e.g. P378 P281 P324)")
    parser.add_argument("--site", type=str, default="Unknown", help="Site name for custom signs")
    parser.add_argument("--medium", type=str, default="seal", help="Medium (seal, tablet, tag)")
    parser.add_argument("--symbol", type=str, default="unicorn", help="Animal symbol (unicorn, bull, etc.)")
    args = parser.parse_args()

    reader = IndusReader()

    if not args.query:
        # Default showcase: Dholavira Signboard and Lothal Cargo Tag
        showcase_ids = ["144.1", "5.1"]
        print("[*] No query specified. Running showcase demonstrations on foundational artifacts:\n")
        for a_id in showcase_ids:
            res = reader.read_artifact(a_id)
            if res:
                print(format_reading_display(res))
                print()
        return

    query_str = " ".join(args.query).strip()

    # Check if query is an artifact ID
    reading = reader.read_artifact(query_str)
    if reading is not None:
        print(format_reading_display(reading))
        return

    # Treat as sign list
    tokens = query_str.replace(",", " ").replace("-", " ").split()
    reading = reader.read_sequence(
        signs=tokens,
        artifact_id="CUSTOM_INPUT",
        site=args.site,
        medium=args.medium,
        symbol=args.symbol,
    )
    print(format_reading_display(reading))


if __name__ == "__main__":
    main()
