"""Manifest and dataset integrity enforcement under CipherLab Blind Cryptanalysis Protocol."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


DATASETS_DIR = Path(__file__).parent / "datasets"
BLIND_PATH = DATASETS_DIR / "blind" / "k4_ciphertext.json"
CONTEXTUAL_PATH = DATASETS_DIR / "contextual" / "public_hints.json"
GROUND_TRUTH_PATH = DATASETS_DIR / "ground-truth" / "archival_metadata.json"


def sha256_of_file(path: Path) -> str:
    """Compute SHA-256 hash of a file's raw bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_dataset(path: Path, current_tier: int = 1) -> Dict[str, Any]:
    """Load JSON dataset enforcing tier-based access control."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    access = data.get("access_control", {})
    required_tier = access.get("tier_level", 1)
    
    if current_tier < required_tier:
        raise PermissionError(
            f"Blind Protocol Violation: Agent at Tier {current_tier} attempted to access "
            f"Tier {required_tier} dataset '{data.get('name')}' ({path.name}). "
            f"External hints and ground-truth must remain sealed!"
        )
        
    return data


def generate_datasets_manifest() -> Dict[str, Any]:
    """Generate SHA-256 digest manifest for all Kryptos K4 datasets."""
    manifest = {
        "datasets": {
            "blind": {
                "path": str(BLIND_PATH.relative_to(Path(__file__).parent)),
                "sha256": sha256_of_file(BLIND_PATH),
                "tier": 1,
            },
            "contextual": {
                "path": str(CONTEXTUAL_PATH.relative_to(Path(__file__).parent)),
                "sha256": sha256_of_file(CONTEXTUAL_PATH),
                "tier": 2,
            },
            "ground_truth": {
                "path": str(GROUND_TRUTH_PATH.relative_to(Path(__file__).parent)),
                "sha256": sha256_of_file(GROUND_TRUTH_PATH),
                "tier": 3,
            },
        }
    }
    return manifest


if __name__ == "__main__":
    m = generate_datasets_manifest()
    print("Kryptos K4 Datasets SHA-256 Manifest:")
    print(json.dumps(m, indent=2))
