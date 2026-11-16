# D-002 — Partial records and identity conflicts

**Status:** Accepted · **Date:** 2026-11-16.
User explicitly confirmed these rules before ingestion.

Keep a nonblank string ID and meaningful text in at least one searchable field;
optional metadata may be null. Retain patents without descriptions. Omit blank
and standalone canceled-claim markers from derived passages, not text merely
mentioning cancellation. Preserve raw JSON and original indices.

**Why / trade-off:** Rejecting empty descriptions loses 119 otherwise searchable
patents; retaining them requires field-level fallbacks.

**Conflicts:** Abort the entire small-sample import on malformed input or duplicate
input IDs. Existing identical content/provenance is unchanged; changed content or
provenance is an error, never an overwrite. No quarantine infrastructure.

**Evidence:** Initial 12 ingestion tests passed; 640 records retained and repeat
ingestion creates none. [Ingestion evidence](../journal/03-ingestion.md).
