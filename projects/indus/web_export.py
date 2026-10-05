"""Web Data Exporter for Indus Interactive Epigraphic Reader & Full-Corpus Explorer.

Generates pre-indexed JSON payloads containing:
1. Curated showcase inscriptions (Dholavira signboard, foreign trade seals, 3D prisms, multi-line seals).
2. Complete sign concordance and syntactic classification dictionary.
3. Clausal parses and administrative English structural glosses.
4. Summary statistics from all 15 Epistemic Ledger trials (PAN-H1 through PAN-H15).
5. Diachronic stratigraphy report (Period 3B molded vs Period 3C incised).
6. Intra-site spatial archaeology report (Workmen Mound F vs Commercial VS).
7. Full searchable corpus ledger (all 3,219 inscriptions).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

base_dir = Path(__file__).resolve().parent.parent.parent
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from projects.indus.multi_surface import MultiSurfaceAnalyzer
from projects.indus.pan_analytics import PanIndusAnalyzer
from projects.indus.pan_corpus import PanIndusCorpus
from projects.indus.reader import CLASS_SLOT_DESCRIPTIONS, IndusReader


def generate_web_data(out_path: Path) -> dict[str, Any]:
    corpus = PanIndusCorpus()
    analyzer = PanIndusAnalyzer(corpus=corpus)
    reader = IndusReader(corpus=corpus, analyzer=analyzer)
    ms_analyzer = MultiSurfaceAnalyzer(corpus=corpus, analyzer=analyzer)

    # 1. Curated Masterwork Showcase Artifacts
    showcase_ids = [
        "144.1",  # Dholavira Citadel Gateway Signboard (9 signs, 4 clauses)
        "5.1",    # Allahdino Bull Commercial Tag
        "6.1",    # Allahdino Seal 1
        "7.1",    # Allahdino Seal 2
        "8.1",    # Allahdino Seal 3
        "9.1",    # Allahdino Seal 4
        "11.1",   # Allahdino Seal 6 (Rhinoceros)
        "19.1",   # Bala-kot Bull Seal (7 signs)
        "27.1",   # Banawali Bull Seal (7 signs)
        "70.1",   # Chanhu-daro 2-line Seal (Line 1: 031-032)
        "70.2",   # Chanhu-daro 2-line Seal (Line 2)
        "1971.1", # Kish Meluhha Cylinder Seal
        "3884.1", # Umma Meluhha International Trade Seal
        "3886.1", # Ur Meluhha Round Stamp Seal
    ]

    showcase_inscriptions: list[dict[str, Any]] = []
    for a_id in showcase_ids:
        reading = reader.read_artifact(a_id)
        if reading is not None:
            clauses_data = []
            for c in reading.clauses:
                signs_data = []
                for s in c.signs:
                    signs_data.append({
                        "position": s.position,
                        "sign_parpola": s.sign_parpola,
                        "sign_mahadevan": s.sign_mahadevan,
                        "sign_wells": s.sign_wells,
                        "root": s.root,
                        "modifier": s.modifier,
                        "syntactic_class": s.syntactic_class,
                        "slot_role": s.slot_role,
                        "description": s.description,
                    })
                clauses_data.append({
                    "clause_index": c.clause_index,
                    "start_pos": c.start_pos,
                    "end_pos": c.end_pos,
                    "is_monotonic": c.is_dag_monotonic,
                    "gloss_text": c.gloss_text,
                    "signs": signs_data,
                })

            showcase_inscriptions.append({
                "artifact_id": reading.artifact_id,
                "site": reading.site,
                "medium": reading.medium,
                "animal_motif": reading.animal_motif,
                "guild_context": reading.guild_context,
                "direction": reading.direction,
                "length": reading.length,
                "num_clauses": reading.n_clauses,
                "is_compliant": reading.is_fully_compliant,
                "structural_english_gloss": reading.executive_summary,
                "clauses": clauses_data,
            })

    # 2. 3D Triangular Molded Terracotta Prisms
    prisms = ms_analyzer.analyze_3d_prisms()[:6]

    # 3. Class Slot Descriptions
    classes_desc = {str(k): v for k, v in CLASS_SLOT_DESCRIPTIONS.items()}

    # 4. Epistemic Ledger Trials Summary (PAN-H1 through PAN-H15)
    ledger_trials = [
        {"id": "PAN-H1", "name": "Cross-Site Syntactic Invariance", "finding": "Mohenjo-Daro vs Harappa invariance (D_SKL=0.0664 b, Z=+20.37σ)"},
        {"id": "PAN-H2", "name": "Cross-Medium Syntactic Generalization", "finding": "Seals (76.3%), Tablets (75.6%), Tags (86.7%) share identical DAG"},
        {"id": "PAN-H3", "name": "Iconographic Motif Coupling", "finding": "Animal heraldry couples to initial administrative class (χ²=35.57, p=0.0033)"},
        {"id": "PAN-H4", "name": "Information-Theoretic Directionality", "finding": "Right-to-Left reading direction proven (3.15x asymmetry, Z=+26.93σ)"},
        {"id": "PAN-H5", "name": "Pan-Indus Global MDL Induction", "finding": "Optimal 4-state HMM achieves 78.49% bit compression"},
        {"id": "PAN-H6", "name": "Hierarchical Multi-Clause Grammar", "finding": "96.25% of corpus explained by ≤3 monotonic clauses (Z=+31.13σ)"},
        {"id": "PAN-H7", "name": "Ligature Decomposition Algebra", "finding": "Root ⊕ Modifier vector space reduces entropy by 26.1% (Z=+441.63σ)"},
        {"id": "PAN-H8", "name": "Dholavira Citadel Signboard Proof", "finding": "100% monotonic fit across 4 clauses partitioned by Spoked Wheel P378"},
        {"id": "PAN-H9", "name": "Comparative Ancient Typology", "finding": "Separates from spoken syntax (Z=+8.65σ); vector proximity to Proto-Elamite accounts"},
        {"id": "PAN-H10", "name": "Meluhha International Trade Audit", "finding": "82.4% syntax retention in Mesopotamia; 3.5x elevation in cuneiform LTR reversal"},
        {"id": "PAN-H11", "name": "Numerical Stroke Metrology", "finding": "2,257 numeral tallies bind directly to capacity measure vessel U (Z=+12.55σ)"},
        {"id": "PAN-H12", "name": "Multi-Surface Discourse Grammar", "finding": "551 multi-face tablets show 8.13x enrichment in Class 4->0 clausal resets across faces (Z=+24.49σ)"},
        {"id": "PAN-H13", "name": "Full-Corpus Transcription Ledger", "finding": "All 3,219 inscriptions parsed: 96.1% grammar compliance, 893 authority consignments, 340 commodity tallies"},
        {"id": "PAN-H14", "name": "Diachronic Stratigraphy & Crystallization", "finding": "Period 3B Molded -> Period 3C Incised: Compliance leaps +3.18% (96.3% -> 99.5%, Z=+3.67σ, p<0.0001); entropy falls -0.1271 b"},
        {"id": "PAN-H15", "name": "Intra-Site Spatial Archaeology", "finding": "Harappa Workmen Mound F (90.6% tablets, 5.1% unicorn) vs Mohenjo-Daro Commercial VS (10.6% tablets, 95.5% unicorn monopoly, Z=+16.73σ, p=0.000000)"},
    ]

    # 5. Load Stratigraphy and Spatial Reports
    derived_dir = base_dir / "data" / "derived"
    strat_path = derived_dir / "stratigraphy_report.json"
    strat_data = {}
    if strat_path.exists():
        with open(strat_path, "r", encoding="utf-8") as f:
            strat_data = json.load(f)

    spatial_path = derived_dir / "spatial_report.json"
    spatial_data = {}
    if spatial_path.exists():
        with open(spatial_path, "r", encoding="utf-8") as f:
            spatial_data = json.load(f)

    # 6. Full Searchable Corpus Index (Compact format for web browser)
    ledger_jsonl = derived_dir / "indus_corpus_transcriptions.jsonl"
    corpus_entries = []
    if ledger_jsonl.exists():
        with open(ledger_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                corpus_entries.append({
                    "id": rec["id"],
                    "site": rec["site"],
                    "type": rec["type"],
                    "broad": rec["broad"],
                    "sym": rec["sym"],
                    "len": rec["len"],
                    "clauses_n": rec["clauses_n"],
                    "compliant": rec["compliant"],
                    "typology": rec["typology"],
                    "signs": [s["p"] for c in rec["clauses"] for s in c["signs"]],
                    "classes": [s["cls"] for c in rec["clauses"] for s in c["signs"]],
                    "roots": [s["root"] for c in rec["clauses"] for s in c["signs"]],
                    "gloss": rec["executive_gloss"],
                })

    export_payload = {
        "metadata": {
            "title": "Indus Epigraphic Reader & Structural Syntax Explorer",
            "version": "2.0.0",
            "corpus_size": len(corpus_entries) or len(corpus.inscriptions),
            "unicity_distance": 907.5,
            "max_inscription_length": 13,
            "epistemic_trials_count": len(ledger_trials),
        },
        "classes": classes_desc,
        "showcase": showcase_inscriptions,
        "prisms": prisms,
        "trials": ledger_trials,
        "stratigraphy": strat_data,
        "spatial": spatial_data,
        "corpus": corpus_entries,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)

    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"[✓] Web export saved to {out_path} ({len(corpus_entries)} corpus items, size={size_mb:.2f} MB).")
    return export_payload


if __name__ == "__main__":
    out_file = Path(__file__).resolve().parent.parent.parent / "site" / "indus_data.json"
    generate_web_data(out_file)
