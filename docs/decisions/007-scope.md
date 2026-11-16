# D-007 — Backend-first scope and AWS boundary

**Status:** Accepted · **Date:** 2026-11-16.

User approved required ingestion/search/measurements before extras.
React is now approved for the selected Part 3 Interface at Scale enhancement
(see [D-005](005-enhancement.md)). Starlight, Celery/Redis and live AWS deployment
remain deferred.

**Why / trade-off:** Protect challenge delivery time instead of speculative setup.
Queues need demonstrated asynchronous work and add retries/duplicate execution
to manage. Initial ingestion is a command.

AWS candidate: static hosting/CDN, ECS Fargate API/ingest tasks, RDS PostgreSQL,
S3 sources. Fargate manages compute, not database performance. Production needs
WSGI/ASGI serving and persistent database storage outside ephemeral API containers.
No AWS resources provisioned or capacity guarantees.
[Architecture and budget assumptions](../architecture/README.md) remain proposed.
