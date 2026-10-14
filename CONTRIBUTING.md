# Contributing to Cipher Lab

Thanks for helping keep this a reproducible research laboratory rather than a claim dump.

## Setup

```bash
uv sync --all-packages --group dev
uv run pytest
uv run ruff check .
```

Python **3.12+** and [`uv`](https://docs.astral.sh/uv/) are required.

## Before you open a PR

1. Read [SCIENTIFIC_LIMITATIONS.md](SCIENTIFIC_LIMITATIONS.md).
2. Prefer a failing or clarifying experiment over a stronger slogan.
3. Keep L0/L1 observations separate from interpretive readings.
4. If you claim linguistic viability, include a negative control (shuffle / foil) and respect the unicity gate.

## Good first contributions

- Reproduce a case in [cases/](cases/) and file a **reproduction report** issue (pass/fail + environment).
- Add a case stub linking an existing `projects/*` module (do not invent parallel registries).
- Fix corpus typos or documentation that overclaims relative to limitations.
- Add tests that pin an invariant you relied on.

## Adding a research case

1. Prefer extending an existing project under `projects/<name>/`.
2. Add a short page under `cases/CASE-NNN-slug.md` with: Input, Constraints, Method, Experiments, Best candidates, Verification, Result, Reproduce.
3. Link it from [cases/README.md](cases/README.md) and the root README table.
4. Keep landing summaries cautious; put strong math in the project README.

## Code style

- Match existing module layout and `ruff` settings in `pyproject.toml`.
- Do not commit secrets, homelab tokens, or large regenerated DuckDB ledgers.
- Derived outputs belong under `data/derived/` (gitignored) unless they are a tiny committed summary JSON needed for clean-checkout demos.

## Conduct

Be precise, cite sources, and assume other researchers will try to break your result. That is the point.

## Maintainers — GitHub social preview

After merging `docs/media/social-preview.png`, upload it under **Settings → General → Social preview** (GitHub UI; not settable via `gh` reliably). Pages also serves the same file at `https://lessthanzero.github.io/cipher-lab/social-preview.png` for Open Graph tags.
