# CASE-002 — Dorabella cipher (1897)

**Project:** [`projects/dorabella`](../projects/dorabella/)  
**Landing status:** Structurally characterized; standard English-prose monoalphabetic routes largely exhausted.  
**Limitations:** [SCIENTIFIC_LIMITATIONS.md](../SCIENTIFIC_LIMITATIONS.md)

## Input

- 87 glyphs in 3 lines, 24-symbol alphabet (Elgar → Dora Penny, 1897).
- Optional negative control: 1886 Liszt inscription ($N=18$).

## Known constraints

- Short ciphertext → aggressive unicity pressure.
- Prior annealing work (Wase 2023) bounds simple monoalphabetic English solutions.
- Musical / Nihilist-coordinate hypotheses are interpretive until they beat foils.

## Method

- Keyword / grille / Nihilist coordinate sweeps with ledger tracking.
- Species-counterpoint and dual MIDI synthesis for melodic cryptogram hypotheses.
- Large keyword dictionaries for English-prose negative results.

## Experiments

- Prose keyword exhaustion (tens of thousands of trials in the lab ledger).
- Liszt inscription as negative control.
- Counterpoint evaluator and Nihilist coordinate solver modules.

## Best candidates

Melodic / structural characterizations outperform naive English prose decrypts in this harness. See [projects/dorabella/README.md](../projects/dorabella/README.md) for metrics and MIDI outputs.

## Verification

```bash
uv sync --all-packages --group dev
uv run pytest tests/ -k dorabella -q
uv run python -m projects.dorabella.counterpoint_evaluator
```

## Result

**Strong negative result** for ordinary English monoalphabetic readings under the tested search budget; **positive structural leads** for musical cryptogram framing remain hypotheses pending external critique.

## Reproduce

Prefer the pytest slice above for a clean checkout. Heavier solvers and MIDI synthesis are documented in the project README and may need local `data/derived/` space.
