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
- [ ] **Qumran Cryptic Scripts (`projects/qumran_cryptic/`)**:
  - [ ] Create `alphabet.py`: Cryptic A, B, and C character bijection inventories.
  - [ ] Create `corpus.py`: Catalog *4Q249* (*papCryptA Midrash Sefer Moshe*), *4Q313*, *4Q317*.
  - [ ] Create `solver.py`: Qumran sectarian Hebrew Markov n-gram model (1QS, 1QM, CD).
  - [ ] Create `runner.py`: Connect to DuckDB epistemic ledger.
  - [ ] Create `tests/test_qumran_cryptic.py`.
- [ ] **Biblical Atbash Sweep (`projects/biblical_atbash/`)**:
  - [ ] Create `cipher.py`: Atbash, Albam, and Atbah transformations over consonantal Hebrew.
  - [ ] Create `lexicon.py`: Curated classical Hebrew lemma dictionary.
  - [ ] Create `null_engine.py`: $N=10,000$ Monte Carlo order-shuffled surrogate generator.
  - [ ] Create `runner.py`: Corpus-wide sweep confirming Jeremiah 25:26 (`ששך` -> `בבל`) and testing disputed candidates.
  - [ ] Create `tests/test_biblical_atbash.py`.

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
  - [x] Implement 138/138 passing automated tests across macOS Darwin (Python 3.12) and Fedora Linux (Python 3.13).
