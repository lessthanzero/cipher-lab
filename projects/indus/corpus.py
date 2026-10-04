"""Indus Script and comparative control corpus loader and synthesizer."""

from __future__ import annotations

import collections
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Counter, Dict, List, Optional, Sequence

from projects.indus.concordance import IndusConcordance


@dataclass(frozen=True, slots=True)
class IndusInscription:
    id: str
    description: str
    signs: tuple[str, ...]
    sign_count: int
    source_code: str


class IndusCorpus:
    """Manages the Indus epigraphic dataset and comparative control corpora."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "indus"
        
        self.data_dir = Path(data_dir)
        self.concordance = IndusConcordance(self.data_dir / "sign_concordance.json")
        self.inscriptions: list[IndusInscription] = []
        self._linear_a_sequences: list[list[str]] = []
        self._load_data()

    def _load_data(self) -> None:
        inscriptions_file = self.data_dir / "mohenjodaro_cisi_inscriptions.json"
        if not inscriptions_file.exists():
            raise FileNotFoundError(f"Inscriptions file missing: {inscriptions_file}")

        with open(inscriptions_file, "r", encoding="utf-8") as f:
            raw_list = json.load(f)

        self.inscriptions = [
            IndusInscription(
                id=item["id"],
                description=item.get("description", ""),
                signs=tuple(item["signs"]),
                sign_count=item.get("sign_count", len(item["signs"])),
                source_code=item.get("source_code", "CISI_MAYIG"),
            )
            for item in raw_list
        ]

        linear_a_file = self.data_dir / "linear_a_control.json"
        if linear_a_file.exists():
            with open(linear_a_file, "r", encoding="utf-8") as f:
                self._linear_a_sequences = json.load(f)

    def get_sequences(self, target_catalog: str = "parpola") -> list[list[str]]:
        """Return list of sign sequences normalized to the requested catalog."""
        target = target_catalog.lower()
        if target == "parpola":
            return [list(ins.signs) for ins in self.inscriptions]
        return [self.concordance.normalize_sequence(ins.signs, target_catalog=target) for ins in self.inscriptions]

    def get_token_frequencies(self, target_catalog: str = "parpola") -> Counter[str]:
        """Return global sign occurrence counts."""
        freq: Counter[str] = collections.Counter()
        for seq in self.get_sequences(target_catalog=target_catalog):
            freq.update(seq)
        return freq

    def get_positional_distributions(self, target_catalog: str = "parpola") -> dict[int, Counter[str]]:
        """Return sign frequency distribution per positional slot (0-indexed)."""
        pos_dist: dict[int, Counter[str]] = collections.defaultdict(collections.Counter)
        for seq in self.get_sequences(target_catalog=target_catalog):
            for idx, sign in enumerate(seq):
                pos_dist[idx][sign] += 1
        return dict(pos_dist)

    def get_linear_a_control(self) -> list[list[str]]:
        """Return Minoan Linear A administrative tag sign sequences."""
        return [list(seq) for seq in self._linear_a_sequences]

    def generate_sproat_heraldic_control(
        self,
        n_samples: int = 179,
        seed: int = 42,
    ) -> list[list[str]]:
        """Synthesize non-linguistic structured sequences modeled on Sproat's heraldic / deity rules.
        
        Sproat (2010) demonstrated that non-linguistic symbol systems with rigid syntactic slots
        (e.g., Field + Ordinary + Charge + Cadency mark) and power-law sign frequencies produce
        entropy profiles identical to natural language.
        """
        rng = random.Random(seed)
        
        # 4 syntactic tiers
        fields = [f"FIELD_{i}" for i in range(1, 15)]
        ordinaries = [f"ORD_{i}" for i in range(1, 30)]
        charges = [f"CHARGE_{i}" for i in range(1, 100)]
        cadencies = [f"CADENCY_{i}" for i in range(1, 10)]

        # Power-law sampling weights
        w_fields = [1.0 / (i ** 1.1) for i in range(1, len(fields) + 1)]
        w_ord = [1.0 / (i ** 1.1) for i in range(1, len(ordinaries) + 1)]
        w_charges = [1.0 / (i ** 1.1) for i in range(1, len(charges) + 1)]
        w_cad = [1.0 / (i ** 1.1) for i in range(1, len(cadencies) + 1)]

        sequences: list[list[str]] = []
        for _ in range(n_samples):
            # Sequence length 3 to 7 (mean ~ 4.6)
            seq: list[str] = [
                rng.choices(fields, weights=w_fields)[0],
                rng.choices(ordinaries, weights=w_ord)[0],
                rng.choices(charges, weights=w_charges)[0],
            ]
            if rng.random() > 0.4:
                seq.append(rng.choices(charges, weights=w_charges)[0])
            if rng.random() > 0.6:
                seq.append(rng.choices(cadencies, weights=w_cad)[0])
            if rng.random() > 0.8:
                seq.append(rng.choices(ordinaries, weights=w_ord)[0])
            sequences.append(seq)
        return sequences

    def generate_meluhha_cargo_tag_control(
        self,
        n_samples: int = 179,
        seed: int = 42,
    ) -> list[list[str]]:
        """Synthesize non-linguistic cargo-tag barcode sequences (Venugopal 2026 / Kriger & Hunt 2026).
        
        Slots:
        Slot 0: Merchant/Lineage emblem (constrained boundary)
        Slot 1: Commodity class
        Slot 2: Weight standard / Numeral stroke
        Slot 3: Destination / Administrative terminal seal (e.g. Terminal Jar)
        """
        rng = random.Random(seed)

        issuers = [f"ISSUER_{i:02d}" for i in range(1, 25)]
        commodities = [f"COMM_{i:03d}" for i in range(1, 80)]
        numerals = ["NUM_1", "NUM_2", "NUM_3", "NUM_4", "NUM_6", "NUM_8", "NUM_10"]
        numeral_weights = [15, 67, 10, 5, 2, 1, 1]  # '2' accounts for majority in Mohenjo-Daro
        terminals = [f"TERM_{i}" for i in range(1, 10)]
        term_weights = [70, 10, 5, 4, 3, 3, 2, 2, 1]  # Extreme terminal concentration (like M342)

        sequences: list[list[str]] = []
        for _ in range(n_samples):
            seq = [
                rng.choice(issuers),
                rng.choice(commodities),
            ]
            if rng.random() > 0.3:
                seq.append(rng.choice(commodities))
            seq.append(rng.choices(numerals, weights=numeral_weights)[0])
            seq.append(rng.choices(terminals, weights=term_weights)[0])
            sequences.append(seq)
        return sequences

    def get_summary(self, target_catalog: str = "parpola") -> dict[str, float | int]:
        """Compute headline descriptive statistics for the active corpus."""
        seqs = self.get_sequences(target_catalog=target_catalog)
        n_texts = len(seqs)
        total_tokens = sum(len(s) for s in seqs)
        mean_len = total_tokens / max(n_texts, 1)
        freq = self.get_token_frequencies(target_catalog=target_catalog)
        n_types = len(freq)
        singletons = sum(1 for c in freq.values() if c == 1)

        return {
            "inscription_count": n_texts,
            "total_tokens": total_tokens,
            "signary_types": n_types,
            "mean_length": round(mean_len, 2),
            "max_length": max(len(s) for s in seqs) if seqs else 0,
            "min_length": min(len(s) for s in seqs) if seqs else 0,
            "singletons_hapax": singletons,
            "singleton_ratio": round(singletons / max(n_types, 1), 4),
        }
