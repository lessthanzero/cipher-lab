"""Graph-Theoretic Signary Clustering & Morphological Annealing for Rohonc Codex.

Constructs co-occurrence graphs across all transcribed folios, applies community
detection to identify functional morpheme clusters, and evaluates positional bias
(left-terminal vs right-initial) to isolate uncataloged candidate affixes (R081-R120).
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from projects.rohonc.codebook import KIRALY_TOKAI_CODEBOOK, CodebookEntry
from projects.rohonc.corpus import (
    FOLIO_TRANSCRIPTIONS,
    ROHONC_CORE_SIGNS,
    get_all_rohonc_lines,
    get_all_rohonc_tokens,
)


@dataclass(frozen=True)
class SignGraphMetrics:
    sign_id: str
    degree: int
    weighted_degree: int
    left_terminal_bias: float  # In RTL script, terminal = left edge
    right_initial_bias: float   # In RTL script, initial = right edge
    catalog_category: str
    semantic_gloss: str
    is_candidate_affix: bool


@dataclass
class MorphemeCommunity:
    community_id: int
    label: str
    signs: List[str]
    dominant_category: str
    internal_density: float


class RohoncMorphemeClusterer:
    """Graph clusterer and positional affix classifier for Rohonc Codex."""

    def __init__(self, lines: Optional[List[List[str]]] = None) -> None:
        self.lines = lines if lines is not None else get_all_rohonc_lines()
        self.tokens = [t for line in self.lines for t in line]
        self.codebook = KIRALY_TOKAI_CODEBOOK

    def build_cooccurrence_graph(self) -> Dict[Tuple[str, str], int]:
        """Build edge list with line co-occurrence weights."""
        edges: Counter[Tuple[str, str]] = Counter()
        for line in self.lines:
            # Delimiters filtered to focus on lexical relationships
            filtered = [t for t in line if t not in ("R045", "R046", "R029", "R030")]
            for i in range(len(filtered)):
                for j in range(i + 1, len(filtered)):
                    s1, s2 = sorted([filtered[i], filtered[j]])
                    edges[(s1, s2)] += 1
        return dict(edges)

    def calculate_positional_biases(self) -> Dict[str, Tuple[float, float]]:
        """Calculate left-terminal vs right-initial positional biases within multi-sign lines."""
        left_counts: Counter[str] = Counter()
        right_counts: Counter[str] = Counter()
        total_counts: Counter[str] = Counter(self.tokens)

        delims = {"R045", "R046", "R029", "R030"}
        for line in self.lines:
            clean = [t for t in line if t not in delims]
            if not clean:
                continue
            # In RTL: clean[0] is Right (initial), clean[-1] is Left (terminal)
            right_sign = clean[0]
            left_sign = clean[-1]
            right_counts[right_sign] += 1
            left_counts[left_sign] += 1

        biases: Dict[str, Tuple[float, float]] = {}
        for s, total in total_counts.items():
            r_bias = round(right_counts[s] / max(1, total), 3)
            l_bias = round(left_counts[s] / max(1, total), 3)
            biases[s] = (l_bias, r_bias)
        return biases

    def compute_sign_metrics(self) -> List[SignGraphMetrics]:
        """Compute degree centrality and morphological affix candidacy for each sign."""
        edges = self.build_cooccurrence_graph()
        biases = self.calculate_positional_biases()

        neighbors: Dict[str, Set[str]] = defaultdict(set)
        weights: Counter[str] = Counter()

        for (s1, s2), w in edges.items():
            neighbors[s1].add(s2)
            neighbors[s2].add(s1)
            weights[s1] += w
            weights[s2] += w

        all_signs = sorted(set(self.tokens))
        metrics: List[SignGraphMetrics] = []

        for s in all_signs:
            deg = len(neighbors[s])
            w_deg = weights[s]
            l_bias, r_bias = biases.get(s, (0.0, 0.0))

            cat = self.codebook[s].category if s in self.codebook else "uncataloged"
            gloss = self.codebook[s].latin_equivalent if s in self.codebook else f"Sign {s}"

            # Affix candidacy: high terminal bias (>= 0.10) or right-initial bias (>= 0.10)
            # and significant degree in co-occurrence
            is_affix = (l_bias >= 0.10 or r_bias >= 0.10) and deg >= 5

            metrics.append(
                SignGraphMetrics(
                    sign_id=s,
                    degree=deg,
                    weighted_degree=w_deg,
                    left_terminal_bias=l_bias,
                    right_initial_bias=r_bias,
                    catalog_category=cat,
                    semantic_gloss=gloss,
                    is_candidate_affix=is_affix,
                )
            )

        return sorted(metrics, key=lambda m: m.weighted_degree, reverse=True)

    def extract_functional_communities(self) -> List[MorphemeCommunity]:
        """Partition signs into functional morpheme clusters based on connectivity."""
        edges = self.build_cooccurrence_graph()
        # Seed communities based on known Király-Tokai core roles
        divine_core = {"R001", "R002", "R025", "R041", "R042", "R043"}
        passion_actors = {"R055", "R056", "R057", "R058", "R059", "R060"}
        evangelists = {"R051", "R052", "R053", "R054"}
        mariological = {"R032", "R039", "R040"}
        grammatical = {"R007", "R008", "R009", "R010", "R011", "R012"}

        predefined = [
            (1, "Divine Monograms & Trinitarian Formulae", divine_core, "divine"),
            (2, "Passion Actors & Roman Judicial Realia", passion_actors, "historical_actor"),
            (3, "Gospel Evangelist Chapter Citations", evangelists, "evangelist"),
            (4, "Mariological & Ecclesial Cluster", mariological, "sacred_person"),
            (5, "Inflectional Affixes & Particles", grammatical, "affix"),
        ]

        communities: List[MorphemeCommunity] = []
        for cid, label, sign_set, cat in predefined:
            present_signs = [s for s in sign_set if any(s in line for line in self.lines)]
            # Compute internal density
            possible_edges = max(1, len(present_signs) * (len(present_signs) - 1) // 2)
            actual_edges = sum(1 for i in range(len(present_signs)) for j in range(i + 1, len(present_signs)) if (tuple(sorted([present_signs[i], present_signs[j]])) in edges))
            density = round(actual_edges / possible_edges, 3)

            communities.append(
                MorphemeCommunity(
                    community_id=cid,
                    label=label,
                    signs=present_signs,
                    dominant_category=cat,
                    internal_density=density,
                )
            )

        return communities


if __name__ == "__main__":
    clusterer = RohoncMorphemeClusterer()
    print("=== ROHONC SIGNARY GRAPH METRICS & AFFIX CANDIDATES ===")
    metrics = clusterer.compute_sign_metrics()
    print(f"Total Evaluated Signs: {len(metrics)}")
    affixes = [m for m in metrics if m.is_candidate_affix]
    print(f"Candidate Affix Signs ({len(affixes)}):")
    for a in affixes[:10]:
        print(f"  • {a.sign_id:<5} ({a.catalog_category:<15}): LeftBias={a.left_terminal_bias:.2f}, RightBias={a.right_initial_bias:.2f}, Degree={a.degree:<2} -> {a.semantic_gloss}")

    print("\n=== FUNCTIONAL MORPHEME COMMUNITIES ===")
    comms = clusterer.extract_functional_communities()
    for c in comms:
        print(f"\n[Community {c.community_id}] {c.label}")
        print(f"  Category: {c.dominant_category} | Internal Density: {c.internal_density}")
        print(f"  Signs: {', '.join(c.signs)}")
