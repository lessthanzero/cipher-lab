# Community Outreach Playbook: Maximizing Impact & Peer Engagement

This playbook coordinates external community outreach across Reddit, Hacker News, domain research blogs, and academic networks.

---

## 1. Hacker News ("Show HN") Submissions

Hacker News rewards deep technical craftsmanship, open tools, interactive browser demos, and candid epistemic humility (i.e. strictly stating what is and isn't proven).

### Submission A: Phaistos Disc Lab (High Viral Potential)
- **Target Timing**: Tuesday or Wednesday between 13:00 UTC and 15:00 UTC (9:00 AM – 11:00 AM ET).
- **Title**: `Show HN: Phaistos Disc Lab – Interactive SVG workbench, audio, and null models`
- **Link URL**: `https://lessthanzero.github.io/phaistos-disk/workbench/`
- **First Comment by Submitter** (Post immediately after submitting):
```markdown
Hi HN,

I built an open-source, local-first computational workbench for exploring the Phaistos Disc:
https://github.com/lessthanzero/phaistos-disk

A core motivation was frustration with decipherment claims that jump straight to speculative translations. Instead, this lab enforces a strict four-tier evidence hierarchy (L0 physical marks, L1 sign transcriptions, L2 palaeographic analogies, L3 interpretive hypotheses).

Features:
- Standalone HTML/SVG interactive spiral workbench (both faces, zoomable, sign-by-sign inspection)
- Synthetic tone generation / playback for rhythmic structures
- Monte Carlo null hypothesis controls (testing sign distributions against synthetic surrogate texts to avoid apophenia)
- Zero build tools required for the web viewer; backend powered by Python and uv

It is explicitly *not* a decipherment claim. I’d love feedback on the SVG visualization, statistical controls, or data layout.
```

---

### Submission B: Cipher Lab
- **Target Timing**: Thursday between 13:00 UTC and 15:00 UTC.
- **Title**: `Show HN: Cipher Lab – Reproducible cryptanalysis for historical ciphers`
- **Link URL**: `https://github.com/lessthanzero/cipher-lab`
- **First Comment by Submitter**:
```markdown
Hi HN,

Cipher Lab is a reproducible computational research harness for historical cryptanalysis (D'Agapeyeff 1939, Dorabella 1897, Rohonc Codex c. 1530, and Shugborough):
https://github.com/lessthanzero/cipher-lab

Key technical components:
1. Shannon Unicity Gating: Disallows single-key optimization if payload length N < U_0, mathematically preventing combinatorial hallucinations on short cryptograms.
2. DuckDB Epistemic Ledger: Logs every hypothesis trial (40,000+ logged) with Bonferroni family-wise error rate control.
3. Multi-Node Distributed Compute: Dispatches Monte Carlo permutation shuffles to remote Linux workers over SSH.
4. Double-Blind Refereeing: Evaluates candidate decryptions against negative-control decoys (foils).

All code, data, and test suites are open source and pass 120 automated tests via pytest.
```

---

## 2. Reddit Strategy

| Subreddit | Subscribers | Target Repository | Angle / Theme |
|---|---|---|---|
| `r/codes` | 130k+ | `cipher-lab` | D'Agapeyeff decipherment + sanity check request |
| `r/cryptography` | 150k+ | `cipher-lab` | Epistemic ledgering, unicity gating, DuckDB statistical controls |
| `r/Archaeology` | 240k+ | `phaistos-disk` | Interactive SVG workbench + physical observation tiers |
| `r/linguistics` | 280k+ | Both | Repeated sequence analysis (`02-12-31-26`) & Rohonc syntax shuffles |
| `r/digitalhumanities` | 15k+ | Both | Reproducible research software & surrogate null models |

> **Ready-to-Post Drafts**:
> - For D'Agapeyeff / `cipher-lab`: See [`cipher-lab/docs/ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md`](../ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md).
> - For Phaistos Disc / `phaistos-disk`: See [`phaistos-disk/docs/OUTREACH_DRAFTS.md`](file:///Users/sashakatin/Developer/phaistos-disk/docs/OUTREACH_DRAFTS.md).

---

## 3. Direct Domain Peer Outreach

### 1. Klaus Schmeh (*Cipherbrain*, `cipherbrain.net`)
- **Profile**: Leading author and journalist on historical cryptography; organizer of mystery cipher challenges; co-author of *Codebreaking: A Practical Guide* (with Elonka Dunin).
- **Pitch**: Send an email pointing to the D'Agapeyeff 14th column reflection + Two-Square reconstruction and the Rohonc Codex Diatessaron alignment. Klaus often writes dedicated blog posts about breakthroughs from his readership.

### 2. Nick Pelling (*Cipher Mysteries*, `ciphermysteries.com`)
- **Profile**: Renowned cipher historian whose diagonal reflection hypothesis catalyzed the D'Agapeyeff solution.
- **Pitch**: Comment on his relevant D'Agapeyeff post or contact him via email sharing the verified mathematical results and GitHub repository credit.

### 3. Tim Marland (`dagapeyeffresearch.com`)
- **Profile**: Author of the seminal computational study on D'Agapeyeff.
- **Pitch**: Use the pre-drafted direct message in [`cipher-lab/docs/ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md`](../ANNOUNCEMENT_AND_COMMUNITY_REVIEW.md).

### 4. Academic Aegean Epigraphers
- **Targets**: Dr. Ester Salgarella (AIAS Aarhus / Linear A), Prof. Silvia Ferrara (Bologna / ERC SAPIENCE), Dr. Brent Davis (Melbourne).
- **Pitch**: Use the polite, critical review request template in [`phaistos-disk/docs/OUTREACH_DRAFTS.md`](file:///Users/sashakatin/Developer/phaistos-disk/docs/OUTREACH_DRAFTS.md#L45-L65).
