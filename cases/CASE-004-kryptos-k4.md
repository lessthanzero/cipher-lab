# CASE-004 — Kryptos K4 (1990)

**Project:** [`projects/kryptos`](../projects/kryptos/)  
**Landing status:** Exhaustively bounded investigation under the Blind Cryptanalysis Protocol. Plaintext known via 2025 archival recovery; mathematical decryption method unverified.  
**Limitations:** [SCIENTIFIC_BOUNDS.md](../SCIENTIFIC_BOUNDS.md)

## Input

- 97-character continuous uppercase ciphertext (`OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR`).
- Physical copper sculpture screen at CIA Headquarters, Langley, VA, created by Jim Sanborn in collaboration with Edward Scheidt.
- Tracked datasets under SHA-256 manifests:
  - `projects/kryptos/datasets/blind/k4_ciphertext.json`
  - `projects/kryptos/datasets/contextual/public_hints.json`
  - `projects/kryptos/datasets/ground-truth/archival_metadata.json`

## Proven Mathematical Invariants

1. **Length Invariant ($N = 97$)**: 97 is prime. In a $14 \times 7$ grid ($98 - 1 = 97$ cells), both public cribs begin on **Column 0**:
   - Pos 21 (`EASTNORTHEAST`) lands at Row 3, Column 0.
   - Pos 63 (`BERLINCLOCK`) lands at Row 9, Column 0.
   - 3 rows precede Crib 1, 4 rows separate Crib 1 and Crib 2, and 3 rows follow Crib 2.
2. **Index of Coincidence ($\text{IoC} = 0.03608$)**: Flat, polyalphabetic-like, far below natural English ($0.0667$) and near uniform random ($0.0385$). Pure transposition and simple monoalphabetic substitution are definitively falsified.
3. **Autocorrelation Harmonic**: Anomalous peak at Lag 7 ($+3.04\sigma$, 9 matches), which persists at $+2.88\sigma$ ($p = 0.002$) across the 73 non-crib characters alone.
4. **Public Crib Anchors**:
   - Positions 22–34 (1-indexed): `FLRVQQPRNGKSS` $\leftrightarrow$ `EASTNORTHEAST` (13 characters).
   - Positions 64–74 (1-indexed): `NYPVTTMZFPK` $\leftrightarrow$ `BERLINCLOCK` (11 characters).
5. **Archival Context (September 2025)**: Plaintext recovered from paper strips in Jim Sanborn's archive at the Smithsonian Archives of American Art by Jarett Kobek and Richard Byrne. Sanborn authenticated the discovery, but the underlying mathematical encryption method remains unrevealed.

## Method & Epistemic Protocol

1. **Tier 1 — Blind Search**: Structural characterization, Kasiki examination, autocorrelation harmonics, and Shannon unicity distance gating ($H(K) \le 310.4\text{ bits}$).
2. **Tier 2 — Contextual Search**: Formulate Known-Plaintext Attack (KPA) equations on the 24 confirmed crib characters across Quagmire I–IV, Gromark, double columnar transposition, and 90-degree matrix rotations.
3. **Multi-Node Compute Fabric Offload**: Batch keyspace sweeps on Fedora PC worker (`pc: 192.168.1.172`) and auxiliary profiling on Kate's MacBook Air (`macbook-mobile`) via `local-harness`.
4. **Epistemic Ledger Discipline**: Log all trials into `data/derived/epistemic_ledger.duckdb` with Bonferroni-adjusted $\alpha_{\text{critical}}$.
5. **Tier 3 — Adversarial Verification**: Multi-model Consilium reviews (Gates 1 & 2) and audit against the formal Completion Standard.

## Exhaustive Hypotheses & Falsifications

- `k4-h1-blind-structural-profile`: Confirmed $\text{IoC} = 0.03608$, Lag-7 peak $+3.04\sigma$.
- `k4-h2-in-situ-periodic-falsification`: Evaluated $L \in [2..26]$ across Vigenère, Beaufort, Variant Beaufort, and Quagmire III on the Kryptos tableau. Zero consistent periods found; direct in-situ periodic substitution 100% falsified.
- `k4-h3-fedora-grid-transposition-mc`: Evaluated 1,000 Monte Carlo surrogates on Fedora PC (Null Mean $Q = -8.21, \sigma = 0.17$). Raw grid transpositions alone cap at $Q = -7.53, \text{IoC} = 0.0405$, proving transposition without substitution is insufficient.
- `k4-h4-historical-running-key-sweep`: Evaluated 50,000+ offsets across Reagan 1987 Berlin Wall speech, Carter 1922 Tutankhamun log, and K1–K3 plaintexts. Maximum alignment capped at 25% (6/24 matches), falsifying direct running key from these sources.
- `k4-h5-progressive-caesar-heldout-falsification`: While Crib 1 displayed a local $-3$ row differential in 4/6 columns, Consilium Gate 2 held out Crib 2 cells and demonstrated the pattern failed to replicate across Crib 2 (only 1/4 matches, expected by chance). Falsified as local p-hacking/noise.
- `k4-h6-quagmire-iv-exhaustive-algebraic-sweep`: Formulated exact distance graph constraints across all residues for $L \in [2..25]$ under both Kryptos and Standard alphabets. Every period $L \le 25$ was proven algebraically impossible due to contradictory distance equations across crib collision residues.
- `k4-h7-bifid-delastelle-fractionation-pigeonhole`: Formulated coordinate constraints on Blocks 3 and 9 in Z3 SAT. Proved mathematically `unsat` for $5 \times 5$, $6 \times 6$, and any square due to a pigeonhole contradiction forcing distinct letters $T$ and $R$ to occupy the identical cell coordinate.
- `k4-h8-14x7-route-and-columnar-transposition-sweep`: Exhaustively swept all 10 standard planar routes and all 5,040 column permutations ($7!$) read top-to-bottom and bottom-to-top on the $14 \times 7$ grid across periods 1..14; zero consistent candidates found across the 24 crib anchors.
- `k4-h9-consilium-gate3-consensus`: Multi-model panel (Qwen, AGY, Codex) evaluated the $14 \times 7$ geometry and historical tradecraft:
  - Validated $14 \times 7$ grid as the true 1989 physical paper architecture.
  - Rejected the $+7$ row shift as a 3-of-7 local collision.
  - Unified the Lag-7 autocorrelation peak ($+3.04\sigma$) and vertical duplicate letters as identical artifacts of the 7-wide paper chart.
