# Milestone 1 — Dataset discovery · 2026-11-16

**Inventory:** 64 JSON arrays with 10 objects each: **640 patents**,
**15,939,070 bytes**. All files parsed. Original location `data/patent_data_small/`;
same bytes later verified at `data/raw/`. No source files modified.

The standalone profiler sorts relative paths and hashes UTF-8 manifest lines
`relative_path<TAB>file_sha256<NEWLINE>`. Dataset fingerprint:

```text
94c2239950e897361fb0231fe522b6be28fa9abdc45799923a040c6d8b701be6
```

Two discovery reports were identical; relocated `backend/scripts/profile_dataset.py`
reproduces this fingerprint. Initial runtime: Python 3.9.6, SQLite 3.54.0.
SQLite FTS5 capability checked, not selected or benchmarked.
Current commands: [README](../../README.md).

## Actual schema

All records have exactly these eight keys; **0 missing/null/empty top-level values**.
Nested emptiness must be checked separately.

| Key | Type | Length min / median / max |
|---|---|---|
| `title` | string | 4 / 36 / 162 characters |
| `doc_number` | string | 11 / 11 / 11 characters |
| `filename` | string | 28 / 28 / 28 characters |
| `abstract` | string | 62 / 714 / 1,768 characters |
| `detailed_description` | list of strings | 1 / 47 / 677 entries |
| `claims` | list of strings | 1 / 19 / 46 entries |
| `bibtex` | string | 141 / 173 / 299 characters |
| `classification` | string | 9 / 10 / 11 characters |

## Quality and implications

- **IDs:** 640 unique 11-digit strings, 0 duplicates. Repeated titles: 43 groups,
  183 patents; titles are not identifiers.
- **Descriptions:** 42,040 entries; 20,819 blank (49.52%), 21,221 nonblank.
  616 patents have blank entries; **119 (18.59%) have no usable description**.
  Nonblank length: 2 / 463 / 25,013 characters.
- **Claims:** 10,578 nonblank entries, length 5 / 200 / 4,829 characters.
  168 contain `cancel`: substring count, not legal canceled-claim count.
  Fragments, numbered entries and canceled ranges coexist; array positions
  are not legal claim numbers.
- **Classification:** 145 strings, observed `B60[A-Z][0-9]+FI` pattern, not a
  verified general standard. Preserve codes; do not infer suffix meaning.
  Prefixes: B60B 298; B60C 318; B60D 20; B60F/B60G/B60J/B60R 1 each.
  B60B selectivity 298/640 does not prove a speedup.
- **Dates:** JSON/XML filename range 2024-02-15–2025-05-01; no explicit date keys.
  XML document numbers all agree; 636 A1, 4 A9. Dates are provenance, not
  independently verified legal filing dates.
- **Artifacts:** Inspected `FIG.1is`, `insert100according`, and short claim
  `a semicircular plate (`. No artifact rate measured or BibTeX correctness verified.

Representative `patents_ipa240215.json`, index 0: document `20240051333`,
`SPOKE`, `B60B104FI`, XML `US20240051333A1-20240215.XML`. Ten claim entries;
first begins `an axle body, having a middle segment...`. Fifteen description
entries, index 1 blank. Document `20240051339`, `PNEUMATIC TIRE`, has `[""]`.

**Learning:** Present does not mean usable. Retain partial patents with traceable
evidence; long descriptions need ranking validation.
