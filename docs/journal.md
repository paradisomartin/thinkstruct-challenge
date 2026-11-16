# Build journal

Evidence and learning by checkpoint. Current commands live in the [README](../README.md);
decision rationale lives in [decisions](decisions.md).

## Milestone 1 — Dataset discovery · 2026-11-16

**Observed:** 64 JSON arrays, each with 10 objects: **640 patents**, **15,939,070 bytes**.
All files parsed. Original location was `data/patent_data_small/`; the same bytes
were later verified at the current `data/raw/` location. No source files modified.

The standard-library profiler sorts relative paths and hashes UTF-8 manifest
lines `relative_path<TAB>file_sha256<NEWLINE>`. Dataset fingerprint:

```text
94c2239950e897361fb0231fe522b6be28fa9abdc45799923a040c6d8b701be6
```

Two discovery runs returned identical reports. The relocated
`backend/scripts/profile_dataset.py` reproduces the same fingerprint.
Initial runtime: Python 3.9.6, SQLite 3.54.0; SQLite FTS5 capability was checked,
but that stack was not selected. No search measurements were made.

### Actual schema and quality

All 640 records have exactly these eight keys, with **0 missing keys, nulls,
or empty top-level values**. Nested empty strings are a separate issue.

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

- **Identity:** 640 unique string IDs, 0 duplicates. Repeated titles form 43 groups
  covering 183 patents; titles are not identifiers.
- **Descriptions:** 42,040 entries, 20,819 blank (**49.52%**), 21,221 nonblank.
  616 patents contain blank entries; **119 (18.59%) have no usable description**.
  Nonblank passage length: 2 / 463 / 25,013 characters.
- **Claims:** 10,578 nonblank string entries, length 5 / 200 / 4,829 characters.
  168 contain `cancel`; this is a substring count, not a count of canceled legal claims.
  Fragments, numbered claims, and canceled ranges coexist. Preserve original indices,
  not invented legal claim numbers.
- **Classifications:** 145 distinct strings, observed pattern `B60[A-Z][0-9]+FI`.
  Preserve originals; no classification-standard interpretation verified.
  Prefix counts: B60B 298; B60C 318; B60D 20; B60F/B60G/B60J/B60R 1 each.
  `B60B` selectivity is 298/640, not evidence of faster queries.
- **Dates:** JSON/XML filename ranges **2024-02-15–2025-05-01**; no explicit
  date keys. XML identifiers agree with all document numbers: 636 `A1`, 4 `A9`.
  Filename dates are provenance, not independently verified legal filing dates.
- **Text quality:** Inspected artifacts include `FIG.1is`, `insert100according`,
  and a short claim fragment `a semicircular plate (`. No artifact rate measured.
  BibTeX correctness was not independently validated.

Representative record: `patents_ipa240215.json`, index 0, document `20240051333`,
title `SPOKE`, classification `B60B104FI`, filename `US20240051333A1-20240215.XML`.
It has 10 claim entries (first begins `an axle body, having a middle segment...`)
and 15 description entries (index 1 blank). Patent `20240051339`, `PNEUMATIC TIRE`,
has description `[""]`: present does not mean usable.

**Learning:** Inspect nested content, not just field presence. Retain partial
patents and expose traceable evidence; long descriptions require ranking validation.

## Decisions and environment · 2026-11-16

- Read the authoritative four-page brief. Its overview says "one or two"
  enhancements, but the specific Part 3 instruction says **pick 1**; follow that.
  "Hybrid" means structured constraints here, not necessarily vectors.
- Began without Git. Added ignore rules, initialized `main`, corrected the
  repository-local author email, and published the initial snapshot `ae5e302`
  to `https://github.com/paradisomartin/thinkstruct-challenge.git`, without the dataset.
- Flask was initially accepted; user explicitly replaced it with Django/Ninja
  for familiarity. No productivity/performance advantage claimed.
- Automated Docker Desktop install failed on interactive sudo; user completed
  installation. Verified Desktop 4.99.0, Engine/CLI 29.9.3, Compose v5.7.0.
  This session uses the Docker.app executable directory in PATH. MCP Toolkit is
  optional tooling, not a dependency.
- User explicitly accepted the search contract and partial-record policy before
  schema/ingestion work; optional frontend/queues/cloud remain deferred.

## Milestone 2 — Schema and ingestion verified · 2026-11-16

- **Built:** Monorepo backend with two models, migration, ingestion service,
  management command, pinned dependencies/images, and root Compose.
  Data is mounted read-only; database persists in a named volume without a host port.
- **Runtime verified:** Python 3.13.18, Django 5.2.19 (LTS series), Ninja 1.8.0,
  psycopg 3.3.9, PostgreSQL 18.7. Sources: [Django releases](https://www.djangoproject.com/download/),
  [Ninja](https://pypi.org/pypi/django-ninja/json),
  [psycopg](https://pypi.org/pypi/psycopg/json), official image manifests.
  Exact resolved versions are pinned; deliberate updates are still required.
- **Verified:** Migration applied; migration-drift check reported no changes.
  All **12 PostgreSQL-backed tests pass**, including reruns: malformed input,
  optional text, provenance, cancellation markers, duplicates, conflict rollback,
  dry run, and repeated ingestion.
- **Actual import:** **640 patents / 31,671 passages**: 10,450 claims and 21,221
  descriptions. Excluded 20,819 blank entries and **128 standalone canceled markers**.
  Dry-run plan matched; second real import created 0 patents / 0 passages and
  reported 640 unchanged. SQL counts independently matched.
- **Learning:** 168 entries containing `cancel` differs from the 128 conservative
  whole-entry marker matches; do not treat these as equivalent measurements.
  All 119 patents without usable descriptions remain retained.
- **Trade-off:** Raw JSON duplicates normalized storage but preserves auditability.
  In-memory validation and one transaction suit this sample, not an unmeasured
  production pipeline. Repeat ingestion is idempotent: same input has no new effect.
- **Checkpoint:** Code and verification recorded separately as commit `f8ce343`.

## Documentation consolidation · 2026-11-16

User approved three documents under `docs/` plus the authoritative PDF.
Consolidated kickoff/checklist/glossary/benchmark scaffolding into their relevant
contexts; retained discovery evidence and meaningful decision history.
Compose/environment example remain at root; backend owns its Dockerfile and code.
No frontend framework, new application behavior, or cloud resources added.
Verified all 18 local Markdown links and the unchanged PDF fingerprint.
Consolidated seven process/design documents into three; the 12 ingestion tests
also passed again before the documentation-only reorganization.

## Delivery status and next step

- [x] Dataset discovery and accepted contract/data policy
- [x] Schema, ingestion, repeatability, and PostgreSQL-backed tests
- [ ] Search, traceable result evidence, filter correctness, and latency comparison
- [ ] Part 2 architecture with explicit sizing/cost assumptions and one selected PoC
- [ ] Exactly one Part 3 enhancement and its required validation
- [ ] Final reproducible README and accessible ~2-minute Part 2/3 recording

**Next joint decision:** PostgreSQL lexical retrieval configuration and ranking.
Search, HTTP API, search benchmarks, and at-scale validation are not implemented.