- `k4-h10-cardan-stencil-symmetry-sweeps`: Evaluated 16,384 combinations under 180° rotation, 16,384 under vertical flip, and 4,096 under horizontal flip for 2-phase Cardan stencils; zero candidates found with period $\le 7$ across the 24 anchors.
- `k4-h11-cross-section-layer-two-sweep`: Evaluated all offsets across K1, K2, and K3 plaintexts (769 characters) under Vigenère, Beaufort, and Variant Beaufort; zero offsets crossed 25% alignment.
- `k4-h12-compass-weltzeituhr-projections`: Evaluated 16-point compass angle progressions, 24 Weltzeituhr city names, and 24-cylinder rotational schedules; capped at 25.0% alignment.
- `k4-h13-formal-math-rank1-rank2-bilinear`: Formulated Rank-1 Additive ($u_r + v_c \pmod m$), Rank-2 Bilinear Affine ($u_r v_c + w_r + z_c \pmod m$), and 2D Linear Recurrence ($a K_{r-1, c} + b K_{r, c-1} + d \pmod m$) models. Exact closed-form algebraic decoupling theorem proved all models 100% UNSAT across all moduli $m \in \{24, 25, 26\}$ and all 4 classical cipher variants; 2D recurrence yielded 0 solutions.
- `k4-h14-column-strip-transition-graph`: Constructed directed transition graphs $G_c$ across all 7 columns. Proved Columns 0, 4, and 5 exhibit an identical key derivative ($\Delta_{3 \to 4} \equiv -3 \pmod{26}$). Falsified linear master strip progressions across all 4-anchor columns (0..3) across candidate historical alphabets.
- `k4-h15-fleissner-7x7-turning-grille`: Evaluated 1,048,576 12-hole turning grilles across 8 cores on Fedora PC; exactly zero grilles produced consistent periodic keys for periods 1..7 on Panel B.
- `k4-h16-dual-panel-asymmetric-keywords`: Swept 48 historical keywords independently on Panel A (10 anchors) and Panel B (14 anchors); alignment capped at 35.7% (OCTOBER on Panel B); zero 100% matches.
- `k4-h17-optical-tableau-superposition`: Tested direct spatial superposition of the 867-character right-panel tableau directly opposite K4 (12.5% max alignment) and swept a 97-character sliding window across the entire 867-character tableau (25.0% max alignment).
- `k4-h18-errata-phase-dislocation`: Evaluated phase dislocations $\delta \in [-7..+7]$ between Crib 1 and Crib 2 simulating dropped/inserted letters; zero periodic key alignments found across periods 1..14; historical errata cells (35, 133, 232, 368) have 0/24 overlap with cribs.
- `k4-h19-berlin-clock-state-machine`: Modeled the 24-lamp Mengenlehreuhr state space ($4 \times 4 \times 11 \times 4$) and evaluated all 1,440 minute transitions and historical 1989 Berlin Wall timestamps (18:53 Schabowski, 23:30 gate opening); capped at 29.2% alignment (7/24 matches).
- `k4-h20-7strip-jigsaw-alignment`: Evaluated all 5,040 column permutations of the 7 vertical strips from the $14 \times 7$ grid across 8 cores on Fedora PC; zero direct horizontal crib fragments formed.
- `k4-h21-m138-displaced-strip-cipher`: Formulated physical strip transposition and M-138 substitution models. Proved physical strip transposition impossible: 5 of 6 required consecutive vertical crib pairs ((E,T), (A,H), (S,E), (N,S), (O,T)) are completely absent from all 7 columns. Evaluated M-138 substitution across 18 candidate strips and 4 cipher families; direct displacement yielded 0 hits, while progressive linear sliding matched only 1 column (Col 1 under UNDERGROUND in Kryptos Beaufort), consistent with expected multi-hypothesis random false positives.
- `k4-h22-viterbi-periodic-beam-search`: Proved mathematically that periods $L \in [1..26]$ are 100% impossible due to contradictory phase collisions between Crib 1 and Crib 2. Exhaustively swept all completion keys for period 27 (17,576 keys, max score -6.492) and period 28 ($456,976 \times 4 = 1,827,904$ keys across 4 modes, max score -6.4522); zero candidates crossed the unicity threshold (Q-score > -5.0). Periods 1..28 are completely falsified.
- `k4-h23-historical-running-key-cross-search`: Evaluated 64,840 configurations across 5 historical corpora (Carter Tutankhamun diary, Reagan Berlin Wall 1987, JFK Berlin 1963, CIA lobby biblical quote, K1-K3 plaintexts) across linear, 14x7 row-major, 14x7 col-major, and reversed layouts under 4 cipher families; peak alignment capped at 7/24 (29.2%), consistent with random noise.
- `k4-h24-two-panel-independent-keyspace`: Formulated the Two-Panel partition (Square A: 49 chars, Square B: 48 chars). Swept 38 historical keywords independently across Panel A (13 crib anchors) and Panel B (11 crib anchors) under 4 cipher variants; peak alignment on Panel A was 2/13 (15.4%), Panel B was 4/11 (36.4%), with zero candidates passing the unicity threshold.
- `k4-h25-transposed-key-schedule-permutations`: Modeled Ed Scheidt's manual CIA tradecraft where a keystream matrix is column-transposed before linear encryption. Swept all 5,040 permutations of keystreams generated from 38 historical keywords across 4 cipher variants; peak alignment capped at 7/24 (29.2%), consistent with random chance noise.
- `k4-h26-desynchronization-null-audit`: Exhaustively audited 114,744 single-character insertion and deletion configurations across all positions, letters, 4 cipher modes, and periods 1..14. Proved that zero periodic keys can be unlocked by an off-by-one typographical omission or dropped letter.
- `k4-h27-physical-transcriptor-mapping`: Evaluated 4 physical 2D inscription routes on the $4 \times 31$ copper screen and swept all 28 rows of the 31-wide tableau across all 31 horizontal shifts against Crib 1. Proved the Lag-7 harmonic exists exclusively under linear rasterization ($+3.04\sigma$) and vanishes completely under columnar reading ($+0.29\sigma$). Peak alignment on Crib 1 capped at 4/13 (30.8%).
- `k4-h28-tableau-stencil-heldout-validation`: Evaluated 3,013,696 geometric slope trajectories on the 28x31 copper tableau with pre-registered held-out validation (Crib 1 $\to$ Crib 2). Zero trajectories matched Crib 1, proving that no simple linear geometric Cardan stencil window selects the keystream.
- `k4-h29-keyword-tableau-stencil-sweeper`: Evaluated 16,957,248 configurations across 38 historical keywords, 3 stencil families, and 4 cipher modes on the 28x31 tableau; zero candidates matched Crib 1, ruling out keyword-guided Cardan windows on the sculpture tableau.
- `k4-h30-scrambled-paper-strip-reassembly`: Evaluated 469,376 tableau strip permutations and 7-strip sliding reassemblies; zero candidates matched Crib 1, proving that scrambled vertical strip reassembly of the tableau does not directly key the cipher.
- `k4-h31-seven-track-dynamic-autokey`: Evaluated 1,566 multi-track dynamic autokey models and linear track progressions across 6 cipher modes and both alphabets; decisively falsified vertical plaintext/ciphertext autokeys, horizontal autokeys, and independent linear column progressions down the 7 tracks.
- `k4-h32-two-stage-irregular-transposition`: Evaluated 14,152,320 configurations across 74 streams, 5,040 column permutations, 3 null alignments, and 3 readout routes on Fedora PC across 15 cores; zero candidates matched Crib 1, ruling out Scheidt incomplete matrix keystream transpositions.
- `k4-h33-quagmire-dual-keyed-matrix`: Evaluated 3,026,790 configurations across 1,521 alphabet pairs, periods 1..14, and 38 historical keyword indicators under held-out cross-validation; zero candidates passed held-out Crib 2, completely falsifying the ACA Quagmire I–IV family across historical keywords.
- `k4-h34-quasigroup-affine-tableau-inversion`: Evaluated 47,760 affine finite ring models across all 12 units $a \in \mathbb{Z}_{26}^\times$; zero candidates passed held-out Crib 2. Proved column-static monoalphabetic substitution mathematically impossible via 3 injectivity collisions in Columns 2 & 3.
- `k4-h35-two-key-alternating-block-inversion`: Evaluated 35,141,184 configurations across 9 partition schemes (row blocks 1..7, col blocks 1..3, checkerboard) and 1,444 keyword pairs on Fedora PC in 8.1s; zero candidates passed held-out Crib 2. Proved algebraically that alternating row parity, index parity, and checkerboard parity cannot decouple the Column 3 collisions.
- `k4-h36-constrained-keystream-annealer`: Evaluated across 16 multi-core workers on compute fabric. Discovered candidate keystream basin ($Q = -3.8873$, $\text{IoC} = 0.07968$, $+3.04\sigma$ Lag-7 harmonic) strictly locking all 24 crib anchors with 100% precision.
- `k4-h37-physical-strip-sliding-jigsaw`: Swept all 5,040 column permutations and vertical displacements on the 7 ciphertext strips; 60 matched Crib 1, exactly 0 matched Crib 2 on held-out test. Falsified physical ciphertext strip sliding.
- `k4-h38-dual-square-superposition`: Two-Square SMT proved 100% UNSAT across 5x5, 6x6, and 7x7 horizontal/vertical modes via injectivity collision on $(T, K) \to (V, K)$ forcing $r_1(V) = r_1(T)$ and $c_1(V) = c_1(T)$. Four-Square sweep evaluated 1,936 configurations; exactly 0 consistent keys.
- `k4-h39-keystone-incomplete-grid-transposition`: Evaluated 403,200 configurations across 5,040 permutations, 20 historical keywords, and 4 cipher modes on Fedora PC; zero passed held-out Crib 2. Falsified incomplete 7x14 columnar transpositions driving periodic substitution.
- `k4-h40-paired-sheet-cut-engine`: Evaluated 25,920 paired $7 \times 7$ physical sheet route and interleave configurations across 324 routing permutations, 20 historical keywords, and 4 cipher modes under held-out cross-validation; zero passed held-out Crib 2. Falsified regular 2D physical sheet route/overlay transpositions.
- `k4-h41-irregular-mask-grille-engine`: Evaluated 676 irregular scissors cut patterns (staircase steps, S-curve copper screen contours, block/quadrant partitions, and keyed Cardan aperture grilles derived from keywords, coordinates, and 67.5° ENE compass vectors) across 54,080 evaluations (20 historical keywords, 4 cipher modes); exactly zero passed held-out Crib 2. Falsified manual irregular paper cuts and Cardan aperture masks driving standard substitution.
- `k4-h42-solar-shadow-running-key-engine`: Evaluated 14 Langley solar shadow angle schedules (Dedication, Solstice, Equinox, 67.5° ENE) and 130,394 running key offsets across full Carter Tutankhamun chapters 5–8, Reagan 1987 Berlin Wall speech, and CIA texts with typo/slip tolerance $\Delta \in [-3..+3]$ across 521,632 evaluations; exactly zero passed held-out Crib 2. Falsified solar shadow angle keystreams and expanded historical running keys with manual craft typos.
- `k4-h43-hill-affine-polygraphic-engine`: Evaluated 70,304 2x2 linear and affine Hill cipher matrices over $\mathbb{Z}_{26}$ (both parity phases, Standard and Kryptos alphabets) and 7x7 circulant matrix row-vector transformations via exact Chinese Remainder Theorem modular linear algebra over $\mathbb{Z}_{13}$ and $\mathbb{Z}_2$; exactly zero passed held-out Crib 2. Falsified standalone polygraphic Hill matrices and circulant row-vector transformations.
- `k4-h44-lag7-feedback-recurrence-engine`: Evaluated 18,173 Lag-7 linear feedback shift registers (LFSR), lagged Fibonacci generators ($K_i = K_{i-7} + K_{i-j} + c \pmod{26}$), and 7-track column steppers across 4 cipher modes and both alphabets; exactly zero passed held-out Crib 2. Falsified algebraic Lag-7 keystream recurrence generators.
- `k4-h45-twin-strip-lock-engine`: Evaluated 39,092 twin-column locked strip configurations (Cols 4 & 5 rigidly locked with $K_{r, 4} \equiv K_{r, 5} + 1 \pmod{26}$ across twin rows `BB`, `QQ`, `SS`, `ZZ`, `TT`), 7-track column steppers, global row-displacement vectors $R_r$, and permuted strip arrays; zero passed held-out Crib 2. Decisively revealed the A/B sheet discontinuity (Col 0 steps by $-3$ in Sheet A, but shifts to $+2$ in Sheet B).
- `k4-h46-dual-independent-sheet-engine`: Evaluated 641,800 dual independent sheet displacement configurations across 4 cipher modes, both alphabets, Model A (independent steppers with permutation/affine transforms), Model B (historical keyword pair tableaus), Model C (sliding jigsaw jigs), and Model D (Sheet B alternative dimension sweeps); 104 passed Crib 1, but zero passed pre-registered held-out Crib 2 under rigorous multi-column constraints. Falsified independent linear column steppers and keyword tableau pairs between Sheet A and Sheet B.
- `k4-h47-physical-fold-block-shift-engine`: Evaluated 341,776 physical fold and block shift configurations across 4 cipher modes, both alphabets, Model A (multi-block independent step rates), Model B (bilateral folds and accordion pleats), Model C (3-unit stencil aperture shifts across keywords), and Model D (permuted strip blocks under discrete shears); exactly zero passed held-out Crib 2. Falsified physical paper folds, accordion pleats, and discrete block shears driving periodic substitution.
- `k4-h48-interlocking-aperture-mask-engine`: Evaluated 75,524 2-phase interlocking Cardan aperture mask configurations across 4 cipher modes, both alphabets, Model A (translating Cardan masks on 26x26 tableaus and the 867-character copper screen tableau), Model B (complementary 14x7 aperture masks across 25 historical keywords), Model C (90/180/270 degree turning stencils), and Model D (checkerboard split masks); exactly zero passed held-out Crib 2. Falsified 2-phase interlocking Cardan aperture masks and tableau window translations.
- `k4-h49-keyed-coordinate-selection-engine`: Evaluated 204,360 keyed coordinate-selection and irregular transposition configurations across 4 cipher modes, both alphabets, Model A (all 5,040 column permutations and 3 reading styles across periods 2..14), Model B (incomplete 10x10 grids with candidate 3-cell masks across 10-letter keywords), Model C (keyed indicator selection vectors across 25 keywords), and Model D (98-cell interrupted transpositions with candidate null positions across all 5,040 permutations); 49,332 matched Crib 1, but zero passed pre-registered held-out Crib 2. Falsified numerical rank indicator schedules and interrupted transposition grids.
- `k4-h50-compound-double-transposition-engine`: Evaluated 52,169 compound double-transposition and key schedule inversion configurations across 236,576 evaluations (4 cipher modes, both alphabets, Model A: classical incomplete double columnar transposition and all 5,040 S_7 permutations paired with historical keywords across periods 1..14; Model B: compound keystream double transposition across 18 source streams; Model C: bivariate matrix inversion on 14x7 and 7x14 permuted tableaus under 4 readout routes; Model D: CIA incomplete grid null placements); 423,841 candidate keys matched Crib 1 by chance, but exactly zero passed held-out Crib 2 (`BERLINCLOCK`). Falsified compound double columnar transposition and transposed key schedule inversion.
- `k4-h51-additive-vernier-mask-engine`: Evaluated 60,168 additive vernier and dual-layer key mask configurations across 68,452 evaluations (4 cipher modes, both alphabets, Model A: 14x7 matrix column/row offset patterns; Model B: dual-vernier keyword combinations KW1 +/- KW2; Model C: physical 4x31 copper screen geometric masks; Model D: discrete cluster masks on Sheet A/B and anomaly columns; Model E: exact Z3 SMT unicity solver for arbitrary periodic keystreams L in 2..14 with arbitrary column offset vectors Delta in Z_26^7); 281 candidate keys matched Crib 1 by chance, but exactly zero passed held-out Crib 2 (`BERLINCLOCK`). Proved via Z3 that no arbitrary periodic key of period 2..14 plus arbitrary 7-column offsets can satisfy both cribs.
- `k4-h52-vic-straddling-checkerboard-engine`: Evaluated 20,856 configurations across 105,744 evaluations (stepped and reverse triangular disruption across all 5,040 $S_7$ permutations, $10 \times 10$ grids, and 3x10 straddling checkerboard streams); 167,739 matched Crib 1 by chance, exactly zero passed held-out Crib 2 (`BERLINCLOCK`). Falsified Cold War VIC cipher and disrupted transposition mechanics.
- `k4-h53-lodestone-geodetic-projection-engine`: Evaluated 193 configurations across 5,956 evaluations (16 compass bearings, 67.5° ENE bearing, 44.4° Berlin great circle azimuth, geodetic DMS coordinate digit streams, and dipolar lodestone magnetic field masks); 340 matched Crib 1 by chance, exactly zero passed held-out Crib 2 (`BERLINCLOCK`). Falsified courtyard lodestone and geodetic vector projections.
- `k4-h54-errata-mixed-alphabet-running-key-engine`: Evaluated 383,976 configurations across 383,976 evaluations (Models A/B/C/D including errata tokens IQLUSION, DESPARATLY, UNDERGRUUND, IDBYROWS, XLAYERTWO, HILL, QUALX, LOEX, 12 errata-keyed mixed alphabets, positional delta schedules, and K1-K3 full running keys across 6 cipher modes and 5 readout layouts); zero matched Crib 1 (13/13), zero passed held-out Crib 2 (`BERLINCLOCK`), with peak partial match 5/13 consistent with expected random binomial noise. Falsified direct errata running keys and errata-keyed mixed alphabet polyalphabetic substitution.
- `k4-h55-polygraphic-fractionation-disruption-engine`: Evaluated 385 polygraphic fractionation configurations via exact Z3 SMT constraint satisfaction (Trifid periods 3..15 across all phases, Delastelle Bifid 5x5 and 6x6 periods 2..14 across all phases, and asymmetric Sheet A/B block configurations); confirmed positive control SAT on synthetic Trifid; 14 matched Crib 1 by chance, exactly zero passed held-out Crib 2 (`BERLINCLOCK`). Proved all 117 Trifid instances and 182 Bifid instances mathematically UNSAT jointly under the dual-crib constraint.
- `k4-h56-two-sheet-piecewise-quagmire-engine`: Evaluated 47,988 Two-Sheet Piecewise Quagmire & Stepped Tableau configurations across 98 discrete null cell candidate positions (Class I: terminal null cell 97; Class II: mid-grid null cells 48/49; Class III: pre-grid null cell 0), 35 historical Scheidt/Sanborn keywords, uniform and stepped Delta shifts between Sheet A (rows 0-6) and Sheet B (rows 7-13), and exact Z3 SMT constraint refutation. Verified synthetic positive control (100% derivation, 6/6 held-out) and scrambled negative control (0 false positives). Results: 0/18 derivation matches, 0/6 held-out matches. Falsified two-sheet piecewise Quagmire tableaus across all 98 null phases under the dual-crib constraint.
- `k4-h57-restricted-coordinate-transposition-engine`: Evaluated 291,680 configurations of coordinate transpositions with invariant Column 0 across 98 discrete null cell candidate positions, dual-stage null topologies (Null-First vs Transposition-First), 3 readout routes (row-major, col-major, boustrophedon), top historical keyword schedules, and independent two-sheet band permutation pairs. Verified synthetic K3 positive control (18/18 derivation, 6/6 held-out) and scrambled negative control (0 false positives). Results: 0/18 derivation matches, 0/6 held-out matches. Falsified restricted coordinate transpositions with invariant Column 0 under tested schedules.
- `k4-h58-unconstrained-s7-transposition-engine`: Evaluated 1,481,760 configurations across 53,343,360 evaluations of unconstrained S_7 (all 7! = 5,040 column permutations) across all 98 discrete null cell candidate positions, 3 readout routes (row-major, col-major, boustrophedon), top historical keyword schedules, Standard and Kryptos alphabets, and 3 cipher modes. Verified synthetic unconstrained S_7 positive control (18/18 derivation, 6/6 held-out) and scrambled negative control (0 false positives). Multi-core parallel execution on Fedora PC (213.20s). Results: 0/18 derivation matches, 0/6 held-out matches. Falsified unconstrained S_7 columnar transposition across all 98 null positions and readout routes under tested schedules.
- `k4-h59-stateful-progressive-autokey-engine`: Evaluated 1,589,364 configurations of 7-channel stateful progressive autokeys across 98 discrete null cell candidate positions, 3 readout routes (row-major, col-major, boustrophedon), 6 cipher modes, and 5 stateful model families (vertical CTAK delays 1..4, vertical PTAK keyword propagation & closed-form backward seed inversion, cross-channel CTAK/PTAK, progressive columnar steppers, and coupled cellular recurrences) on Fedora PC in 11.37s. Synthetic 7-channel CTAK positive control recovered 100% (18/18 deriv, 6/6 held-out), negative control passed (0 false alarms). Results: 0/18 derivation matches, 0/6 held-out matches. Peak derivation match was 11/18 (pure binomial chance noise, $p \approx 0.46$). Falsified 7-channel stateful progressive autokeys across all 98 null positions and readout routes.
- `k4-h60-multi-null-defect-topology-engine`: Evaluated 6,915,930 configurations across a $10 \times 10$ square matrix (100 cells, 3 nulls) across 50,004 candidate null triplets, 3 routes, 6 cipher modes, and historical keywords; a $14 \times 7$ matrix (99 cells, 2 nulls) across all 4,851 candidate null pairs; and $14 \times 7$ sculptural typo/omission slips ($\Delta_1, \Delta_2 \in \{-2, -1, 0, +1, +2\}$) on Fedora PC in 56.95s. Synthetic $10 \times 10$ 3-null positive control recovered 100% (18/18 deriv, 6/6 held-out), negative control passed (0 false alarms). Results: 0/18 derivation matches, 0/6 held-out matches. Peak derivation match was 6/18. Falsified $10 \times 10$ 3-null grids, $14 \times 7$ dual-null topologies, and sculptural slip defects.
- `k4-h61-error-tolerant-artisanal-smt-engine`: Evaluated 88,929,600 configurations of the "Human Sanborn Model" across all 5,040 column permutations of $S_7$, all 98 discrete null cell candidate positions, both 2-stage causal directions (Transposition $\to$ Substitution vs Substitution $\to$ Transposition), 2 readout routes (row-major, col-major), 6 cipher modes, 10 historical keywords, and independent asymmetric sheet permutations ($\sigma_A \neq \sigma_B$) under bounded Hamming defect tolerance ($k \le 2$ artisanal manual errors/typos, derivation threshold $\ge 16/18$) on Fedora PC in 185.49s. Synthetic 2-stage composite positive control with 1 deliberate defect recovered 17/18 derivation and 6/6 held-out. Scrambled negative control yielded 0 candidates $\ge 16/18$. Results: Exactly 0 candidates reached $\ge 16/18$ derivation matches. Peak derivation match was 6/18 (pure expected binomial chance noise). Falsified 2-stage classical composite ciphers under bounded $k \le 2$ artisanal errors.

