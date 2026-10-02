# Laboratory Action Items & Strategic Roadmap

## Phase 1: Visibility Operations & Upstream PR Tracking
- [ ] **GitHub Pages Verification**:
  - [ ] Confirm `cipher-lab` Settings → Pages → Source is set to **GitHub Actions**.
  - [ ] Verify live deployment of the interactive research essay at `https://lessthanzero.github.io/cipher-lab/`.
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
- [ ] **Prototype Scaffolding**:
  - [ ] Initialize standalone repository `/Users/sashakatin/Developer/episteme-canvas` (React/Svelte + Canvas/SVG).
  - [ ] Implement Decision DAG rendering engine adhering to [`docs/episteme_spec/AGENT_EVENT_SCHEMA.json`](docs/episteme_spec/AGENT_EVENT_SCHEMA.json).
  - [ ] Implement tactile time-travel scrubber and rewind/forking primitives.
- [ ] **Epistemic Lens Integration**:
  - [ ] Build visual confidence scoring component displaying Bonferroni/FDR thresholds.
  - [ ] Implement blinded foil failure indicator on candidate hypothesis nodes.
- [ ] **OpenTelemetry Integration**:
  - [ ] Build lightweight OpenTelemetry AI trace adapter to stream live agent runs from LangGraph / custom Python loops.

---

## Phase 4: Competitive Hackathon Readiness
- [ ] **Frontier AI Agent Hackathons**:
  - [ ] Track calendar for upcoming AI Engineer World's Fair / London AI hackathons.
  - [ ] Prepare two-minute live video demo of the Episteme interactive steering canvas.
- [ ] **ScienceTech & Lab Automation Sprints**:
  - [ ] Monitor Francis Crick Institute Innovation Challenge and BioHackathon Europe dates.
  - [ ] Prepare case study showcasing Elsevier research UX and lab automation robotics workflows.

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
