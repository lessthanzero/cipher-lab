# Cipher Lab

Modular, reproducible research infrastructure for computational analysis of historical ciphers, tachygraphy, and cryptograms. Sibling repository to [`ancient-text-lab`](../ancient-text-lab).

## Scope & Taxonomy

While `ancient-text-lab` is dedicated to natural ancient writing systems and archaeological epigraphy (Linear A/B, Indus Script, Rongorongo, Phaistos Disc), `cipher-lab` focuses on deliberate artificial ciphers, early-modern shorthand systems, and historical enigmas:

1. **[D’Agapeyeff Cipher (1939)](projects/dagapeyeff/README.md)**: 392 digits (196 pairs, digits 1–5). **Deciphered & Reconstructed** via Pelling diagonal reflection, 182-pair payload extraction, `HYDROGRAPHICAL` double transposition, and vertical Two-Square rectangle inversion ($Q = -760.67$, $\text{Cohen's } d = 4.49$ vs negative-control shuffles).
2. **[Dorabella Cipher (1897) & 1886 Liszt Inscription](projects/dorabella/README.md)**: 87 glyphs in 3 lines across 24 symbols. **Codicologically Bounded & Structurally Characterized** as a melodic cryptogram anticipating *Enigma Variations, Op. 36, Variation X ("Dorabella")*, cross-validated against the 1886 Liszt Inscription negative control ($N=18$), isolating John Holt Schooling's April 1896 Nihilist coordinate harmonic ($+5.08\sigma$ at lag 6), while establishing a definitive negative result for standard English prose across 17,000+ keywords.
3. **Rohonc Codex**: ~450 pages, ~87k characters, early-modern European codebook-syllabary tachygraphy (Király & Tokai 2010/2018).
4. **[Shugborough Inscription (c. 1748–1756)](projects/shugborough/README.md)**: 8 letters (`OUOSVAVV`) flanked by `D · M ·` on Peter Scheemakers' Shepherd's Monument. **Codicologically Bounded & Epigraphically Characterized**: Shannon unicity violation ($N \ll U_0$) mathematically bounds single-key cryptanalysis; carved interpuncts (`·`) and rounded `U` vs pointed `V` letterforms prove an 18th-century memorial Latin initialism under *Dis Manibus*; Bayesian transition modeling benchmarks historical candidates while falsifying the popular "widower" and polyalphabetic "Magdalen" myths.

## Key Publications & Documentation

- **[D'Agapeyeff Decipherment Report](projects/dagapeyeff/README.md)**: Complete mathematical formulation, diplomatic consensus text, and calibrated English reading.
- **[Dorabella Research Report](projects/dorabella/README.md)**: Epistemic ledger (40,752 trials), 1886 Liszt negative control, species counterpoint evaluation, and dual MIDI synthesis.
- **[Shugborough Research Report](projects/shugborough/README.md)**: Epigraphic interpunct audit, Shannon unicity violation proof, Bayesian Latin initialism model, and pseudohistory refutations.
- **[Shugborough Academic Preprint](docs/SHUGBOROUGH_EPIGRAPHIC_PAPER.md)**: Formal codicological, epigraphic, and information-theoretic resolution paper (*The Antiquaries Journal* / *Cryptologia*).
- **[Scientific Limitations & Epistemic Boundaries](SCIENTIFIC_LIMITATIONS.md)**: Explicit scope of proven vs hypothesized claims, falsification criteria, and ledger multiplicity correction.
- **[Community Review & Announcement Package](docs/ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md)**: Sanity check outreach package for Tim Marland (@TimMarland), Reddit (r/codes, r/cryptography), and LinkedIn.

## Core Principles

- **Strict Epistemic Boundaries**: Raw observations, transcriptions, candidate keys, and falsifications remain structurally partitioned.
- **Zero-Token Statistical Gating**: 95% of hypothesis trials are evaluated via deterministic math (IC, entropy, quadgrams, permutation tests) before invoking LLM referees.
- **Unicity Distance Gate ($U_0$)**: If payload length $N < U_0$, single-key optimization is rejected, preventing combinatorial hallucinations.
- **Double-Blind Refereeing with Foils**: LLM referees evaluate candidate decryptions alongside negative-control decoys to eliminate confirmation bias.
- **Append-Only Epistemic Ledger**: Multiplicity-corrected $p$-values are computed across the full denominator of all trials (40,752 trials tracked in DuckDB).

## Quickstart & Verification

```bash
# 1. Sync environment
uv sync --all-packages --group dev

# 2. Run full test suite (97 passing tests)
uv run pytest

# 3. Verify D'Agapeyeff decipherment
uv run python -m projects.dagapeyeff.exact_14key_sweep
uv run python -m projects.dagapeyeff.linguistic_reconstruction

# 4. Verify Dorabella species counterpoint & Nihilist coordinate solver
uv run python -m projects.dorabella.counterpoint_evaluator
uv run python -m projects.dorabella.nihilist_coordinate_solver

# 5. Synthesize Dorabella and 1886 Liszt MIDI audio streams
uv run python -m projects.dorabella.dual_musical_engine

# 6. Verify Shugborough epigraphy, Bayesian initialisms & DuckDB ledger
uv run python -m projects.shugborough.runner
```
