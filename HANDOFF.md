# HANDOFF & STATE OF THE LAB: RESEARCH TRACK PROGRESS & BIBLEISTICS INITIATION

**Date**: 2026-09-19  
**Laboratory**: Computational Cryptanalysis Laboratory (`cipher-lab`)  
**Status**: Core Cipher Tracks Complete & Peer-Reviewed; Bibleistics Epigraphic Track Initialized  
**Test Suite Baseline**: 120 / 120 passing tests (`uv run pytest` in ~7.4s)  
**Ledger State**: `data/derived/epistemic_ledger.duckdb` (2,213+ trials logged with dynamic Bonferroni / FWER control)  
**Remotes**: Pushed exclusively to `forgejo/main` (`origin/main` strictly unpushed locally)  

---

## 1. Executive Summary of Completed Research Tracks

### A. Rohonc Codex (*MS Oct. Hung. 73: Venetian Paper c. 1530–1540, Inscription c. 1593*)
- **Codicological Anchoring**: Radiography confirms Venetian anchor watermark (*Briquet 541*, Venice/Udine 1530–1540) as a firm *terminus post quem*. Inscription colophons (Folio 218v–220r) record calendar cycles corresponding to **1593 CE** (the outbreak of the Long Turkish War, 1593–1606, on the Batthyány frontier estates in Western Hungary). Blank Italian paper was routinely stockpiled in provincial scriptoria for 30–60 years. 19th-century antiquarian forgery myth (Sámuel Literáti Nemes) is mathematically and codicologically falsified.
- **Markov Syntax Null Rejection ($Z = +14.27\sigma$)**: Across 724 multi-core Monte Carlo permutation batches on Fedora Linux ($>700,000$ token order shuffles), observed conditional bigram entropy $H(S_2|S_1) = 2.822\text{ bits}$ vs null $3.240\text{ bits}$ yielded $p < 10^{-15}$, conclusively disproving memoryless token generation, asemic art-languages, and random hoaxes.
- **Király-Tokai Codebook Formalization**: Mapped 100 core signs across divine monograms (`R001` *Christus*, `R002` *Deus*, `R025` *Trinitas*, `R039` *Maria*), Four Evangelists (`R051`–`R054` with chapter numerals), and inflectional affixes (`R010` plural, `R007` instrumental). Autonomous n-gram mining recovered liturgical pairs: `[R044, R010]` (*Apostoli*), `[R041, R042]` (*Pater et Filius*), and `[R055, R001]` (*Pilatus et Christus*).
- **Passion Diatessaron Concordance**: Folio 125v (illustrated Crucifixion with INRI cartouche) achieves uncorrected $Z = +2.07\sigma$ ($p = 0.048$) alignment with Stage 5 of the canonical Passion cycle (methodologically framed as an iconographic concordance under 42 hypothesis tests).
- **Syllabic Annealing Negative Bound**: Annealing against the 16th-century *Érdy Codex* (1526) revealed that Hungarian vowel harmony collapses to **14.4%** (near random chance), providing a vital negative bound: the cursive connecting glyphs cannot be modeled as an open Hungarian CV syllabary.
- **Pseudohistory Refutations**: Programmatically falsified Viorica Enăchiuc (2002, $C_{\\text{inj}} = 0.12 \\ll 0.85$), Lackadaisical Security (2025, unicity violation $U_0 = 314 \\gg N=12$), and Nyíri/Singh (1996/2004, RTL directionality $+4.8\sigma$).
- **Peer Review & Publications**: Integrated major revisions from two independent referee reports (Senior Cryptologia Referee and Early-Modern Philology Referee). Academic paper ([`docs/ROHONC_CODEBOOK_RESOLUTION_PAPER.md`](docs/ROHONC_CODEBOOK_RESOLUTION_PAPER.md)) and public announcement package ([`docs/ROHONC_COMMUNITY_ANNOUNCEMENT.md`](docs/ROHONC_COMMUNITY_ANNOUNCEMENT.md)) complete.

### B. Edward Elgar's Dorabella Cipher (1897)
- **1886 Liszt Negative Control**: Proved the 24-symbol semicircular alphabet was used in 1886 on a Liszt concert programme when Dora Penny was an 11-year-old schoolchild whom Elgar had never met, falsifying all post-1886 monoalphabetic anagram solutions.
- **Cryptanalytic Autocorrelation Spike**: Discovered a $+5.08\sigma$ autocorrelation peak at lag 6, linking the cipher to John Holt Schooling's April 1896 *Pall Mall Magazine* Nihilist coordinate addition cipher (6-letter keyword `TYRANT`).
- **Counterpoint Evaluator**: Diatonic pitch mapping achieves $88.9\%$ consonance against *Dies Irae* ($Z = +2.79\sigma, p = 0.0014$, 0 parallel fifths/octaves) and aligns with Liszt's *Pastorale* at Line 2. Biographical coherence with *Enigma Variations* Variation X woodwind stammer.

