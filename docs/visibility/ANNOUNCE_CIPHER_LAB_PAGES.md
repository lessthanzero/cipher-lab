# Announcement drafts — Cipher Lab Pages essay

**Artifact:** https://lessthanzero.github.io/cipher-lab/  
**Repo:** https://github.com/lessthanzero/cipher-lab  

**Context already public (do not re-launch as “new”):**

- Reddit: Dorabella, D’Agapeyeff, Phaistos (case-level posts)
- HN: [Show HN: Phaistos Disc workbench](https://news.ycombinator.com/item?id=49866163)

**Angle for this wave:** the *lab essay* — one coherent story (D’Agapeyeff as demo) + how claims stay bounded. Soft claims. No “please star.”

**Consilium note:** Prefer monograph framing; keep Dorabella/Phaistos as secondary probes, not co-equal wins.

---

## X / Bluesky — short thread (4)

### 1/4
```text
I wrote up Cipher Lab as a short research essay on GitHub Pages.

Not a product launch — a reproducible look at the 1939 D’Agapeyeff challenge, with the margin anomaly made visible in the browser.

https://lessthanzero.github.io/cipher-lab/
```

### 2/4
```text
Story arc:

1. Why short historical ciphers overfit
2. The 1939 impasse (author lost his own notes)
3. Reflect the 14×14 grid → strip padding → 182-pair payload
4. Candidate reading under review — with limits stated up front
```

### 3/4
```text
Dorabella and Phaistos stay sibling probes, not a “solved mysteries” scoreboard.

I already posted those cases separately on Reddit; Phaistos workbench was on HN earlier.

This page is the lab spine + one demo you can re-run from git.
```

### 4/4
```text
Reproduce:

uv sync && uv run pytest tests/test_dagapeyeff.py -q

Code: https://github.com/lessthanzero/cipher-lab

If the reading fails your control, open an issue — that’s the useful signal.
```

---

## Hacker News — Show HN

**Timing:** Prefer mid-week morning US (avoid same-day spam after Phaistos if that thread is still warm).  
**Title options (pick one):**

1. `Show HN: Cipher Lab – reproducible essay on the 1939 D’Agapeyeff cipher`
2. `Show HN: A research preview for historical cryptanalysis (D’Agapeyeff demo)`

**URL:** `https://lessthanzero.github.io/cipher-lab/`  
(Secondary link in comment: GitHub repo.)

### First comment (submitter)

```markdown
Hi HN —

Following the Phaistos Disc workbench post, here’s the sibling **Cipher Lab** essay:
https://lessthanzero.github.io/cipher-lab/

Cipher Lab is a small open harness for historical cryptanalysis (unicity gating, negative controls, append-only trial ledger). The Pages piece is deliberately narrow: one primary demo (D’Agapeyeff 1939), soft claims, and a clean reproduce path.

Interactive bit: 14×14 pair grid → diagonal reflection → strip the anomalous margin → 182-pair payload.

Repo + CASE-001 notes:
https://github.com/lessthanzero/cipher-lab

```bash
uv sync --all-packages --group dev
uv run pytest tests/test_dagapeyeff.py -q
```

Happy to take methodological criticism. Dorabella / Phaistos are linked as sibling probes, not co-equal “solved” trophies.
```

---

## Optional Reddit cross-post (only if a prior thread asks “where’s the write-up?”)

Do **not** cold-post another D’Agapeyeff launch in the same subs. If useful as a reply:

> Full lab essay with the interactive grid is here: https://lessthanzero.github.io/cipher-lab/ — framed as research preview, not case closed.