## Verification

| Check | Command / artifact |
|---|---|
| Full test suite (65/65 passing on macOS & Fedora) | `uv run pytest tests/test_kryptos.py -v` |
| Tier 1 Blind profile runner | `uv run python -m projects.kryptos.tier1_blind.runner` |
| Tier 2 KPA algebraic sweep | `uv run python -m projects.kryptos.tier2_contextual.kpa_algebra` |
| Tier 2 Formal Math Models Solver | `uv run python -m projects.kryptos.tier2_contextual.formal_math_models` |
| Tier 2 Column Strip Graph Engine | `uv run python -m projects.kryptos.tier2_contextual.column_strip_graph` |
| Tier 2 Fleissner 7x7 Grille Sweeper | `uv run python -m projects.kryptos.tier2_contextual.fleissner_grille_sweeper` |
| Tier 2 Dual-Panel Asymmetric Sweeper | `uv run python -m projects.kryptos.tier2_contextual.dual_panel_sweeper` |
| Tier 2 Optical Tableau Sweeper | `uv run python -m projects.kryptos.tier2_contextual.optical_tableau_sweeper` |
| Tier 2 Errata & Phase Dislocation Engine | `uv run python -m projects.kryptos.tier2_contextual.errata_stencil_engine` |
| Tier 2 Berlin Clock State Machine | `uv run python -m projects.kryptos.tier2_contextual.berlin_clock_state_machine` |
| Tier 2 7-Strip Jigsaw Alignment Engine | `uv run python -m projects.kryptos.tier2_contextual.strip_jigsaw_engine` |
| Tier 2 M-138 Displaced Strip Engine | `uv run python -m projects.kryptos.tier2_contextual.m138_strip_dislocation` |
| Tier 2 Viterbi Periodic Beam Search | `uv run python -m projects.kryptos.tier2_contextual.viterbi_periodic_beam_search` |
| Tier 2 Extended Running Key Sweeper | `uv run python -m projects.kryptos.tier2_contextual.extended_running_key_sweeper` |
| Tier 2 Paired 7x7 Sheet Cut Engine | `uv run python -m projects.kryptos.tier2_contextual.paired_sheet_cut_engine` |
| Tier 2 Irregular Mask & Cardan Grille Engine | `uv run python -m projects.kryptos.tier2_contextual.irregular_mask_grille_engine` |
| Tier 2 Solar Shadow & Running Key Engine | `uv run python -m projects.kryptos.tier2_contextual.solar_shadow_running_key_engine` |
| Tier 2 Hill & Circulant Polygraphic Engine | `uv run python -m projects.kryptos.tier2_contextual.hill_affine_polygraphic_engine` |
| Tier 2 Lag-7 Feedback Recurrence Engine | `uv run python -m projects.kryptos.tier2_contextual.lag7_feedback_recurrence_engine` |
| Tier 2 Twin-Column Strip Lock Engine | `uv run python -m projects.kryptos.tier2_contextual.twin_strip_lock_engine` |
| Tier 2 Dual Independent Sheet Engine | `uv run python -m projects.kryptos.tier2_contextual.dual_independent_sheet_engine` |
| Tier 2 Physical Fold & Block Shift Engine | `uv run python -m projects.kryptos.tier2_contextual.physical_fold_block_shift_engine` |
| Tier 2 2-Phase Interlocking Mask Engine | `uv run python -m projects.kryptos.tier2_contextual.interlocking_aperture_mask_engine` |
| Tier 2 Keyed Coordinate Selection Engine | `uv run python -m projects.kryptos.tier2_contextual.keyed_coordinate_selection_engine` |
| Tier 2 Compound Double Transposition Engine | `uv run python -m projects.kryptos.tier2_contextual.compound_double_transposition_engine` |
| Tier 2 Additive Vernier Mask Engine | `uv run python -m projects.kryptos.tier2_contextual.additive_vernier_mask_engine` |
| Tier 2 VIC Straddling Checkerboard Engine | `uv run python -m projects.kryptos.tier2_contextual.vic_straddling_checkerboard_engine` |
| Tier 2 Lodestone Geodetic Projection Engine | `uv run python -m projects.kryptos.tier2_contextual.lodestone_geodetic_projection_engine` |
| Tier 2 Errata & Mixed-Alphabet Running Key Engine | `uv run python -m projects.kryptos.tier2_contextual.errata_mixed_alphabet_engine` |
| Tier 2 Polygraphic Fractionation Engine | `uv run python -m projects.kryptos.tier2_contextual.polygraphic_fractionation_engine` |
| Tier 2 Two-Sheet Piecewise Quagmire Engine | `uv run python -m projects.kryptos.tier2_contextual.two_sheet_piecewise_quagmire_engine` |
| Tier 2 Restricted Coordinate Transposition Engine | `uv run python -m projects.kryptos.tier2_contextual.restricted_coordinate_transposition_engine` |
| Tier 2 Unconstrained S7 Transposition Engine | `uv run python -m projects.kryptos.tier2_contextual.unconstrained_s7_transposition_engine` |
| Tier 2 7-Channel Stateful Progressive Autokey Engine | `uv run python -m projects.kryptos.tier2_contextual.stateful_progressive_autokey_engine` |
| Tier 2 Multi-Null & 10x10 Defect Topology Engine | `uv run python -m projects.kryptos.tier2_contextual.multi_null_defect_topology_engine` |
| Tier 2 Error-Tolerant Artisanal Composite SMT Engine | `uv run python -m projects.kryptos.tier2_contextual.error_tolerant_artisanal_smt_engine` |
| Tier 2 Two-Panel Independent Solver | `uv run python -m projects.kryptos.tier2_contextual.two_panel_independent_solver` |
| Tier 2 Transposed Key Schedule Engine | `uv run python -m projects.kryptos.tier2_contextual.transposed_key_schedule_engine` |
| Tier 2 Desynchronization Null Audit | `uv run python -m projects.kryptos.tier2_contextual.desynchronization_audit_engine` |
| Tier 2 Physical Transcriptor 31-to-7 Engine | `uv run python -m projects.kryptos.tier2_contextual.physical_transcriptor_engine` |
| Tier 2 31-Wide Tableau Stencil Engine | `uv run python -m projects.kryptos.tier2_contextual.tableau_stencil_engine` |
| Tier 2 Keyword Tableau Stencil Engine | `uv run python -m projects.kryptos.tier2_contextual.keyword_stencil_engine` |
| Tier 2 Scrambled Paper Strip Reassembly Engine | `uv run python -m projects.kryptos.tier2_contextual.scrambled_strip_reassembly` |
| Tier 2 7-Track Dynamic Autokey Engine | `uv run python -m projects.kryptos.tier2_contextual.seven_track_autokey_engine` |
| Tier 2 Irregular Key Transposition Engine | `uv run python -m projects.kryptos.tier2_contextual.irregular_scheidt_transposition` |
| Tier 2 Quagmire Dual-Keyed Slide Engine | `uv run python -m projects.kryptos.tier2_contextual.quagmire_dual_keyed_engine` |
| Tier 2 Quasigroup & Affine Inversion Engine | `uv run python -m projects.kryptos.tier2_contextual.quasigroup_tableau_inverter` |
| Tier 2 Two-Key Alternating Block Engine | `uv run python -m projects.kryptos.tier2_contextual.two_key_alternating_engine` |
| Tier 2 Constrained Multi-Core Annealer | `uv run python -m projects.kryptos.tier2_contextual.constrained_keystream_annealer` |
| Tier 2 Strip Sliding Jigsaw Solver | `uv run python -m projects.kryptos.tier2_contextual.strip_sliding_jigsaw_solver` |
| Tier 2 Dual-Square Superposition Engine | `uv run python -m projects.kryptos.tier2_contextual.dual_square_superposition_engine` |
| Tier 2 Keystone Incomplete Grid Engine | `uv run python -m projects.kryptos.tier2_contextual.keystone_incomplete_grid_engine` |
| Tier 2 Paired 7x7 Sheet Cut Engine | `uv run python -m projects.kryptos.tier2_contextual.paired_sheet_cut_engine` |
| Tier 2 Route & Columnar Sweeper | `uv run python -m projects.kryptos.tier2_contextual.route_mask_sweeper` |
| Tier 2 Cardan Stencil Sweeper | `uv run python -m projects.kryptos.tier2_contextual.cardan_stencil_sweeper` |
| Tier 2 Layer Two Coupling Sweeper | `uv run python -m projects.kryptos.tier2_contextual.cross_section_mask` |
| Tier 2 Compass & Weltzeituhr Sweeper | `uv run python -m projects.kryptos.tier2_contextual.compass_weltzeituhr_sweeper` |
| $14 \times 7$ Differential Matrix Solver | `uv run python -m projects.kryptos.tier2_contextual.matrix_solver` |
| Historical Running Key Sweeper | `uv run python -m projects.kryptos.tier2_contextual.running_key_sweep` |
| Constrained Matrix Annealer | `uv run python -m projects.kryptos.tier2_contextual.matrix_annealer` |
| Continuous Discovery Sweeper | `uv run python -m projects.kryptos.tier2_contextual.continuous_discovery` |
| Completion Standard Audit | `uv run python -m projects.kryptos.tier3_verification.completion_audit` |
| Fedora PC Remote Worker probe | `./scripts/remote_worker.sh pc "cd ~/Developer/cipher-lab && uv run pytest tests/test_kryptos.py -q"` |

