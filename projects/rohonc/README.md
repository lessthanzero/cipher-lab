# Rohonc Codex Investigation: Codebook & Liturgical Resolution

- **Manuscript**: Rohonc Codex (*Rohonci kódex*, Batthyány Collection, Hungarian Academy of Sciences, MS Oct. Hung. 73)
- **Origin**: Central Europe (Batthyány family castle, Rohonc / Rechnitz, Austria; donated 1838)
- **Codicological Date**: c. 1530–1550 (Venetian anchor watermark Briquet 541 dated 1530–1540; internal date 1593 CE)
- **Dimensions & Scale**: 448 pages, ~87,000 characters, ~150 core signs (~790 compound variants), 87 Christian illustrations
- **Scientific Paradigm**: Early-modern tachygraphic codebook/syllabary (Király & Tokai 2018; Láng 2021)
- **Academic Preprint**: [`docs/ROHONC_CODEBOOK_RESOLUTION_PAPER.md`](file:///Users/sashakatin/Developer/cipher-lab/docs/ROHONC_CODEBOOK_RESOLUTION_PAPER.md)

---

## 1. Key Computational Findings

1. **Information-Theoretic Rigor ($N \gg U_0$)**:
   - Zipf-Mandelbrot rank-frequency parameterization ($\gamma = 1.86, \beta = 8.00, R^2 = 0.907$).
   - Conditional bigram entropy $H(S_2|S_1) = 2.822\text{ bits}$.
   - Syntax Monte Carlo permutation test ($N=10,000$ permutations on Fedora PC): $Z = +14.27\sigma$ ($p < 10^{-15}$). Rejects random noise, modern hoax, and asemic art-language hypotheses.
2. **Király-Tokai Codebook Architecture**:
   - Formalized 50 diagnostic codebook entries: Divine monograms (`R001` Christus, `R002` Deus, `R025` Trinitas, `R039` Sancta Maria), Four Evangelists (`R051` Matthew, `R052` Mark, `R053` Luke, `R054` John), Passion actors (`R055` Pilate, `R056` Judas, `R057` Peter, `R060` Soldiers), Sacraments (`R061` Chalice, `R062` Bread/Host, `R080` Sepulchre), and affixes (`R010` Plural, `R007` Instrumental).
3. **Formulaic Collocation Discovery**:
   - Autonomous extraction of recurrent liturgical pairs: `[R044, R010]` (*Apostoli*, frequency 9), `[R041, R042]` (*Pater et Filius*), `[R032, R039]` (*Angelus + Maria*, Annunciation), `[R055, R001]` (*Pilatus + Christus*), `[R039, R054]` (*Maria + Iohannes* beneath the Cross).
4. **Liturgical Diatessaron Harmony Alignment**:
   - Dynamic sequence alignment against the 6-stage canonical Passion narrative. Folio 125v (illustrated Crucifixion) achieves statistically significant alignment ($Z = +2.07\sigma, p = 0.048$).
5. **Pseudohistory Falsification**:
   - Programmatic mathematical refutations of the Sámuel Literáti Nemes forgery myth, Viorica Enăchiuc (2002) Dacian battle chronicle, Lackadaisical Security (2025) rotational Old Romanian cipher, and Sumerian/Hindi claims.

---

## 2. Directory Structure

```
projects/rohonc/
├── corpus.py               # Core sign catalog (80 signs), 12 RTFF families, transcribed folios
├── stats.py                # Zipf-Mandelbrot fitting, entropy profiling, directionality audit
├── codebook.py             # Király-Tokai 50-entry codebook, NER scanner, cluster discovery
├── liturgical_aligner.py   # 6-stage Passion Diatessaron alignment & Monte Carlo scoring
├── debunker.py             # Mathematical falsification suite for pseudohistorical claims
├── discovery_mac.py        # Local Apple Silicon worker for codebook refinement & entity scanning
├── discovery_pc.py         # Remote Fedora PC worker for large-scale Monte Carlo null sweeps
└── runner.py               # Master CLI orchestrator with DuckDB epistemic ledger logging
```

---

## 3. How to Reproduce

### Run Full Epigraphic & Codebook Pipeline
```bash
# Execute end-to-end epigraphic gating, codebook extraction, liturgical alignment, and debunker
uv run python -m projects.rohonc.runner --mode all --permutations 1000
```

### Run Local Darwin Discovery Cycle
```bash
uv run python -m projects.rohonc.discovery_mac
```

### Run Distributed Monte Carlo Null Permutations on Remote PC
```bash
uv run python -m projects.rohonc.discovery_pc --permutations 2000
```

### Run Automated Test Suite
```bash
uv run pytest tests/test_rohonc*.py -v
```
