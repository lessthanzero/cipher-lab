# CASE-001 — D’Agapeyeff cipher (1939)

**Project:** [`projects/dagapeyeff`](../projects/dagapeyeff/)  
**Landing status:** Best current reconstruction under active peer review (not a closed historical verdict).  
**Limitations:** [SCIENTIFIC_LIMITATIONS.md](../SCIENTIFIC_LIMITATIONS.md)

## Input

- 392-digit textbook challenge (196 digit pairs, digits primarily 1–5) from Alexander D’Agapeyeff, *Codes and Ciphers* (1939).
- Tracked corpus helpers in `projects/dagapeyeff/corpus.py` (raw digits, pairs, frequencies).

## Known constraints

- Author later stated he lost his own encryption notes and could not recover the plaintext.
- Community priors used as structural hypotheses (not axioms): 14th-column anomaly (van Eykelen), diagonal reflection (Pelling), Two-Square / keyword baselines (Marland and others).
- Linguistic viability must beat negative-control shuffles; unicity gating applies inside the harness.

## Method

1. Build $14 \times 14$ pair grid; apply diagonal reflection / margin trim hypotheses.
2. Explore double columnar transposition keyed by survey vocabulary (e.g. `HYDROGRAPHICAL`) and vertical Two-Square rectangle variants.
3. Score candidates with English language models / IoC / $\chi^2$ and shuffle controls.
4. Log trials in the epistemic ledger when runners are used (local `data/derived/`).

## Experiments

- Corpus integrity and baseline Polybius decode path (unit tests).
- Exact 14-key / structural sweeps (`exact_14key_sweep`).
- Longer stochastic reconstruction and errata ledgers (see project README; heavier than CI).

## Best candidates

See the calibrated English reading and diplomatic consensus in [projects/dagapeyeff/README.md](../projects/dagapeyeff/README.md). Treat errata tables as part of the claim, not optional footnotes.

## Verification

| Check | Command / artifact |
|-------|--------------------|
| Corpus invariants | `uv run pytest tests/test_dagapeyeff.py -q` |
| Structural sweep entrypoint | `uv run python -m projects.dagapeyeff.exact_14key_sweep` |
| Full narrative + metrics | project README |

## Result

**Working reconstruction** of a naval-survey style English plaintext under the coupled structural pipeline, with quantified scores vs shuffle controls. Independent specialist review is invited; landing pages avoid “case closed” language.

## Reproduce

```bash
uv sync --all-packages --group dev
uv run pytest tests/test_dagapeyeff.py -q
uv run python -m projects.dagapeyeff.exact_14key_sweep
```

Optional deeper run (longer; may write under `data/derived/`):

```bash
uv run python -m projects.dagapeyeff.linguistic_reconstruction
```
