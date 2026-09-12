"""OpenAI GPT-6 Astra Advisor for D'Agapeyeff Cipher.

Feeds deep historical, biographical, and cryptanalytic context to GPT-6 Astra 
via codex-cli to generate seed keywords, cribs, and transposition hypotheses.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, Optional

DAGAPEYEFF_SYSTEM_PROMPT = """You are an elite cryptanalytic advisor specializing in WWII-era historical ciphers, 
Slavic linguistic interference, Russian Nihilist ciphers, and British SOE operational security."""

DAGAPEYEFF_CONTEXT = """
TARGET: The D'Agapeyeff Cipher (1939, published in 'Codes and Ciphers' by Alexander D'Agapeyeff, page 144).
TOTAL LENGTH: 395 digits printed; last 3 digits '000' are padding; payload is 392 digits (196 two-digit pairs).

AUTHOR BACKGROUND:
- Alexander D'Agapeyeff (Russian: Александр Агапеев / Д'Агапеев, born May 20, 1900/1902 in Russia, died 1969 UK).
- Civilian cartographer and patent draughtsman in London.
- Served as camouflage and codes instructor in British intelligence (SOE dossier HS 9/9/5).
- In 'Codes and Ciphers', his worked example of double columnar transposition is explicitly a Russian Nihilist cipher using keyword 'SCHUVALOF' (Count Peter Shuvalov / граф Пётр Шувалов).
- D'Agapeyeff exhibited two clerical errors in his own worked example:
  1. German/idiosyncratic transliteration of Russian (SCH for Ш, terminal F for В).
  2. Errors in numerical letter ranking of the transposition key.

STATE-OF-THE-ART EMPIRICAL FINDINGS (Tim Marland, dagapeyeffresearch.com, March 2026):
1. Pair Structure: Digits strictly alternate row digits in {6,7,8,9,0} and column digits in {1,2,3,4,5}.
   Transposition MUST operate on 196 pairs (14x14 grid), NEVER individual digits.
2. Reversed Kerckhoffs: D'Agapeyeff copied Auguste Kerckhoffs' 1883 'La Cryptographie Militaire', but swapped encryption/decryption instructions.
3. 14th Column Nulls: Arranged as 14x14, the 5 rarest symbols cluster in column 14. Removing col 14 yields a 14x13 (182 pairs) grid.
4. Position 97 Anomaly: Pair 97 is '04'. Modifying '04' -> '75' drops chi-squared from 21.6 to 18.2.
5. Benchmark to beat: Tim Marland's SOTA project record Q = -692.13.

TASK:
Propose targeted cryptanalytic hypotheses to seed a joint simulated annealing optimizer (which searches the 14-column transposition and 5x5 Polybius square simultaneously).

Respond in valid JSON:
{
  "hypotheses_summary": "Short 2-sentence rationale based on author background",
  "seed_polybius_keywords": [
    "KEYWORD1", "KEYWORD2", ... (at least 8 keywords: Russian transliterated, French cartographic, or 1939 British SOE terms)
  ],
  "candidate_cribs": [
    "CRIB1", "CRIB2", ... (short Russian transliterated or English phrases likely to appear in 1939 map/military plaintexts)
  ],
  "structural_suggestions": [
    "suggestion 1", "suggestion 2"
  ]
}
"""


def query_astra_advisor(
    prompt: Optional[str] = None,
    model: str = "gpt-6-astra",
    timeout_secs: float = 60.0,
) -> Dict[str, Any]:
    """Query OpenAI GPT-6 Astra via codex exec to get hypothesis recommendations."""
    codex_bin = shutil.which("codex") or "/opt/homebrew/bin/codex"
    if not codex_bin or not os.path.exists(codex_bin):
        print("[!] codex-cli binary not found, using rule-based fallback seeds.")
        return _fallback_seeds()

    full_prompt = f"{DAGAPEYEFF_SYSTEM_PROMPT}\n\n{DAGAPEYEFF_CONTEXT}"
    if prompt:
        full_prompt += f"\n\nADDITIONAL USER INQUIRY:\n{prompt}"
    full_prompt += "\n\nRespond with valid JSON only."

    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as out_file:
        out_path = out_file.name

    cmd = [
        codex_bin,
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "-c",
        'model_reasoning_effort="low"',
        "-m",
        model,
        "-o",
        out_path,
        full_prompt,
    ]

    try:
        subprocess.run(
            cmd,
            input="",
            capture_output=True,
            text=True,
            timeout=timeout_secs,
        )
        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            # Clean up temp file
            try:
                os.remove(out_path)
            except OSError:
                pass

            if "{" in raw and "}" in raw:
                json_str = raw[raw.find("{") : raw.rfind("}") + 1]
                data = json.loads(json_str)
                return data
    except Exception as e:
        print(f"[*] Failed to query GPT-6 Astra: {e}")
        if os.path.exists(out_path):
            try:
                os.remove(out_path)
            except OSError:
                pass

    return _fallback_seeds()


def query_astra_cartographic_nihilist(
    model: str = "gpt-6-astra",
    timeout_secs: float = 60.0,
) -> Dict[str, Any]:
    """Query OpenAI GPT-6 Astra specifically focusing on the NIHILIST and 1939 Ordnance Survey hypothesis."""
    prompt = """
