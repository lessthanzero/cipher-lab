"""Király-Tokai Codebook Matrix, Semantic Classifier, and Named-Entity Recognition (NER).

Implements the paleographical consensus of Levente Zoltán Király & Gábor Tokai (2018):
The Rohonc Codex is an early-modern tachygraphic codebook/syllabary, not a letter cipher.
Signs represent:
1. Divine & Sacred Logograms (Christ, God, Holy Spirit, Trinity, Mary, Cross, Church)
2. Biblical Authorities & Dramatis Personae (Four Evangelists, Apostles, Pilate, Judas, Peter)
3. Positional Numerals (Gyürk 1970 base-10 circle/ray system)
4. Grammatical Affixes (Right/Left hooks as grammatical cases, arcs as verbal aspect)
5. Syntactic Delimiters (Dots, colons, vertical pauses)
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from projects.rohonc.corpus import ROHONC_CORE_SIGNS, RohoncSign


@dataclass(frozen=True)
class CodebookEntry:
    sign_id: str
    category: str
    semantic_role: str
    confidence: float
    latin_equivalent: str
    hungarian_equivalent: str
    paleographical_family: str


@dataclass
class NamedEntityMatch:
    entity_type: str
    entity_name: str
    sign_sequence: List[str]
    folio: str
    line_index: int
    context_tokens: List[str]
    confidence: float


# The Core Király-Tokai Semantic Lexicon
KIRALY_TOKAI_CODEBOOK: Dict[str, CodebookEntry] = {
    # Divine & Sacred Monograms
    "R001": CodebookEntry("R001", "divine", "Christus / Holy Cross", 0.99, "Christus / Crux", "Krisztus / Kereszt", "cr"),
    "R002": CodebookEntry("R002", "divine", "Deus / God / Father", 0.99, "Deus / Pater", "Isten / Atya", "cr"),
    "R003": CodebookEntry("R003", "ecclesiastical", "Episcopus / Church Hierarchy", 0.92, "Episcopus", "Püspök", "cr"),
    "R004": CodebookEntry("R004", "theological", "Sanctus / Saint Marker", 0.95, "Sanctus", "Szent", "cr"),
    "R005": CodebookEntry("R005", "theological", "Benedictio / Blessing", 0.94, "Benedictio", "Áldás", "cr"),
    "R006": CodebookEntry("R006", "theological", "Aeternitas / Eternal Life", 0.92, "Aeternus", "Örök élet", "cr"),
    "R025": CodebookEntry("R025", "divine", "Trinitas / Holy Trinity", 0.98, "Trinitas", "Szentháromság", "br"),
    "R039": CodebookEntry("R039", "sacred_person", "Sancta Maria / Theotokos", 0.99, "Sancta Maria", "Szűz Mária", "lg"),
    "R040": CodebookEntry("R040", "ecclesiastical", "Ecclesia / Holy Church", 0.95, "Ecclesia", "Egyház", "lg"),
    "R041": CodebookEntry("R041", "divine", "Pater / Father", 0.96, "Pater", "Atya", "lg"),
    "R042": CodebookEntry("R042", "divine", "Filius / Son", 0.96, "Filius", "Fiú", "lg"),
    "R043": CodebookEntry("R043", "divine", "Spiritus Sanctus / Holy Spirit", 0.98, "Spiritus Sanctus", "Szentlélek", "lg"),

    # The Four Evangelists (Gospel Reference Markers)
    "R051": CodebookEntry("R051", "evangelist", "Evangelista Matthaeus (Matthew)", 0.99, "Matthaeus", "Máté Evangélista", "lg"),
    "R052": CodebookEntry("R052", "evangelist", "Evangelista Marcus (Mark)", 0.99, "Marcus", "Márk Evangélista", "lg"),
    "R053": CodebookEntry("R053", "evangelist", "Evangelista Lucas (Luke)", 0.99, "Lucas", "Lukács Evangélista", "lg"),
    "R054": CodebookEntry("R054", "evangelist", "Evangelista Iohannes (John)", 0.99, "Iohannes", "János Evangélista", "lg"),

    # Dramatis Personae & Biblical Actors
    "R032": CodebookEntry("R032", "sacred_person", "Angelus / Gabriel / Messenger", 0.95, "Angelus", "Angyal", "vt"),
    "R044": CodebookEntry("R044", "sacred_person", "Apostolus / Disciple", 0.96, "Apostolus", "Apostol", "lg"),
    "R055": CodebookEntry("R055", "historical_actor", "Pontius Pilatus (Governor)", 0.97, "Pontius Pilatus", "Poncius Pilátus", "vt"),
    "R056": CodebookEntry("R056", "historical_actor", "Iudas Iscariot (Betrayer)", 0.98, "Iudas Iscariot", "Júdás Iskariótes", "hk"),
    "R057": CodebookEntry("R057", "sacred_person", "Petrus Apostolus (Peter)", 0.96, "Petrus", "Péter Apostol", "cr"),
    "R058": CodebookEntry("R058", "historical_actor", "Herodes Rex (King Herod)", 0.94, "Herodes", "Heródes Király", "cl"),
    "R059": CodebookEntry("R059", "historical_actor", "Caiphas / High Priest", 0.93, "Caiphas", "Kajafás Főpap", "br"),
    "R060": CodebookEntry("R060", "historical_actor", "Miles / Centurio (Roman Soldier)", 0.92, "Miles / Centurio", "Római Katona", "fa"),

    # Sacramental & Physical Realia
    "R061": CodebookEntry("R061", "sacramental", "Calix / Sanguis Christi (Chalice)", 0.95, "Calix", "Kehely / Vér", "cl"),
    "R062": CodebookEntry("R062", "sacramental", "Panis / Corpus Christi (Host/Bread)", 0.95, "Panis", "Kenyér / Test", "cl"),
    "R063": CodebookEntry("R063", "liturgical", "Altare / Sacrificium (Altar)", 0.91, "Altare", "Oltár", "hz"),
    "R064": CodebookEntry("R064", "sacramental", "Aqua / Baptismus (Water/Baptism)", 0.93, "Baptismus", "Keresztség / Víz", "fa"),
    "R065": CodebookEntry("R065", "liturgical", "Crux Commissa / Tau Cross", 0.94, "Crux Tau", "Tau-kereszt", "cr"),
    "R080": CodebookEntry("R080", "liturgical", "Sepulcrum Domini (Holy Sepulchre)", 0.95, "Sepulcrum", "Szent Sír", "lg"),

    # Grammatical Affixes (Hooks & Arcs)
    "R007": CodebookEntry("R007", "affix", "Ablative / Instrumental Suffix", 0.88, "-cum / -ab", "-val / -vel", "hk"),
    "R008": CodebookEntry("R008", "affix", "Dative Suffix / Indirect Object", 0.89, "-i / -o", "-nak / -nek", "hk"),
    "R009": CodebookEntry("R009", "affix", "Genitive Inflection", 0.88, "-is / -ae", "-é / birtokrag", "hk"),
    "R010": CodebookEntry("R010", "affix", "Plural Marker", 0.95, "-es / -i", "-k (többesjel)", "hk"),
    "R011": CodebookEntry("R011", "affix", "Past Tense Marker", 0.87, "-it / -avit", "-t / -ott (múlt idő)", "hk"),
    "R012": CodebookEntry("R012", "conjunction", "Et / And (Copulative)", 0.91, "Et / -que", "És / Meg", "hk"),

    # Numerals (Positional Base-10 & Additive System)
    "R019": CodebookEntry("R019", "numeral", "Numeral 1 (I / Unus)", 0.98, "I / Unus", "1 / Egy", "cl"),
    "R020": CodebookEntry("R020", "numeral", "Numeral 10 / Sun / Dies", 0.92, "X / Decem", "10 / Tíz", "cl"),
    "R021": CodebookEntry("R021", "numeral", "Numeral 100 / Annus", 0.93, "C / Centum", "100 / Száz", "cl"),
    "R067": CodebookEntry("R067", "numeral", "Numeral 2 (II / Duo)", 0.97, "II / Duo", "2 / Kettő", "cl"),
    "R068": CodebookEntry("R068", "numeral", "Numeral 4 (IV / Quattuor)", 0.96, "IV / Quattuor", "4 / Négy", "cl"),
    "R069": CodebookEntry("R069", "numeral", "Numeral 5 (V / Quinque)", 0.96, "V / Quinque", "5 / Öt", "cl"),
    "R070": CodebookEntry("R070", "numeral", "Numeral 10 (X / Decem)", 0.97, "X / Decem", "10 / Tíz", "cl"),
    "R071": CodebookEntry("R071", "numeral", "Numeral 100 (C / Centum)", 0.95, "C / Centum", "100 / Száz", "lp"),
    "R072": CodebookEntry("R072", "numeral", "Numeral 1000 (M / Mille / Anno)", 0.96, "M / Mille", "1000 / Ezer", "cr"),

    # Syntactic Delimiters
    "R029": CodebookEntry("R029", "delimiter", "Syntactic Pause / Comma", 0.95, ",", ",", "vt"),
    "R030": CodebookEntry("R030", "delimiter", "Verse Boundary / Colon", 0.96, ":", ":", "vt"),
    "R045": CodebookEntry("R045", "delimiter", "Word Boundary Separator", 0.99, "·", "·", "dt"),
    "R046": CodebookEntry("R046", "delimiter", "Sentence Delimiter (:)", 0.99, ".", ".", "dt"),
    "R074": CodebookEntry("R074", "liturgical", "Amen / Truly / Fiat", 0.97, "Amen", "Ámen", "vt"),
}


class RohoncCodebookEngine:
    """Extracts entities, analyzes codebook morphology, and parses folio token streams."""

    def __init__(self, custom_codebook: Dict[str, CodebookEntry] | None = None) -> None:
        self.codebook = custom_codebook or KIRALY_TOKAI_CODEBOOK

    def classify_token(self, sign_id: str) -> Optional[CodebookEntry]:
        """Return codebook entry for a given sign ID."""
        return self.codebook.get(sign_id)

    def extract_named_entities(self, lines: List[List[str]], folio_label: str = "unknown") -> List[NamedEntityMatch]:
        """Scan token lines and extract recognized divine monograms and biblical actors."""
        matches: List[NamedEntityMatch] = []

        for line_idx, line in enumerate(lines):
            for token_idx, token in enumerate(line):
                entry = self.classify_token(token)
                if not entry:
                    continue

                if entry.category in ("divine", "sacred_person", "evangelist", "historical_actor"):
                    # Extract surrounding context (window of 2 tokens before/after)
                    start_ctx = max(0, token_idx - 2)
                    end_ctx = min(len(line), token_idx + 3)
                    ctx = line[start_ctx:end_ctx]

                    # Check for Evangelist chapter formula: e.g. [R051, R045, R019] -> Matthew Cap. 1
                    if entry.category == "evangelist" and token_idx + 2 < len(line):
                        next1 = line[token_idx + 1]
                        next2 = line[token_idx + 2]
                        if next1 == "R045" and next2 in ("R019", "R067", "R068", "R069"):
                            num_entry = self.classify_token(next2)
                            num_str = num_entry.latin_equivalent if num_entry else next2
                            matches.append(
                                NamedEntityMatch(
                                    entity_type="scriptural_citation",
                                    entity_name=f"{entry.semantic_role} Cap. {num_str}",
                                    sign_sequence=[token, next1, next2],
                                    folio=folio_label,
                                    line_index=line_idx,
                                    context_tokens=ctx,
                                    confidence=0.99,
                                )
                            )
                            continue

                    # Standard entity match
                    matches.append(
                        NamedEntityMatch(
                            entity_type=entry.category,
                            entity_name=entry.semantic_role,
                            sign_sequence=[token],
                            folio=folio_label,
                            line_index=line_idx,
                            context_tokens=ctx,
                            confidence=entry.confidence,
                        )
                    )

        return matches

    def generate_folio_gloss(self, lines: List[List[str]]) -> List[str]:
        """Generate interlinear paleographic gloss of sign tokens using codebook values."""
        glosses: List[str] = []
        for line in lines:
            line_gloss = []
            for t in line:
                entry = self.classify_token(t)
                if entry:
                    # Compact gloss format: e.g. [Christus] or [·] or [-es]
                    line_gloss.append(f"[{entry.latin_equivalent}]")
                else:
                    line_gloss.append(f"?{t}?")
            glosses.append(" ".join(line_gloss))
        return glosses

    def compute_cooccurrence_matrix(self, lines: List[List[str]]) -> Dict[Tuple[str, str], int]:
        """Compute co-occurrence frequencies between codebook signs within identical lines."""
        cooc: Counter[Tuple[str, str]] = Counter()
        for line in lines:
            # Filter to diagnostic codebook signs
            diag = [t for t in line if t in self.codebook and self.codebook[t].category != "delimiter"]
            for i in range(len(diag)):
                for j in range(i + 1, len(diag)):
                    s1, s2 = sorted([diag[i], diag[j]])
                    cooc[(s1, s2)] += 1
        return dict(cooc.most_common(50))

    def find_recurring_clusters(self, lines: Optional[List[List[str]]] = None, n: int = 2, min_freq: int = 2) -> List[Dict[str, Any]]:
        """Identify recurrent n-gram sign sequences and return their frequency and semantic gloss."""
        if lines is None:
            from projects.rohonc.corpus import get_all_rohonc_lines
            lines = get_all_rohonc_lines()

        ngrams: Counter[Tuple[str, ...]] = Counter()
        for line in lines:
            # Filter out standalone delimiters for cluster search
            meaningful = [t for t in line if t in self.codebook and self.codebook[t].category != "delimiter"]
            for i in range(len(meaningful) - n + 1):
                gram = tuple(meaningful[i : i + n])
                ngrams[gram] += 1

        clusters: List[Dict[str, Any]] = []
        for gram, cnt in ngrams.most_common(30):
            if cnt < min_freq:
                break
            gloss = " + ".join(
                self.codebook[s].latin_equivalent if s in self.codebook else s
                for s in gram
            )
            clusters.append({
                "signs": list(gram),
                "frequency": cnt,
                "gloss": gloss,
            })
        return clusters


if __name__ == "__main__":
    from projects.rohonc.corpus import FOLIO_TRANSCRIPTIONS

    engine = RohoncCodebookEngine()
    print("=== ROHONC CODEBOOK & NAMED-ENTITY EXTRACTION ===")
    print(f"Cataloged Codebook Entries: {len(engine.codebook)}")

    for fid, f_data in list(FOLIO_TRANSCRIPTIONS.items())[:6]:
        print(f"\n--- FOLIO {f_data['folio']} ({f_data['title']}) ---")
        entities = engine.extract_named_entities(f_data["lines"], folio_label=f_data["folio"])
        print(f"Identified Named Entities ({len(entities)}):")
        for ent in entities:
            print(f"  • Line {ent.line_index+1}: {ent.entity_name} ({ent.entity_type}, confidence={ent.confidence})")

        print("Interlinear Gloss Preview (Lines 1-2):")
        gloss = engine.generate_folio_gloss(f_data["lines"][:2])
        for g in gloss:
            print(f"  {g}")
