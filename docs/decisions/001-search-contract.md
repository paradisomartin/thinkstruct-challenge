# D-001 — Search contract

**Status:** Accepted · **Date:** 2026-11-16.
User explicitly confirmed the contract before ingestion. Service implemented;
HTTP adapter and latency comparison remain pending.

**Why:** Patent-level results with traceable passages keep the workflow explainable.
Claim-only results are an alternative, but entries are not reliably complete or
numbered legal claims.

| Input | Semantics |
|---|---|
| `query` | Plain text over title, abstract, usable claims/descriptions; no SQL/FTS syntax or promise of semantic understanding. |
| `classification_prefix` | Optional uppercase prefix of the original code, e.g. `B60B`. |
| `title_keywords` | Optional literal terms; all must occur as normalized title tokens. |
| `abstract_keywords` | Optional literal terms; all must occur as normalized abstract tokens. |
| `title_exact` | Whole-title equality after case folding, trimming, whitespace collapse; multiple patents may match. |
| `limit`, `offset` | Defaults 20 and 0; limit 1–100, offset nonnegative. |

Combine filters with AND. Keyword normalization uses case folding and Unicode
alphanumeric tokens, no stemming/substrings; each term must normalize to one token.
Missing filtered fields fail constraints. Retrieval tokenization is separate.

Allow filter-only requests ordered by document number; reject invalid parameters
and requests without effective text/filters. Query results sort by descending
relevance then document number; no matches returns an empty list.

**Output:** `results`, pre-pagination `total_matches`, effective request. Results
include document number, title, original classification, nullable abstract/citation,
score/ranking method (null score for filter-only lookup), source filename and
zero-based record index. Excerpts contain original text, source field and original
array index (null for scalar fields), or are null when unavailable. Prefer matching
claims/descriptions, then matching title/abstract; no invented passage evidence
from metadata-only matches. Window size remains to validate.

**Limits:** Scores are not probabilities/legal assessments; array positions are
not legal claim numbers. No arbitrary-ID scraping, verified filing-date filter,
or novelty determination. [Configuration](011-search-configuration.md).
