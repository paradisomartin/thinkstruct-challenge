# 03 — System Design (Part 2)

**Status:** Outline only — to be completed after the MVP is understood.

## Scope and assumptions
- Current dataset: small sample of vehicle patent applications.
- Target scale to reason about: ~10 million patents (as specified by the brief).
- Query volume, freshness expectations, infrastructure provider, and budget are **not** given; state explicit assumptions before estimating cost.

## Architecture diagram

_Add an Excalidraw or draw.io export here once the design is selected. Keep the editable original under the repo if possible._

```text
Source data
    |
    v
Validation + normalization
    |
    v
Index / metadata store <--- index status and error records
    |
    v
Search API <--- filter + ranking logic
    |
    v
Client / search consumer
```

## Components (to decide)
- Ingestion worker and scheduler
- Data validation / dead-letter handling
- Metadata storage
- Lexical and/or semantic retrieval index
- Search API
- Cache and/or rate limiting (only if justified)
- Metrics, logs, and pipeline status

## Main pipelines
1. **Ingestion:** receive → validate → normalize → upsert → index → mark completed/failed.
2. **Search:** parse query/filters → retrieve candidates → score/rank → hydrate metadata → return results.

## Failure handling and observability
- Define stable patent IDs and idempotent upserts.
- Retry transient failures; quarantine invalid records.
- Track indexed records, failed records, ingest lag, query latency, and error rates.

## Cost model (fill with explicit assumptions)

| Component | Sizing assumption | Monthly cost estimate | Scaling driver |
|---|---|---|---|
| Object storage | TBD | TBD | Data size |
| Metadata database | TBD | TBD | Document count and QPS |
| Search index | TBD | TBD | Indexed passages, replicas |
| Ingestion compute | TBD | TBD | New/updated documents |
| API/compute | TBD | TBD | QPS and latency SLO |
| Monitoring | TBD | TBD | Log/metric volume |
| **Total** | | **TBD** | |

_Do not invent prices or infrastructure sizing. Estimate only after explicit assumptions and a chosen platform._

## Scale risks
- Storage growth when indexing passages rather than patents
- Latency/cost trade-off of semantic embedding generation
- Filter selectivity and ranking quality
- Re-indexing, schema migrations, deduplication, missing data
- Operational visibility and cost forecasting

## Proof of concept
- **Chosen component:** Pending
- **Goal:**
- **How to run:**
- **What it proves:**
- **Known shortcuts:**
