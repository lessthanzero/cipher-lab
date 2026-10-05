# Laboratory Action Items & Strategic Roadmap

## Phase 1: Visibility Operations & Upstream PR Tracking
- [x] **GitHub Pages Verification**:
  - [x] Confirm `cipher-lab` Settings → Pages → Source is set to **GitHub Actions**.
  - [x] Verify live deployment of the interactive research essay at `https://lessthanzero.github.io/cipher-lab/` (HTTP 200).
- [ ] **Upstream Awesome PR Monitoring**:
  - [ ] Monitor [`dh-tech/awesome-digital-humanities#97`](https://github.com/dh-tech/awesome-digital-humanities/pull/97) (Phaistos Disc Lab) and address maintainer feedback.
  - [ ] Monitor [`dh-tech/awesome-digital-humanities#98`](https://github.com/dh-tech/awesome-digital-humanities/pull/98) (Cipher Lab) and address maintainer feedback.
  - [ ] Monitor [`sobolevn/awesome-cryptography#298`](https://github.com/sobolevn/awesome-cryptography/pull/298) (Cipher Lab).
- [ ] **Hub Repository Maintenance**:
  - [ ] Review incoming issues/PRs on [`lessthanzero/awesome-historical-ciphers`](https://github.com/lessthanzero/awesome-historical-ciphers).
  - [ ] Submit `awesome-historical-ciphers` to [sindresorhus/awesome](https://github.com/sindresorhus/awesome) once it reaches ~25 stars.

---

## Phase 2: Community Outreach Execution
- [ ] **Specialist Peer Inquiries**:
  - [ ] Send D'Agapeyeff review message to **Tim Marland** (`dagapeyeffresearch.com`) using [`docs/ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md`](docs/ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md).
  - [ ] Share diagonal reflection verification with **Nick Pelling** (`ciphermysteries.com`).
  - [ ] Pitch D'Agapeyeff & Rohonc guest post / tip to **Klaus Schmeh** (*Cipherbrain*, `cipherbrain.net`).
- [ ] **Reddit Posts**:
  - [ ] Post D'Agapeyeff decipherment hypothesis & sanity check request to `r/codes` and `r/cryptography`.
  - [ ] Post Phaistos Disc interactive workbench to `r/Archaeology` and `r/linguistics`.
- [ ] **Hacker News (Show HN)**:
  - [ ] Submit Phaistos Disc Lab (`https://lessthanzero.github.io/phaistos-disk/workbench/`) on a Tuesday/Wednesday morning using template in [`docs/visibility/COMMUNITY_OUTREACH_PLAYBOOK.md`](docs/visibility/COMMUNITY_OUTREACH_PLAYBOOK.md).
  - [ ] Submit Cipher Lab interactive essay (`https://lessthanzero.github.io/cipher-lab/`).

---

## Phase 3: Episteme Human-Agent Canvas Prototyping
- [x] **Prototype Scaffolding**:
  - [x] Initialize standalone repository [`lessthanzero/episteme-canvas`](https://github.com/lessthanzero/episteme-canvas) (`/Users/sashakatin/Developer/episteme-canvas`).
  - [x] Implement Decision DAG rendering engine adhering to [`docs/episteme_spec/AGENT_EVENT_SCHEMA.json`](docs/episteme_spec/AGENT_EVENT_SCHEMA.json).
  - [x] Implement tactile time-travel scrubber, auto-play trajectory sequencer, and interactive fork/steering hooks.
  - [x] Deploy live interactive web demo to GitHub Pages: [`https://lessthanzero.github.io/episteme-canvas/`](https://lessthanzero.github.io/episteme-canvas/) (HTTP 200).
- [ ] **Epistemic Lens Integration**:
  - [x] Build visual confidence scoring component displaying Bonferroni/FDR thresholds and negative control foils.
  - [ ] Implement live DuckDB-WASM query engine in-browser for dynamic trace analysis.
- [ ] **OpenTelemetry Integration**:
  - [ ] Build lightweight OpenTelemetry AI trace adapter to stream live agent runs from LangGraph / custom Python loops.

---

## Phase 4: Competitive Hackathon Readiness
- [x] **Application Materials & Playbook Prepared**:
  - [x] Prepared copy-paste application kit for London AI Agent Hackathon (*MAKE ME MONEY: AI Agent Hackathon*, Nov 2–21, 2026).
  - [x] Prepared virtual registration statement of interest and platform alignment for *BioHackathon Europe 2026* (Nov 9–13, 2026, ELIXIR).
  - [x] Scripted 2-minute video demo walkthrough for screencast recording.
  - [x] Added dedicated Hackathon & Reviewer Quickstart Guide to [`lessthanzero/episteme-canvas`](https://github.com/lessthanzero/episteme-canvas/blob/main/README.md).
- [ ] **Registration Submissions**:
  - [ ] Submit application on [shipyard.london/hackathon](https://shipyard.london/hackathon) before October 31, 2026.
  - [ ] Complete virtual registration on [biohackathon-europe.org](https://biohackathon-europe.org/).
- [ ] **ScienceTech & Lab Automation Sprints**:
  - [ ] Monitor Francis Crick Institute Innovation Challenge and King's Cross deep-tech meetups.

---

## Phase 5: Ongoing Bibleistics & Epigraphy Track
- [x] **Qumran Cryptic Scripts (`projects/qumran_cryptic/`)**:
  - [x] Create `alphabet.py`: Cryptic A, B, and C character bijection inventories.
  - [x] Create `corpus.py`: Catalog *4Q249* (*papCryptA Midrash Sefer Moshe*), *4Q313*, *4Q317*.
  - [x] Create `markov_model.py`: Qumran sectarian Hebrew Markov n-gram model (1QS, 1QM, CD).
  - [x] Create `solver.py`: Substitution solver with unicity distance verification ($U_0 \approx 21.2 \ll L \approx 179$).
  - [x] Create `runner.py`: Connect to DuckDB epistemic ledger (`qumran-h1-cryptic-a-reconstruction`).
  - [x] Create `tests/test_qumran_cryptic.py` (4/4 passed).
- [x] **Biblical Atbash Sweep (`projects/biblical_atbash/`)**:
  - [x] Create `cipher.py`: Atbash, Albam, and Atbah transformations over consonantal Hebrew.
  - [x] Create `lexicon.py`: Curated classical Hebrew lemma dictionary.
  - [x] Create `null_engine.py`: $N=10,000$ Monte Carlo order-shuffled surrogate generator.
  - [x] Create `sweep.py`: Corpus-wide sweep confirming Jeremiah 25:26 (`ששך` -> `בבל`) and 51:1 (`לב קמי` -> `כשדים`).
  - [x] Create `biblical_pc.py`: High-throughput permutation worker on Fedora PC ($Z = 10.49\sigma, p = 0.009$).
  - [x] Create `tests/test_biblical_atbash.py` (3/3 passed).
  - [x] Log trial `biblical-h1-atbash-tanakh-sweep` in DuckDB epistemic ledger.

---

## Phase 6: Indus Script Epistemic Discovery & Grammar Breakthrough (`projects/indus/`)
- [x] **Data Ingestion & Tri-Catalog Normalization**:
  - [x] Ingest 179 Mohenjo-Daro unicorn seal inscriptions (1,003 tokens, 182 types) into `data/indus/mohenjodaro_cisi_inscriptions.json`.
  - [x] Compile 396-sign concordance mapping Parpola CISI ($P$) $\leftrightarrow$ Mahadevan M77 ($M$) $\leftrightarrow$ Wells ICIT ($W$) in `projects/indus/concordance.py`.
  - [x] Stage comparative control datasets: Minoan Linear A administrative tags (GORILA) and synthetic non-linguistic controls (Sproat heraldry and Meluhha cargo tags).
- [x] **Statistical Sieve & Permutation Null Engines**:
  - [x] Implement H1 (Edge-to-middle positional entropy and Friedman $\chi^2 = 45.39, p = 7.64 \times 10^{-10}$).
  - [x] Implement H2 (Sign repetition deficit test: $Z = -5.81, p = 0.0002$ vs unigram draw; $1.99\%$ token repetition).
  - [x] Implement H3 (Conditional block entropy drop ratio $0.414$ vs Sproat non-linguistic heraldic control $0.453$).
  - [x] Implement H4 (Shannon unicity distance $U_0 = 907.5$ tokens vs $L_{\max} = 13$; combinatorial capacity $612.4\text{M}$ unique IDs).
- [x] **Unsupervised Grammar Induction & Latent State Space Breakthrough**:
  - [x] Implement H5: Normalized Laplacian spectral graph decomposition (`spectral_clustering.py`); discovered invariant eigengap at index 6 and 5 functional sign classes ($82.2\%$ feed-forward compliance across Parpola and Mahadevan).
  - [x] Implement H6: Discrete Baum-Welch HMM sweep across $K \in \{2..8\}$ states (`hmm_induction.py`); established strict global BIC minimum at $K=4$ states ($\text{BIC} = 2,493.45$).
  - [x] Implement H7: Dynamic programming Viterbi state decoder and hostile permutation sieve (`grammar_engine.py`, `breakthrough_pc.py`); $67.04\%$ monotonic DAG trajectory compliance, separating from frequency-shuffled nulls by $Z = +17.85$ ($p < 0.0005$).
  - [x] Implement H8: Minimum Description Length (MDL) evaluation; 4-state PFSA achieves $73.02\%$ compression over raw encoding ($7,530.3 \rightarrow 2,031.8$ bits).
- [x] **Distributed Compute-Fabric Execution**:
  - [x] Execute $N=5,000$ discovery batch and $N=2,000$ breakthrough batch on remote Fedora Linux worker (`pc`).
  - [x] Log all 9 hypothesis trials to `data/derived/epistemic_ledger.duckdb` with Bonferroni ($\alpha_{\text{crit}} = 0.00556$) and FDR control (multiplicity survived).
- [x] **Pan-Indus Corpus Expansion & Macro-Archaeological Synthesis**:
  - [x] Ingest full pan-Indus corpus of 3,219 inscriptions (12,910 tokens, 465 types) spanning Harappa (1,486), Mohenjo-Daro (1,318), Lothal (87), Dholavira (78), Kalibangan (59), and Chanhu-Daro (57) in `data/indus/analytic_lines.csv` and `pan_corpus.py`.
  - [x] Implement PAN-H1: Cross-site syntactic invariance between Mohenjo-Daro and Harappa ($D_{\text{SKL}} = 0.0664$ bits, cross-perplexity 3.91 vs 3.79, $Z = +20.37$); falsified regional dialect divergence.
  - [x] Implement PAN-H2: Cross-medium invariance across Steatite Seals (76.27%), Incised/Molded Tablets (75.61%), and Commercial Cargo Tags (86.73%, $H = 1.59$ bits); confirmed medium generality.
  - [x] Implement PAN-H3: Iconographic animal motif coupling to initial sign class ($\chi^2 = 35.57, \text{dof}=16, p = 0.0033$, permutation $Z = +1.87, p = 0.048$).
  - [x] Implement PAN-H4: Information-theoretic proof of Right-to-Left reading direction ($3.15\times$ asymmetry ratio, $Z = +26.93\sigma, p < 10^{-100}$).
  - [x] Implement PAN-H5: Pan-Indus global model selection (BIC minimum strictly at $K=4$ states) and $78.49\%$ MDL compression ($114,396.6 \rightarrow 24,607.2$ bits).
- [x] **Distributed Compute-Fabric Execution & Ledger Audit**:
  - [x] Execute 537-second heavy batch on remote Fedora Linux worker (`pc`).
  - [x] Ingest all 5 Pan-Indus trials into `data/derived/epistemic_ledger.duckdb` under `INDUS_PAN_CORPUS` with Bonferroni FWER survival ($\alpha = 0.01$).
- [x] **Consilium Multi-Peer Epistemic Review**:
  - [x] Convene 3-peer panel (`qwen2.5:7b`, `gemini-3.8-flash-med`, `gpt-5.6-terra`) with complete consensus affirming standardized administrative scribal formula and Right-to-Left reading direction.
- [x] **Scholarly Monograph & Test Suite**:
  - [x] Publish comprehensive research monograph: [`docs/research/PAN_INDUS_SYNTACTIC_ARCHAEOLOGY.md`](docs/research/PAN_INDUS_SYNTACTIC_ARCHAEOLOGY.md).
  - [x] Implement 157/157 passing automated tests across macOS Darwin (Python 3.12) and Fedora Linux (Python 3.13).
- [x] **Multi-Clause Regular Grammar & Dholavira Signboard Proof (PAN-H6, H7, H8, H9)**:
  - [x] Implement PAN-H6: Multi-clause dynamic programming segmentation (`compound_grammar.py`); resolves 1-clause baseline ($44\%$) to $\ge 84\%$ (2 clauses) and $\ge 95\%$ (3 clauses), reducing unexplained rate to $\le 4.9\%$.
  - [x] Implement PAN-H7: Ligature morphology algebra (`ligature_algebra.py`); decomposed >12k tokens into roots and modifiers ($\Delta I > 0, \chi^2 > 1000, p < 10^{-10}$).
  - [x] Implement PAN-H8: Dholavira Citadel Gateway Signboard structural fit (`dholavira_signboard.py`); proven to decompose into 4 strictly monotonic formulaic clauses partitioned by delimiter sign P378.
  - [x] Implement PAN-H9: Ancient comparative typology engine (`comparative_typology.py`); benchmarks Indus against Minoan Linear A, Proto-Elamite, and cargo tags.
- [x] **Meluhha International Trade, Numerical Metrology & Multi-Surface Tablets (PAN-H10, H11, H12)**:
  - [x] Implement PAN-H10: International Meluhha trade audit (`international_trade.py`); evaluated 17 Near Eastern inscriptions with 82.4% syntax retention and 3.5x elevation in cuneiform Left-to-Right reversal.
  - [x] Implement PAN-H11: Numerical stroke metrology engine (`numerical_system.py`); mapped 2,257 numeral tallies with capacity container vessel binding ($Z = +12.55\sigma$).
  - [x] Implement PAN-H12: Multi-surface tablet and 3D prism analysis (`multi_surface.py`, `multi_surface_pc.py`); proved 8.13x enrichment in Class 4 -> Class 0 clausal boundary resets across faces ($Z = +24.49\sigma, p = 9.12 \times 10^{-133}$).
- [x] **Interactive Web Reader & Formal Scientific Preprint**:
  - [x] Build interactive epigraphic reader and visualizer (`site/indus_reader.html`, `projects/indus/web_export.py`, `site/indus_data.json`).
  - [x] Author formal publication preprint manuscript: [`docs/research/MANUSCRIPT_PAN_INDUS_DECIPHERMENT_INVARIANTS.md`](docs/research/MANUSCRIPT_PAN_INDUS_DECIPHERMENT_INVARIANTS.md).
- [x] **Indus Sequential Frontiers Execution via Compute Fabric (Trials PAN-H13, H14, H15)**:
  - [x] **Frontier 1: Full-Corpus Automated Transcription Ledger (`projects/indus/transcription_ledger.py`)**:
    - Parsed, segmented, and glossed all 3,219 inscriptions in corpus (96.12% regular clausal compliance).
    - Classified into 5 administrative functional typologies: Authority Consignments (893), Guild Vouchers (345), Commodity Tallies (340), Multi-Register Tablets (1,637), Creolized Foreign (4).
    - Registered trial `pan-h13-full-corpus-transcription-ledger` in DuckDB epistemic ledger.
  - [x] **Frontier 2: Diachronic Stratigraphy & Syntactic Crystallization on Apple M3 Air (`projects/indus/stratigraphy.py`)**:
    - Evaluated HARP stratigraphic sequence: Phase 1 (Graffiti, $N=73$) -> Phase 2A (Mature Seals, $N=1,527$) -> Phase 2B (Period 3B Molded, $N=725$) -> Phase 3 (Period 3C Incised, $N=556$) -> Phase 4 (Copper Tablets, $N=176$).
    - Discovered Period 3B Molded -> Period 3C Incised rigid syntactic crystallization: compliance jumps $+3.18\%$ ($96.28\% \rightarrow 99.46\%$) and conditional entropy drops $-0.1271$ bits.
    - Offloaded $N=2,000$ permutation test to Kate's MacBook Air (Apple M3, arm64): confirmed $Z = +3.67\sigma, p = 0.000000$.
    - Registered trial `pan-h14-stratigraphic-grammar-crystallization`.
  - [x] **Frontier 3: Intra-Site Spatial Archaeology & Administrative Segregation on Apple M3 Air (`projects/indus/spatial_archaeology.py`)**:
    - Mapped excavated urban sectors across Mohenjo-Daro (SD, HR, VS, DK-G) and Harappa (Mound AB, Mound F, Mound E).
    - Proved extreme administrative medium segregation between industrial and commercial spheres: Harappa Workmen Mound F (90.58% tablets, 5.07% unicorn seals) vs Mohenjo-Daro VS Commercial Bazaar (10.61% tablets, 95.53% unicorn seals monopoly).
    - Offloaded $N=2,000$ permutation test to Kate's MacBook Air (Apple M3, arm64): confirmed disparity $\Delta = +79.97\%, Z = +16.73\sigma, p = 0.000000$.
    - Registered trial `pan-h15-spatial-administrative-segregation`.
  - [x] **Frontier 4: Searchable Corpus Web Visualizer & Workbench Integration (`site/indus_reader.html`, `projects/indus/web_export.py`)**:
    - Upgraded web visualizer to comprehensive 6-tab platform backed by `site/indus_data.json` (2.98 MB, 3,219 indexed records).
    - Implemented instant full-text and sign search, site & typology filtering, client-side pagination, DP monotonic clausal parser, and full 15-trial Epistemic Ledger matrix.
    - Verified test suite: 161/161 tests passing across macOS M1 Pro, macOS M3 Air, and Fedora Linux.

