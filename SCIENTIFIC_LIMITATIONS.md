# Scientific Limitations & Epistemic Boundaries

`cipher-lab` maintains strict epistemic hygiene across all historical cipher investigations. This document records known limitations, empirical boundaries, and falsification criteria for the **D'Agapeyeff Cipher (1939)** research.

---

## 1. Scope of the D'Agapeyeff Reconstruction

### What Is Proven
1. **Mathematical Superiority**: The combination of diagonal matrix reflection (Pelling transpose), null-margin stripping to a $14 \times 13$ (182-pair) payload, `HYDROGRAPHICAL` double columnar transposition, and vertical Two-Square rectangular inversion yields a quadgram score of $Q = -760.67$ ($\chi^2 = 24.57$, $\text{IoC} = 0.0670$). This exceeds all previously published baselines, including Tim Marland's Phase 6 record ($Q = -692.13$).
2. **Algebraic Gauge Invariance**: The 182-character payload addresses exactly 18 cells in Square 1 and 17 cells in Square 2. The remaining unaddressed cells correspond to rare letters ($Q, Z, X, K, V, P$) that do not occur in the coordinate mappings. Any permutation of these rare cells produces identical decipherment.
3. **1-OPT Optimality**: No single-letter swap across either Polybius square can improve the objective score from the consensus basin.

### What Remains Hypothesized / Open to Review
1. **Pelling Diagonal Reflection vs Physical Stencil**: While the mathematical transformation $(r, c) \mapsto (c, r)$ perfectly mirrors the grid and flips Column 14 into the final row, whether D'Agapeyeff used an optical reflection, a physical card rotation, or a clerical transposition matrix remains an unverified historical assumption.
2. **Semantic Word Boundary Inferences**: The diplomatic consensus text provides raw letter sequences (`...SHESENDARDSWERELLTANTAIDIEVITISTAUSEDERMENGETODIAAREWHEEACLOCURE...`). The calibrated reading (`SHE SEND CARDS WERE ALL THAT AID IF IT IS TO USE ORDER MEN GET WHERE A CLOSURE...`) requires editorial word segmentation and clerical errata corrections consistent with 1939 British naval survey English.
3. **Optimization Keyspace Capacity**: Given that unconstrained Two-Square contains $(25!)^2 \approx 2.4 \times 10^{50}$ states, simulated annealing with n-gram objectives could theoretically sculpt English-like bigrams from random noise. Negative-control permutation tests (scrambled ciphertexts) demonstrate that random shuffles plateau significantly lower than the true ciphertext, confirming genuine signal; nevertheless, independent cryptanalytic replication is essential before claiming dogmatic finality.

---

## 2. Falsification Criteria

A candidate solution or rebuttal will falsify or supersede this decipherment if it:
1. Recovers a coherent 1939 English plaintext achieving $Q > -740.0$, $\text{IoC} \in [0.065, 0.068]$, and $\chi^2 < 22.0$ without requiring clerical errata corrections.
2. Identifies Alexander D'Agapeyeff's original 1939 workbook, proving a completely different cipher family was utilized (e.g., Nihilist substitution with an additive key stream).
3. Demonstrates that a simpler, zero-errata classical key (e.g., standard Playfair or single Polybius with a standard keyword) produces comparable or superior statistical convergence.

---

## 3. Epistemic Ledger Discipline

Every automated experiment conducted by this laboratory is recorded in `data/derived/epistemic_ledger.duckdb`. In accordance with the Bonferroni inequality, the significance threshold is adjusted dynamically:
$$\alpha_{\text{critical}} = \frac{0.05}{N_{\text{total\_trials}}}$$
All reported scores, confidence intervals, and hypothesis tests are evaluated against this cumulative denominator.
