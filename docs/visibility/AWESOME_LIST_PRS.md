# Awesome List Pull Request Packages

This guide contains copy-paste ready pull request branches, titles, descriptions, and git patches for submitting `cipher-lab` and `phaistos-disk` to top curated "Awesome" repositories.

---

## 1. `dh-tech/awesome-digital-humanities`

- **Repository**: [dh-tech/awesome-digital-humanities](https://github.com/dh-tech/awesome-digital-humanities)
- **Target Audience**: Humanities scholars, computational linguists, digital historians, and research software engineers.
- **Rule Note**: The repo requires **one entry per PR**. Therefore, submit two separate PRs:
  - PR A: `Phaistos Disc Lab` into `## Visualization`
  - PR B: `Cipher Lab` into `## Data Analysis`

### PR A: Phaistos Disc Lab (Visualization)

#### Git Branch & Edit:
```bash
# Clone your fork
git clone git@github.com:lessthanzero/awesome-digital-humanities.git
cd awesome-digital-humanities
git checkout -b add-phaistos-disc-lab
```

#### Line Insertion (Alphabetical order in `## Visualization` between `Palladio` and `RAWGraphs`):
```markdown
- [Palladio](https://hdlab.stanford.edu/palladio/) - Visualize complex historical data with ease.
- [Phaistos Disc Lab](https://lessthanzero.github.io/phaistos-disk/) - Interactive SVG dual-face spiral workbench, synthetic audio playback, and statistical null hypothesis controls for the Phaistos Disc.
- [RAWGraphs](https://rawgraphs.io/) - Open source, web-based tool for the visualization of complex data.
```

#### PR Title:
```text
Add Phaistos Disc Lab to Visualization
```

#### PR Description:
```markdown
### Summary
Add **Phaistos Disc Lab** to the `Visualization` section.

### Short Pitch
Phaistos Disc Lab provides an interactive, standalone SVG workbench (with dual-face spiral views, sign cataloguing, and audio playback) paired with Python-based Monte Carlo null models and statistical controls for Aegean scripts. It allows researchers and students to explore transcription-level epigraphic observations cleanly separated from interpretive readings.

- Live tool: https://lessthanzero.github.io/phaistos-disk/
- Source code: https://github.com/lessthanzero/phaistos-disk

### Checklist
- [x] I have read and understood the [contribution guidelines](CONTRIBUTING.md).
- [x] Table of contents has been verified.
- [x] Contents are sorted alphabetically.
```

---

### PR B: Cipher Lab (Data Analysis)

#### Git Branch & Edit:
```bash
git checkout main
git checkout -b add-cipher-lab
```

#### Line Insertion (Alphabetical order in `## Data Analysis` between `Breve` and `Data Pen`):
```markdown
- [Breve](https://hdlab.stanford.edu/breve/) - Visualize and edit tabular data.
- [Cipher Lab](https://github.com/lessthanzero/cipher-lab) - Reproducible computational cryptanalysis infrastructure, epistemic ledgering, and statistical gating for historical ciphers and liturgical codebooks.
- [Data Pen](https://hdlab.stanford.edu/data-pen/) - Framework for humanities researchers to access, explore, and manipulate multidimensional historical data.
```

#### PR Title:
```text
Add Cipher Lab to Data Analysis
```

#### PR Description:
```markdown
### Summary
Add **Cipher Lab** to the `Data Analysis` section.

### Short Pitch
Cipher Lab is an open-source computational research environment designed for rigorous analysis of historical ciphers, early modern shorthand systems, and liturgical manuscripts (e.g. Rohonc Codex, D'Agapeyeff, Dorabella, Shugborough). It enforces strict epistemic bounds, Shannon unicity gating ($N \ge U_0$), and an append-only DuckDB ledger with family-wise error rate control to eliminate apophenia in historical decipherment.

- Source code: https://github.com/lessthanzero/cipher-lab
- Releases: https://github.com/lessthanzero/cipher-lab/releases

### Checklist
- [x] I have read and understood the [contribution guidelines](CONTRIBUTING.md).
- [x] Table of contents has been verified.
- [x] Contents are sorted alphabetically.
```

---

## 2. `sobolevn/awesome-cryptography`

- **Repository**: [sobolevn/awesome-cryptography](https://github.com/sobolevn/awesome-cryptography)
- **Target Category**: `## Tools -> ### Standalone` or `## Resources -> ### Web-tools`

#### Line Insertion (In `## Tools -> ### Standalone`, sorted alphabetically):
```markdown
- [Bcrypt](http://bcrypt.sourceforge.net/) - Cross-platform file encryption utility.
- [blackbox](https://github.com/StackExchange/blackbox) - safely store secrets in Git/Mercurial/Subversion.
- [certbot](https://github.com/certbot/certbot) - Previously the Let's Encrypt Client...
- [Cipher Lab](https://github.com/lessthanzero/cipher-lab) - Modular, reproducible research infrastructure for computational cryptanalysis of historical ciphers with automated statistical gating and epistemic ledgers.
- [Coherence](https://github.com/liesware/coherence/) - Cryptographic server for modern web apps.
```

#### PR Title:
```text
Add Cipher Lab to Standalone Tools
```

#### PR Description:
```markdown
### Summary
Add **Cipher Lab** to `Tools -> Standalone`.

### Why it's awesome
Cipher Lab provides a modular, reproducible computational framework for historical cryptanalysis (two-square, double transposition, polyalphabetic substitution, and tachygraphic systems). It introduces automated unicity distance gating ($U_0$), double-blind foil testing, and DuckDB epistemic tracking with Bonferroni correction over tens of thousands of hypothesis trials.
```

---

## 3. `archaeology/archaeology`

- **Repository**: [archaeology/archaeology](https://github.com/archaeology/archaeology)
- **Target Section**: `## Stuff seen elsewhere`

#### Line Insertion:
```markdown
• [Phaistos Disc Lab](https://github.com/lessthanzero/phaistos-disk): Interactive computational research lab, SVG spiral workbench, and physical mark epigraphy for the Phaistos Disc with statistical null hypothesis controls.
```

#### PR Title:
```text
Add Phaistos Disc Lab to directory
```

---

## 4. `DanzillaMaster/awesome-ancient-greek-nlp`

- **Repository**: [DanzillaMaster/awesome-ancient-greek-nlp](https://github.com/DanzillaMaster/awesome-ancient-greek-nlp)
- **Target Section**: `## Annotation and Analysis Tools` or `## Communities and Research Groups`

#### Line Insertion:
```markdown
• [Phaistos Disc Lab](https://github.com/lessthanzero/phaistos-disk) - Interactive corpus inspection, Evans 45-sign catalogue, and statistical controls for Aegean scripts.
```
