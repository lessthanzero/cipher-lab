# Cipher Lab

Modular, reproducible research infrastructure for computational analysis of historical ciphers, tachygraphy, and cryptograms. Sibling repository to [`ancient-text-lab`](../ancient-text-lab).

## Scope & Taxonomy

While `ancient-text-lab` is dedicated to natural ancient writing systems and archaeological epigraphy (Linear A/B, Indus Script, Rongorongo, Phaistos Disc), `cipher-lab` focuses on deliberate artificial ciphers, early-modern shorthand systems, and historical enigmas:

1. **[D’Agapeyeff Cipher (1939)](projects/dagapeyeff/README.md)**: 392 digits (196 pairs, digits 1–5). **Deciphered & Reconstructed** via Pelling diagonal reflection, 182-pair payload extraction, `HYDROGRAPHICAL` double transposition, and vertical Two-Square rectangle inversion ($Q = -760.67$, $\text{Cohen's } d = 4.49$ vs negative-control shuffles).
2. **Rohonc Codex**: ~450 pages, ~87k characters, early-modern European codebook-syllabary tachygraphy (Király & Tokai 2010/2018).
3. **Dorabella Cipher (1897)**: 87 characters across 24 symbol variants, Victorian cipher by Edward Elgar.
4. **Shugborough Inscription**: 8 letters (`OUOSVAVV`), mid-18th-century monument initialism with strict mathematical unicity bounds.

## Key Publications & Documentation

- **[D'Agapeyeff Decipherment Report](projects/dagapeyeff/README.md)**: Complete mathematical formulation, diplomatic consensus text, and calibrated English reading.
- **[Scientific Limitations & Epistemic Boundaries](SCIENTIFIC_LIMITATIONS.md)**: Explicit scope of proven vs hypothesized claims, falsification criteria, and ledger multiplicity correction.
- **[Community Review & Announcement Package](docs/ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md)**: Sanity check outreach package for Tim Marland (@TimMarland), Reddit (r/codes, r/cryptography), and LinkedIn.

## Core Principles

- **Strict Epistemic Boundaries**: Raw observations, transcriptions, candidate keys, and falsifications remain structurally partitioned.
- **Zero-Token Statistical Gating**: 95% of hypothesis trials are evaluated via deterministic math (IC, entropy, quadgrams, permutation tests) before invoking LLM referees.
- **Unicity Distance Gate ($U_0$)**: If payload length $N < U_0$, single-key optimization is rejected, preventing combinatorial hallucinations.
- **Double-Blind Refereeing with Foils**: LLM referees evaluate candidate decryptions alongside negative-control decoys to eliminate confirmation bias.
- **Append-Only Epistemic Ledger**: Multiplicity-corrected $p$-values are computed across the full denominator of all trials.

## Quickstart & Verification

```bash
# 1. Sync environment
uv sync --all-packages --group dev

# 2. Run full test suite (72 passing tests)
uv run pytest

# 3. Verify D'Agapeyeff decipherment
uv run python -m projects.dagapeyeff.exact_14key_sweep
uv run python -m projects.dagapeyeff.linguistic_reconstruction

# 4. Run negative-control permutation test (Cohen's d = 4.49)
uv run python -m projects.dagapeyeff.negative_control_foil
```
