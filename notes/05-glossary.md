# 05 — Glossary

Add definitions when they become relevant to a decision or implementation. Keep each entry short and grounded.

| Term | Meaning in this project |
|---|---|
| Patent claim | Text that defines the legally enforceable scope of an invention. |
| Abstract | Short summary of a patent's invention, usable for text filtering/search. |
| Detailed description | Longer body text of the patent, provided as paragraphs in the dataset. |
| Prior art | Earlier published material relevant to whether an invention is novel. |
| Classification code | Code categorizing technical subject matter; the brief mentions prefix `B60B` for vehicle wheels. |
| Patent document number | Identifier of a patent/application record; actual format needs dataset inspection. |
| Hybrid search (brief's usage) | Search combining text retrieval with constraints such as classification, title, and abstract keywords. |
| Retrieval | Finding candidate documents or text passages matching a query. |
| Ranking | Ordering retrieved results by estimated relevance. |
| Proof of concept (PoC) | A minimal implementation demonstrating one part of the proposed at-scale system. |
| Dataset profiling | Read-only measurement of actual shapes, counts, missing content, and anomalies before designing ingestion. |
| Missing vs. empty content | An absent key, null, empty list, and a nonempty list containing only blank strings are different cases. This sample has 119 descriptions of the last kind. |
| Search contract | Explicit rules for valid inputs, filters, ordering, pagination, and returned evidence, independent of CLI or HTTP transport. |
| Lexical retrieval | Matching words/tokens rather than learned meaning; a transparent baseline that may miss paraphrases. |
| Inverted index / FTS5 | A token-to-document lookup structure; FTS5 is SQLite's full-text indexing/search extension. |
| BM25 | A lexical ranking function using term frequency, term rarity, and document length. Scores are not probabilities; score direction depends on the implementation. |
| Semantic embedding / vector similarity | A model maps text to numerical vectors, then compares them to estimate related meaning. Requires model and passage choices; not implemented here. |
| Filter selectivity | How much a constraint narrows eligible data. Here `B60B` retains 298/640 patents; this does not itself establish a speedup. |
| Token normalization | Rules for turning text into comparable tokens; exact-title equality and keyword filtering need explicit rules separate from retrieval tokenization. |
| Provenance / source index | A result's original file, record, field, and array position. An array index is not necessarily a legal claim number. |
| Canceled-claim marker | Text such as `1 - 5 . (canceled)` occupying a claims entry without substantive claim text; not meaningful match evidence on its own. |
| Source batch date | Date encoded in the source JSON filename; not independently verified as the patent's legal filing date. |
| Kind code | Identifier suffix such as the observed `A1` or `A9`; preserve the supplied value rather than assuming all documents use `A1`. |
| SHA-256 manifest fingerprint | Hash summarizing sorted filenames and their content hashes, identifying the exact dataset bytes used for a discovery run. |
| Deterministic pagination | Stable ordering and slicing of results; a document-number tie-breaker prevents tied scores from arbitrarily changing page membership for fixed data. |
| PostgreSQL full-text search | Native lexical search using `tsvector` documents and `tsquery` queries, commonly accelerated by a GIN inverted index. |
| `ts_rank` / `ts_rank_cd` | PostgreSQL relevance functions, not BM25; choice and configuration require validation. |
| Flask / WSGI | Flask handles HTTP requests; a production WSGI server runs the application outside its development server. |
| Docker Compose | Local definition of cooperating containers and persistent volumes; not an AWS deployment mechanism. |
| Background worker / queue | Runs asynchronous jobs outside request handling; Celery/Redis adds retry and job-state responsibilities. Deferred until justified. |
| ECS Fargate | AWS-managed compute for ECS containers; does not automatically optimize database queries or guarantee full-system scalability. |
| RDS / S3 | AWS-managed relational database hosting / object storage; candidates for persistent database and raw source storage. |
| Astro Starlight / React | Optional documentation framework / interactive UI library; React components can run inside Astro. |
| Git ignore / remote | Ignore rules exclude untracked artifacts from normal staging; a remote is a destination for publishing commits. Ignore rules do not remove already tracked files or history. |

## To add as needed
- Re-ranking / cross-encoder
- Idempotency / dead-letter queue
- Consistency of linked UI views / stale responses