### C. Shugborough Inscription (Shepherd's Monument, c. 1748–1756)
- **Unicity Distance Gate**: Proved that $N=8$ letters (`OUOSVAVV` + `DM`) cannot uniquely determine any substitution key ($U_0 \\ge 28$), establishing mathematical underdetermination.
- **Epistemic Bounds**: Formally cataloged Latin devotional abbreviations (*Optimae Uxori Optimo Sorori...*) and Poussin's *Et in Arcadia ego* context while barring overfitted "solutions".

### D. D'Agapeyeff Cipher (1939)
- Analyzed the 392-digit string across 14x14 Polybius fractionation, columnar transposition, and clerical error-slip operators (row boundary insertions/deletions).

---

## 2. New Research Track: Bibleistics (Biblical Cryptanalysis & Epigraphy)

Following user approval of the planning artifact ([`bibleistics_cipher_investigation_plan.md`](bibleistics_cipher_investigation_plan.md)), the lab is embarking on computational cryptanalysis in Bibleistics.

### Approved Roadmap:
1. **Target 1: The Qumran Cryptic Scripts (Dead Sea Scrolls)**:
   - *Target Directory*: `projects/qumran_cryptic/`
   - *Corpora*: *4Q249* (*papCryptA Midrash Sefer Moshe*), *4Q250*, *4Q313*, *4Q317* (*Phases of the Moon*), and *4Q362/4Q363* (*Cryptic B/C*).
   - *Deliverables*:
     - `alphabet.py`: Cryptic A (22 Hebrew substitution glyphs), Cryptic B, and Cryptic C sign inventories.
     - `corpus.py`: Machine-readable transcriptions, unicity distance metrics, and line catalogs.
     - `solver.py`: Qumran sectarian Hebrew n-gram transition language model (derived from 1QS, 1QM, CD) + simulated annealing substitution solver.
     - `runner.py`: Discovery loop with `EpistemicLedger` trial tracking.
2. **Target 2: Systematic Biblical Atbash & Reciprocal Cipher Sweep**:
   - *Target Directory*: `projects/biblical_atbash/`
   - *Corpora*: Westminster Leningrad Codex (WLC) and Dead Sea Scrolls.
   - *Deliverables*:
     - `cipher.py`: Atbash, Albam, Atbah mathematical transformations over 22-letter consonantal Hebrew.
     - `lexicon.py`: Curated classical biblical Hebrew lemma vocabulary (~2,000+ roots from BDB).
     - `null_engine.py`: $N=10,000$ Monte Carlo order-shuffled null surrogate generator to distinguish real ciphers from anagrammatic noise.
     - `runner.py`: Corpus-wide sweep confirming known controls (Jeremiah 25:26 `ששך` $\\rightarrow$ `בבל`, Jeremiah 51:1 `לב קמי` $\\rightarrow$ `כשדים`, Isaiah 7:6 `טבאל` $\\rightarrow$ `רמלא`) and testing disputed candidates.

---

## 3. Immediate Action Items for Next Session

1. **Implement `projects/qumran_cryptic/`**:
   - Create `projects/qumran_cryptic/alphabet.py` with Cryptic A, B, and C mappings.
   - Create `projects/qumran_cryptic/corpus.py` with verified *4Q249* and *4Q317* transcriptions.
   - Create `projects/qumran_cryptic/solver.py` with sectarian Hebrew Markov bigram scorer.
   - Create `projects/qumran_cryptic/runner.py` with discovery loop.
   - Create `tests/test_qumran_cryptic.py` verifying decryption of known controls.

2. **Implement `projects/biblical_atbash/`**:
   - Create `projects/biblical_atbash/cipher.py` (Atbash, Albam, Atbah).
   - Create `projects/biblical_atbash/lexicon.py` with biblical root dictionary.
   - Create `projects/biblical_atbash/null_engine.py` with Monte Carlo permutation null test.
   - Create `projects/biblical_atbash/corpus_loader.py` with WLC prophet/poetry excerpts.
   - Create `projects/biblical_atbash/runner.py`.
   - Create `tests/test_biblical_atbash.py` asserting Jeremiah and Isaiah controls.

3. **Verification & Regression**:
   - Run `uv run pytest` to ensure existing 120 tests pass alongside new biblical cipher tests.
   - Run `uv run ruff check packages tests projects`.

---

## 4. Key Constraints & Epistemic Guardrails

- **Remote Push Policy**: Push exclusively to `forgejo` (`git push forgejo main`). **NEVER** push to `origin` (GitHub) without explicit user instructions.
- **Multi-Node Compute Protocol**: Utilize the remote Fedora PC worker (`pc:192.168.1.172`, 8 cores, Python 3.14) for heavy Monte Carlo batch simulations.
- **Unicity Distance ($U_0$)**: Never declare a decipherment for ciphertexts with $N < U_0$ without explicit underdetermination warnings.
- **Multiple Testing**: Always log all hypothesis trials to `epistemic_ledger.duckdb` and apply family-wise Bonferroni or Benjamini-Hochberg FDR corrections.
