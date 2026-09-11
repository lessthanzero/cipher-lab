# Scientific Boundaries & Epistemic Policies

1. **Unicity Distance Invariant**:
   For any cipher family, Shannon's unicity distance $U_0 = \frac{H(K)}{D}$ must be calculated. If ciphertext length $N < U_0$, the system must declare the corpus underdetermined and refuse unconstrained text generation.
2. **Permutation & Negative-Twin Controls**:
   Any candidate decryption claiming statistical significance must be evaluated against 1,000 order-shuffled surrogates and negative-control twin cryptograms. The candidate score must exceed $p < 0.001$ with False Discovery Rate (FDR) adjustment.
3. **Abstentions Counted in Denominator**:
   Abstentions and rejected trials are permanently logged in the DuckDB trial ledger. They must never be scrubbed to inflate success metrics.
4. **No Unconstrained "Typo Correction"**:
   For suspected error-slip ciphers (e.g., D'Agapeyeff), error-slip operators are strictly bounded (maximum 1-2 edit operations) with explicit penalty terms.
