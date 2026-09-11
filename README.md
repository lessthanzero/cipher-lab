# Cipher Lab

Modular, reproducible research infrastructure for computational analysis of historical ciphers, tachygraphy, and cryptograms. Sibling repository to [`ancient-text-lab`](../ancient-text-lab).

## Scope & Taxonomy

While `ancient-text-lab` is dedicated to natural ancient writing systems and archaeological epigraphy (Linear A/B, Indus Script, Rongorongo, Phaistos Disc), `cipher-lab` focuses on deliberate artificial ciphers, early-modern shorthand systems, and historical enigmas:

1. **D’Agapeyeff Cipher (1939)**: 392 digits (196 pairs, digits 1–5), likely fractionated/checkerboard with manual encipherment error.
2. **Rohonc Codex**: ~450 pages, ~87k characters, early-modern European codebook-syllabary tachygraphy (Király & Tokai 2010/2018).
3. **Dorabella Cipher (1897)**: 87 characters across 24 symbol variants, Victorian cipher by Edward Elgar.
4. **Shugborough Inscription**: 8 letters (`OUOSVAVV`), mid-18th-century monument initialism with strict mathematical unicity bounds.

## Core Principles

- **Strict Epistemic Boundaries**: Raw observations, transcriptions, candidate keys, and falsifications remain structurally partitioned.
- **Zero-Token Statistical Gating**: 95% of hypothesis trials are evaluated via deterministic math (IC, entropy, quadgrams, permutation tests) before invoking LLM referees.
- **Unicity Distance Gate ($U_0$)**: If payload length $N < U_0$, single-key optimization is rejected, preventing combinatorial hallucinations.
- **Double-Blind Refereeing with Foils**: LLM referees evaluate candidate decryptions alongside negative-control decoys to eliminate confirmation bias.
- **Append-Only Epistemic Ledger**: Multiplicity-corrected $p$-values are computed across the full denominator of all trials.

## Development

```bash
uv sync --all-packages --group dev
uv run --package cipher-lab pytest
uv run --package cipher-lab ruff check packages tests projects
```