SPECIFIC OBSERVATION & INQUIRY:
In our computational discovery run on the 14x13 stripped grid (182 pairs), a top candidate decryption produced the string:
"...SOATERNIHLLRL..."
The researcher noticed that 'NIHLL' is phonetically and orthographically very close to 'NIHIL' / 'NIHILIST'.
In 'Codes and Ciphers' (1939), Alexander D'Agapeyeff explicitly introduces the Russian Nihilist cipher immediately alongside the challenge cipher, using a worked example of Count Peter Shuvalov ('SCHUVALOF').
Simultaneously, D'Agapeyeff was a professional cartographer writing 'Maps' (Oxford University Press) discussing the 1939 British Ordnance Survey Retriangulation (Martin Hotine), Cassini projection, trig points, and grid references.

QUESTIONS FOR ASTRA:
1. Could 'NIHILIST' or 'NIHIL' serve as a key, preamble, or indicator word in this cipher?
2. What are the most probable 1939 British Ordnance Survey coordinate phrases, sheet notations, or map scale formulas?
3. Propose 10-15 targeted compound keywords and crib phrases combining 'NIHILIST' and 1939 British cartography for a 2-hour simulated annealing run on the 14x13 grid.

Respond in valid JSON:
{
  "nihilist_analysis": "Assessment of NIHLL / Nihilist connection",
  "seed_polybius_keywords": [
    "NIHILIST", "ORDNANCESURVEY", ... (12-16 keywords)
  ],
  "candidate_cribs": [
    "CRIB1", "CRIB2", ... (10-15 authentic cartographic & Nihilist crib phrases)
  ],
  "structural_suggestions": [
    "suggestion 1", "suggestion 2"
  ]
}
"""
    return query_astra_advisor(prompt=prompt, model=model, timeout_secs=timeout_secs)


def _fallback_seeds() -> Dict[str, Any]:
    """Deterministic fallback seeds if Astra is offline or times out."""
    return {
        "hypotheses_summary": "Fallback seeds derived from D'Agapeyeff's worked example and Russian cartographic origin.",
        "seed_polybius_keywords": [
            "NIHILIST", "NIHIL", "SCHUVALOF", "SCHUWALOW", "ORDNANCESURVEY",
            "RETRIANGULATION", "CASSINI", "TRIGPOINT", "BENCHMARK",
            "KARTOGRAFIYA", "TOPOGRAFIYA", "AGAPEYEFF", "ROSSIYA",
            "MAPSECTION", "TRIANGULATION", "COUNTRYSIDE",
        ],
        "candidate_cribs": [
            "NIHILIST", "ORDNANCE SURVEY", "RETRIANGULATION", "ONE INCH MAP",
            "SHEET NUMBER", "GRID REFERENCE", "CONTOUR LINES", "TRUE NORTH",
            "MAGNETIC NORTH", "DEGREES MINUTES", "SCALE OF MAP",
        ],
        "structural_suggestions": [
            "Test 14th column removal (182 pairs) with NIHILIST / ORDNANCESURVEY keyword alphabet.",
            "Apply lexical bonus for Ordnance Survey and Nihilist vocabulary roots.",
        ],
    }
