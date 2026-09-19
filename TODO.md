# TODO & Action Items: Biblical Cryptanalysis & Epigraphy Track

## Phase 1: Qumran Cryptic Scripts (`projects/qumran_cryptic/`)
- [ ] Create `projects/qumran_cryptic/alphabet.py`:
  - [ ] Implement Cryptic A signary (22 Hebrew substitution glyphs with descriptions & transliteration tokens).
  - [ ] Implement Cryptic B and Cryptic C sign inventories.
- [ ] Create `projects/qumran_cryptic/corpus.py`:
  - [ ] Catalog *4Q249* (*papCryptA Midrash Sefer Moshe*).
  - [ ] Catalog *4Q250* (*Text Concerning the Spirits*).
  - [ ] Catalog *4Q313* (*Creation & Sabbath Shirot*).
  - [ ] Catalog *4Q317* (*Phases of the Moon* Enochic lunar calendar).
  - [ ] Catalog *4Q362/4Q363* (*Cryptic B* fragments).
- [ ] Create `projects/qumran_cryptic/solver.py`:
  - [ ] Build Qumran sectarian Hebrew Markov n-gram language model (1QS, 1QM, CD).
  - [ ] Build simulated annealing substitution solver.
- [ ] Create `projects/qumran_cryptic/runner.py`:
  - [ ] Connect to `EpistemicLedger` in `data/derived/epistemic_ledger.duckdb`.
- [ ] Create `tests/test_qumran_cryptic.py`:
  - [ ] Verify Cryptic A character bijection.
  - [ ] Verify decryption of known *4Q249* passages.

## Phase 2: Systematic Biblical Atbash & Reciprocal Ciphers (`projects/biblical_atbash/`)
- [ ] Create `projects/biblical_atbash/cipher.py`:
  - [ ] Implement Atbash ($\\aleph \\leftrightarrow \\text{ת}, \\beth \\leftrightarrow \\text{ש}, \\dots$).
  - [ ] Implement Albam ($\\aleph \\leftrightarrow \\text{ל}, \\beth \\leftrightarrow \\text{מ}, \\dots$).
  - [ ] Implement Atbah (pairs summing to 10 or 100).
- [ ] Create `projects/biblical_atbash/lexicon.py`:
  - [ ] Build curated classical Biblical Hebrew root/lemma vocabulary (~2,000+ entries from BDB).
- [ ] Create `projects/biblical_atbash/corpus_loader.py`:
  - [ ] Load curated prophetic and poetic texts (Jeremiah 25, 51; Isaiah 7; Job 20-21; Ezekiel 23).
- [ ] Create `projects/biblical_atbash/null_engine.py`:
  - [ ] Build $N=10,000$ Monte Carlo order-shuffled surrogate generator to calculate empirical Z-scores and FDR-adjusted p-values for dictionary collisions.
- [ ] Create `projects/biblical_atbash/runner.py`:
  - [ ] Execute corpus scan and record trials to `EpistemicLedger`.
- [ ] Create `tests/test_biblical_atbash.py`:
  - [ ] Test Jeremiah 25:26 `ששך` -> `בבל` (Atbash).
  - [ ] Test Jeremiah 51:1 `לב קמי` -> `כשדים` (Atbash).
  - [ ] Test Isaiah 7:6 `טבאל` -> `רמלא` (Albam).

## Phase 3: Verification & Integration
- [ ] Run full test suite: `uv run pytest` (target: 100% passing).
- [ ] Run linter: `uv run ruff check packages tests projects`.
- [ ] Commit and push exclusively to `forgejo/main`.
