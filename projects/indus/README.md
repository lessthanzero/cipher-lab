# Indus Script Discovery Sprint (cipher-lab)

**Laboratory Track**: Undeciphered Ancient Epigraphy & Structural Cryptanalysis  
**Corpus**: Indus Valley Civilization (Harappan), c. 2600–1900 BCE  
**Primary Dataset**: Mohenjo-Daro Unicorn Seal Inscriptions (179 texts, 1,003 tokens, 182 sign types; Corpus of Indus Seals and Inscriptions — CISI / Parpola 1994)  
**Dual-Catalog Concordance**: Cross-mapped across Parpola ($P$), Mahadevan ($M77$), and Wells ($W$) signaries (396 mapped graphemes)  

---

## 1. Epistemic Invariants & Scientific Guardrails

1. **Translation is Strictly Prohibited**:
   Shannon unicity distance ($U_0 \approx 200\text{--}450$ signs for a 182–417 sign inventory) vastly exceeds the maximum single-line inscription length ($N \le 17\text{--}26$ signs; mean length $\bar{L} \approx 4.6$ signs). Without a bilingual Rosetta stone or physical anchor, any unconstrained mapping of signs to phonetic values (Dravidian, Indo-Aryan, Munda, or Sumerian) is mathematically underdetermined and constitutes statistical apophenia.

2. **Structural & Entropic Discrimination**:
   The sprint evaluates the central computational debate in ancient script studies:
   - **Linguistic Hypothesis** (Mahadevan 1977; Parpola 1994; Rao et al., *Science* 2009): The Indus script is a glottographic, logosyllabic writing system encoding spoken language.
   - **Non-Linguistic Registration Hypothesis** (Farmer, Sproat, & Witzel 2004; Sproat 2010, 2014; Mukhopadhyay 2019; Kriger & Hunt 2026; Venugopal 2026): The script is a positionally structured, non-linguistic emblem, property-marking, or cargo-tag barcode system.

3. **Hostile Permutation Nulls**:
   All statistical claims must survive four adversarial null models:
   - **Null 1 (Uniform Shuffle)**: Uniform random permutations within sequence length.
   - **Null 2 (Frequency-Preserving Shuffle)**: Random permutations preserving exact unigram corpus frequencies.
   - **Null 3 (Positional-Marginal-Preserving Permutation)**: Shuffling signs strictly within their observed positional slot.
   - **Null 4 (Structured Non-Linguistic Control)**: Synthetic tags generated from formal non-linguistic grammars (Sproat deity/heraldic formula and Meluhha 4-slot cargo-tag schema).

4. **Multiplicity-Adjusted Ledgering**:
   Every hypothesis trial is recorded in `data/derived/epistemic_ledger.duckdb` with Bonferroni and Benjamini–Hochberg False Discovery Rate (FDR) control ($\alpha = 0.001$).

---

## 2. Architecture & Compute Fabric

- **macOS M1 Pro (Local Host)**: Data ingestion, dual-catalog concordance harmonization, DuckDB ledger tracking, and local unit test execution.
- **Fedora Linux PC (`pc`, x86_64, 16 GB RAM)**: Heavy batch Monte Carlo null simulations ($N=100,000$ iterations) and bootstrap parameter estimations via `discovery_pc.py` and `scripts/remote_worker.sh`.
- **Peer Advisory Panel (Consilium)**: Multi-model consensus panel (`qwen`, `agy`, `codex`) via `~/Developer/dotfiles/scripts/agent/consilium.sh`.
