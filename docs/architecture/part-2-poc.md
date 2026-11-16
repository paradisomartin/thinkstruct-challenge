# Part 2 — On-demand container ingestion PoC

**Selected and verified locally on 2026-11-16.** This is the small Part 2 PoC:
run ingestion and indexing as disposable containers, then serve their persisted
results from a separate API container. It reuses Part 1 code rather than adding
a queue or deploying AWS. The brief explicitly permits local PostgreSQL and
containerization as PoC examples.

## What this demonstrates

The same built image supports separate commands for migrations, ingestion,
indexing and the API. A job exits after its work; PostgreSQL retains the data.
Repeating identical input adds nothing. This is the local analogue of launching
an ingestion task independently from the API service, not an ECS integration test.

`compose.poc.yaml` overrides the development mounts and port:

- Code runs from the built image, with **no `backend/` bind mount**.
- Only source data is mounted, read-only at `/data/raw`.
- Explicit project name `thinkstruct-poc` creates its own network and
  `thinkstruct-poc_postgres_data` volume.
- API port is `127.0.0.1:8001`, leaving the normal port `8000` available.

Inspection confirmed that the existing database still uses
`thinkstruct_postgres_data`, not the PoC volume. No commands below target the
normal `thinkstruct` project.

## Reproduce

From the repository root, use Docker Compose **2.24.4 or newer** (`!override`
support), the root `.env` prepared as in the [README](../../README.md), and the
supplied 64-file sample under `data/raw/`. The large dataset is not needed.
Docker must be on PATH; on macOS without CLI symlinks:

```sh
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

Always keep the explicit project name and both files:

```sh
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml config --quiet
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml build app
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml up -d --wait db
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml run --rm app python manage.py migrate
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml run --rm app python manage.py ingest_patents /data/raw
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml run --rm app python manage.py rebuild_search_index
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml run --rm app python manage.py ingest_patents /data/raw
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml up -d --wait app
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml run --rm app python manage.py test patents api
```

The verified run began with no PoC volume; Docker created a fresh one.
If the volume already exists, these commands reuse it: the first ingestion may
also report unchanged records. For another clean start, choose a new unused
project name consistently in every command (only one PoC API can use port 8001).
Do not delete the normal database volume.

Check persisted counts independently of the ingestion report:

```sh
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml exec -T db psql -U thinkstruct -d thinkstruct -c \
  "SELECT (SELECT count(*) FROM patents_patent) AS patents, (SELECT count(*) FROM patents_passage) AS passages, (SELECT count(*) FROM patents_patent WHERE search_vector IS NOT NULL) AS indexed; SELECT source_field, count(*) FROM patents_passage GROUP BY source_field ORDER BY source_field;"
```

Check the live HTTP path with host Python 3 (standard library only):

```sh
python3 - <<'PY'
import json
from urllib.parse import urlencode
from urllib.request import urlopen

base = "http://127.0.0.1:8001"
for path in ["/api/health", "/api/openapi.json"]:
    with urlopen(base + path, timeout=10) as response:
        assert response.status == 200
    print(path, 200)

cases = [
    ({"query": "wheel spoke"}, 114),
    ({"query": "wheel spoke", "classification_prefix": "B60B",
      "title_keywords": "wheel"}, 55),
    ({"query": "pressure", "abstract_keywords": "pressure"}, 29),
    ({"title_exact": "SPOKE"}, 1),
]
for params, expected in cases:
    with urlopen(base + "/api/v1/patents/search?" + urlencode(params), timeout=10) as response:
        data = json.load(response)
    assert data["total_matches"] == expected, (params, data["total_matches"])
    for result in data["results"]:
        assert result["source_file"] and result["record_index"] >= 0
        assert result["excerpt"] and result["excerpt"]["text"]
    print(params, data["total_matches"])
PY
```

These assertions check counts and presence of evidence; the automated suite
separately tests source-position integrity, ranking and conflicting-import rollback.

Commands above follow the current v1 routes and test layout. The recorded
verification below predates that refactor; it is not a new PoC execution.

## Observed results

| Check | Result |
|---|---|
| Fresh database | Committed migrations applied successfully |
| First ingestion | 64 files; 640 patents and 31,671 passages created |
| Index rebuild | 640 patents indexed |
| Repeat ingestion | 0 patents / 0 passages created; 640 unchanged |
| SQL counts after reingestion | 640 patents, 31,671 passages, 640 non-null search vectors |
| Passage breakdown | 10,450 claims; 21,221 description paragraphs |
| Health / OpenAPI | Both HTTP 200 |
| Search / filters | 114 plain; 55 classification + title; 29 abstract; 1 exact title, as above |
| Automated suite inside image | 55 tests passed; temporary test database removed by Django |
| Mount inspection | Read-only dataset only for app; separate named database volumes |
| Existing local API | Health remained HTTP 200 on port 8000 |

This is a functional clean-start check, not a latency benchmark. Image build
layers were cached; no cold-build or full-corpus throughput claim is made.

## Boundary with AWS

The [AWS proposal](part-2-aws.md) would replace the local job launch with ECS
`RunTask`, source mounts with S3 reads, and the local database with RDS.
Those integrations, IAM/networking, bounded batches, durable progress/retries,
automatic index readiness and production serving remain unimplemented.
Ingestion still validates the whole sample in memory and writes one transaction;
indexing is a separate explicit command. Health checks database connectivity,
not index completeness. The API still uses Django's development server.

To stop the PoC while retaining its data:

```sh
docker compose -p thinkstruct-poc -f compose.yaml -f compose.poc.yaml stop
```

This preserves both database volumes. No AWS resources or paid APIs are used.
