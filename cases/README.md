# Research cases

Public index of concrete investigations. IDs here are **landing labels** only; implementation lives under `projects/`.

| ID | Subject | Project | Reproduce |
|----|---------|---------|-----------|
| [CASE-001](CASE-001-dagapeyeff.md) | D’Agapeyeff cipher (1939) | [`projects/dagapeyeff`](../projects/dagapeyeff/) | `pytest tests/test_dagapeyeff.py` |
| [CASE-002](CASE-002-dorabella.md) | Dorabella cipher (1897) | [`projects/dorabella`](../projects/dorabella/) | see case page |
| [CASE-003](CASE-003-shugborough.md) | Shugborough inscription | [`projects/shugborough`](../projects/shugborough/) | see case page |
| [CASE-004](CASE-004-kryptos-k4.md) | Kryptos K4 (1990) | [`projects/kryptos`](../projects/kryptos/) | `pytest tests/test_kryptos.py` |

Related flagship investigation (sibling repo): [Phaistos Disc Lab](https://github.com/lessthanzero/phaistos-disk) (`PH-DISK-*` cases).

When adding a case, keep Input → Constraints → Method → Experiments → Result → Reproduce structure, and record failures as well as successes.
