# Cipher Lab

Modular, reproducible research infrastructure for computational analysis of historical ciphers, tachygraphy, and cryptograms. Sibling repository to [`ancient-text-lab`](../ancient-text-lab).

## Scope & Taxonomy

While `ancient-text-lab` is dedicated to natural ancient writing systems and archaeological epigraphy (Linear A/B, Indus Script, Rongorongo, Phaistos Disc), `cipher-lab` focuses on deliberate artificial ciphers, early-modern shorthand systems, and historical enigmas:

1. **[D’Agapeyeff Cipher (1939)](projects/dagapeyeff/README.md)**: 392 digits (196 pairs, digits 1–5). **Deciphered & Reconstructed** via Pelling diagonal reflection, 182-pair payload extraction, `HYDROGRAPHICAL` double transposition, and vertical Two-Square rectangle inversion ($Q = -760.67$, $\text{Cohen's } d = 4.49$ vs negative-control shuffles).
2. **[Dorabella Cipher (1897) & 1886 Liszt Inscription](projects/dorabella/README.md)**: 87 glyphs in 3 lines across 24 symbols. **Codicologically Bounded & Structurally Characterized** as a melodic cryptogram anticipating *Enigma Variations, Op. 36, Variation X ("Dorabella")*, cross-validated against the 1886 Liszt Inscription negative control ($N=18$), isolating John Holt Schooling's April 1896 Nihilist coordinate harmonic ($+5.08\sigma$ at lag 6), while establishing a definitive negative result for standard English prose across 17,000+ keywords.
3. **[Rohonc Codex (c. 1530–1550)](projects/rohonc/README.md)**: 448 pages, ~87k characters, ~150 core signs, 87 Christian Passion illustrations. **Resolved as an Early-Modern Liturgical Tachygraphic Codebook & Controlled Syllabary** (Király & Tokai 2018; Láng 2021). Watermark anchored to Venetian mills (1530–1540, Briquet 541); unstructured hoax and modern forgery myths mathematically rejected ($Z = +14.27\sigma$ syntax permutation test); 50 core codebook entries mapped; formulaic liturgical collocations extracted (`Apostoli`, `Pater et Filius`, `Pilatus et Christus`); Diatessaron sequence aligned to Passion scenes (Folio 125v Golgotha Crucifixion $Z = +2.07\sigma, p = 0.048$).
4. **[Shugborough Inscription (c. 1748–1756)](projects/shugborough/README.md)**: 8 letters (`OUOSVAVV`) flanked by `D · M ·` on Peter Scheemakers' Shepherd's Monument. **Codicologically Bounded & Epigraphically Characterized**: Shannon unicity violation ($N \ll U_0$) mathematically bounds single-key cryptanalysis; carved interpuncts (`·`) and rounded `U` vs pointed `V` letterforms prove an 18th-century memorial Latin initialism under *Dis Manibus*; Bayesian transition modeling benchmarks historical candidates while falsifying the popular "widower" and polyalphabetic "Magdalen" myths.

## Key Publications & Documentation

- **[D'Agapeyeff Decipherment Report](projects/dagapeyeff/README.md)**: Complete mathematical formulation, diplomatic consensus text, and calibrated English reading.
- **[Dorabella Research Report](projects/dorabella/README.md)**: Epistemic ledger (40,752 trials), 1886 Liszt negative control, species counterpoint evaluation, and dual MIDI synthesis.
- **[Rohonc Codex Academic Preprint](docs/ROHONC_CODEBOOK_RESOLUTION_PAPER.md)**: Formal codicological, tachygraphic morphology, and liturgical Diatessaron resolution paper (*Cryptologia* / *Early Modern Studies*).
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

## Distributed Compute Harness & Hardware Architecture

The laboratory operates across a coordinated heterogeneous multi-node computing architecture designed for memory safety, reproducible batch execution, and high-throughput permutation sweeps:

1. **Local Apple Silicon Workstation (Darwin M1 Pro, 16GB)**:
   - **Darwin Memory-Safe Telemetry**: Computes true available physical RAM via Mach page accounting (`vm_stat` parsing `Pages free`, `speculative`, `inactive`, `purgeable` at 16 KB default page size). Prevents memory exhaustion or disk swap thrashing when processing large n-gram arrays.
   - **Interactive & Real-Time Engines**: Executes deterministic unicity gating, Fuxian species counterpoint rules engines, DuckDB ledger tracking, and pure-Python MIDI audio synthesis.

2. **Remote Fedora Linux PC Worker (`pc:192.168.1.172`, 8 CPU Cores)**:
   - **Remote Compute Dispatch**: Orchestrated via `RemoteComputeWorker` over SSH with automated health checking and batch serialization.
   - **Heavy Monte Carlo Permutations**: Runs massive parallel null simulations (e.g. 724 multi-core permutation batches totaling >700,000 token order shuffles for the Rohonc syntax test at $Z = +14.27\sigma$).
   - **Exhaustive Parameter Sweeps**: Dispatches multi-threaded grid sweeps across 14x14 transposition matrices, dictionary key sweeps (17,000+ words for Dorabella), and polyalphabetic fractionations.

3. **Append-Only Epistemic Ledger (DuckDB)**:
   - Persistent embedded ledger (`data/derived/epistemic_ledger.duckdb`) tracking every hypothesis trial across all ciphers (40,752 trials logged).
   - Enforces dynamic family-wise error rate (FWER) control via Bonferroni correction ($\alpha_{\text{critical}} = 0.05 / 40{,}752 = 1.23 \times 10^{-6}$) and Benjamini-Hochberg False Discovery Rate (FDR) adjustments.

## Model Referee Architecture & LLM Telemetry

To eliminate LLM apophenia, confirmation bias, and hallucinated "translations," `cipher-lab` employs a multi-tiered referee protocol that couples closed and open models under double-blind controls:

1. **Double-Blind Referee Protocol with Foils (`evaluate_with_blinded_foils`)**:
   - The candidate decipherment is shuffled alongside 2–3 negative-control decoys (synthetic anagrams or scrambled ciphertexts).
   - Referees evaluate linguistic coherence blindly. If an LLM selects a decoy or scores a scrambled foil highly, its evaluation is marked as an apophenic failure and penalized.

2. **Multi-Tier Model Stack**:
   - **OpenAI Codex (`gpt-5.6` / `gpt-6-astra`)**: Invoked via CLI (`codex exec --sandbox read-only`) with low reasoning effort for high-level adversarial critique and hypothesis falsification.
   - **Google Antigravity 3.8 Flash**: Multi-repo agent synthesis, epistemic protocol orchestration, and experimental plan management.
   - **Homelab Ollama Worker Cluster (`pc:11434` & `127.0.0.1:11434`)**:
     - `qwen2.5:7b`: Statistical and adversarial linguistic peer review passes.
     - `gemma2:9b`: Archaeological, epigraphic, and historical sanity checks.
     - `qwen2.5-coder:7b`: Code hygiene, packaging, and reproducibility verification.
     - `llama3.2:3b` & `phi4-mini:latest`: Fast word-boundary segmentation and low-latency blinded foil scoring.

3. **Structured Telemetry Logging**:
   - All local and remote model requests are logged to `~/.local/share/local-models/usage.jsonl` recording ISO timestamp, project name, task, provider, model ID, token counts, and execution latency in milliseconds.

## Quickstart & Verification

```bash
# 1. Sync environment
uv sync --all-packages --group dev

# 2. Run full test suite (120 passing tests)
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

# 7. Verify Rohonc Codex codebook extraction, liturgical alignment & distributed MC
uv run python -m projects.rohonc.runner --mode all
```