## Result

**Current Formal Verdict**: **Plaintext known; decryption method unverified.**  
Archival discovery recovered the prose message, but the cryptographic transformation $E_K(P) = C$ remains unsolved. All surveyed classical and craft systems (standalone columnar transpositions across all 5,040 $S_7$ permutations, direct periodic polyalphabetic $L \le 25$, two-sheet Quagmire I–IV tableaus across all 98 null phases, Bifid period 7, planar route transpositions, 2-phase Cardan stencils, K1–K3 superposition, static keywords, Rank-1/Rank-2 bilinear modular forms, 7-channel stateful progressive autokeys, $10 \times 10$ 3-null / $14 \times 7$ dual-null defect grids, and error-tolerant artisanal 2-stage composites with $k \le 2$ defects across 61 formal pre-registered trials) have been rigorously, exhaustively, and reproducibly falsified across the multi-node compute fabric under strict blind derivation and held-out cross-validation, confirmed by Consilium Gates 24–26.

## Reproduce

```bash
uv sync --all-packages --group dev
uv run pytest tests/test_kryptos.py -q
uv run python -m projects.kryptos.tier1_blind.runner
uv run python -m projects.kryptos.tier2_contextual.kpa_algebra
uv run python -m projects.kryptos.tier2_contextual.unconstrained_s7_transposition_engine
uv run python -m projects.kryptos.tier2_contextual.stateful_progressive_autokey_engine
uv run python -m projects.kryptos.tier2_contextual.multi_null_defect_topology_engine
uv run python -m projects.kryptos.tier2_contextual.error_tolerant_artisanal_smt_engine
uv run python -m projects.kryptos.tier3_verification.completion_audit
```

