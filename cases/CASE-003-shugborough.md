# CASE-003 — Shugborough inscription

**Project:** [`projects/shugborough`](../projects/shugborough/)  
**Landing status:** Unicity-bounded; Latin memorial initialism model preferred over popular myths.  
**Limitations:** [SCIENTIFIC_LIMITATIONS.md](../SCIENTIFIC_LIMITATIONS.md)

## Input

- 8 letters `OUOSVAVV` flanked by `D · M ·` on the Shepherd’s Monument (Shugborough, mid-18th century).
- Epigraphic observations: interpuncts, `U` vs `V` letterforms.

## Known constraints

- $N \ll U_0$ for single-key cryptanalysis → combinatorial “solutions” are underdetermined.
- Any viable reading should respect *Dis Manibus* memorial conventions and carved punctuation.

## Method

- Shannon unicity gate before optimization.
- Epigraphic audit + Bayesian Latin initialism transition model.
- Explicit falsification checks against popular “widower” / Magdalen polyalphabetic stories.

## Experiments

- Runner suite in `projects/shugborough/runner.py`.
- Letterform / interpunct constraint tests.

## Best candidates

Memorial Latin initialism under *Dis Manibus*, scored against historical candidates. Details: [projects/shugborough/README.md](../projects/shugborough/README.md).

## Verification

```bash
uv sync --all-packages --group dev
uv run pytest tests/ -k shugborough -q
uv run python -m projects.shugborough.runner
```

## Result

**Information-theoretic bound:** classical single-key decrypts are not uniquely recoverable. **Preferred historical model:** epigraphic Latin initialism; popular tourist cryptograms fail letterform / prior tests in this harness.

## Reproduce

Use the commands above. Academic write-up: [docs/SHUGBOROUGH_EPIGRAPHIC_PAPER.md](../docs/SHUGBOROUGH_EPIGRAPHIC_PAPER.md).
