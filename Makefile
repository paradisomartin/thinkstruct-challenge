.DEFAULT_GOAL := help

# Docker Desktop may be installed without CLI symlinks on macOS.
ifneq ($(wildcard /Applications/Docker.app/Contents/Resources/bin/docker),)
export PATH := /Applications/Docker.app/Contents/Resources/bin:$(PATH)
endif

DOCKER ?= $(if $(wildcard /Applications/Docker.app/Contents/Resources/bin/docker),/Applications/Docker.app/Contents/Resources/bin/docker,docker)
COMPOSE = env PATH="$(PATH)" "$(DOCKER)" compose
RUN = $(COMPOSE) run --rm app
BRUNO_ENV ?= ThinkStruct Challenge Env
PYTHON ?= python3.13

.PHONY: help venv build db dev migrate makemigrations check test ingest reindex benchmark health openapi api-test logs status stop
.PHONY: frontend-install frontend-dev frontend-check frontend-build frontend-preview frontend-test frontend-unit-test

help:
	@printf '%s\n' \
	  'make venv            Prepare optional host Python 3.13 environment for the editor' \
	  'make dev             Build, migrate, and start the local API with reload' \
	  'make frontend-install Install frontend dependencies from the lockfile (requires Node.js/npm)' \
	  'make frontend-dev    Run the frontend development server on port 5173' \
	  'make frontend-check  Check frontend TypeScript' \
	  'make frontend-build  Check and build the frontend for production' \
	  'make frontend-preview Serve the built frontend locally on port 4173' \
	  'make frontend-test   Browser checks/timing (requires API/sample and running preview)' \
	  'make frontend-unit-test Run Vitest frontend integration tests (no servers required)' \
	  'make migrate         Apply committed database migrations' \
	  'make makemigrations  Generate migrations in backend/ (review before applying)' \
	  'make check           Check Django configuration and model/migration consistency' \
	  'make test            Run PostgreSQL-backed domain and HTTP tests' \
	  'make ingest          Import /data/raw; add ARGS=--dry-run to validate only' \
	  'make reindex         Rebuild patent search vectors after ingestion' \
	  'make benchmark       Measure warm search; write artifacts/search-benchmark.json' \
	  'make health          Check API/database readiness' \
	  'make openapi         Export the live schema to artifacts/openapi.json for Bruno' \
	  'make api-test        Run the versioned Bruno collection against the running API' \
	  'make logs            Follow API and database container logs' \
	  'make status          Show service state and published ports' \
	  'make stop            Stop services without removing persistent data'

venv:
	@if [ ! -e .venv ]; then \
	  command -v "$(PYTHON)" >/dev/null 2>&1 || { printf '%s\n' 'Python 3.13 not found. Install it or set PYTHON=/path/to/python3.13.' >&2; exit 1; }; \
	  "$(PYTHON)" -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) else 'Python 3.13 is required for the editor environment.')" && \
	  "$(PYTHON)" -m venv .venv; \
	fi
	@test -x .venv/bin/python || { printf '%s\n' 'Existing .venv is not usable; move it aside explicitly before retrying.' >&2; exit 1; }
	@.venv/bin/python -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 13) and sys.prefix != sys.base_prefix else 'Expected a Python 3.13 virtual environment; existing .venv was not replaced.')"
	@.venv/bin/python -m pip install -r backend/requirements.lock
	@printf '%s\n' 'Select .venv/bin/python in VS Code. Application/test commands still run in Docker.'

build:
	@$(COMPOSE) build app

db:
	@$(COMPOSE) up -d --wait db

dev: migrate
	@$(COMPOSE) up -d --wait app

migrate: build db
	@$(RUN) python manage.py migrate

makemigrations: build db
	@$(RUN) python manage.py makemigrations $(ARGS)

check: build db
	@$(RUN) python manage.py check
	@$(RUN) python manage.py makemigrations --check --dry-run

test: build db
	@$(RUN) python manage.py test patents api

ingest: migrate
	@$(RUN) python manage.py ingest_patents /data/raw $(ARGS)

reindex: migrate
	@$(RUN) python manage.py rebuild_search_index

benchmark: migrate
	@mkdir -p artifacts
	@$(RUN) python manage.py benchmark_search $(ARGS) > artifacts/search-benchmark.json
	@printf '%s\n' 'Search benchmark written to artifacts/search-benchmark.json'

health:
	@$(COMPOSE) exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5).read().decode())"

openapi:
	@mkdir -p artifacts
	@$(COMPOSE) exec -T app python -c "import json, urllib.request; print(json.dumps(json.load(urllib.request.urlopen('http://127.0.0.1:8000/api/openapi.json', timeout=5)), indent=2))" > artifacts/openapi.json
	@printf '%s\n' 'OpenAPI exported to artifacts/openapi.json'

api-test: health
	@mkdir -p artifacts
	@cd tools/bruno && bru run -r --env "$(BRUNO_ENV)" --reporter-json ../../artifacts/bruno-report.json --reporter-skip-all-headers --reporter-skip-body

logs:
	@$(COMPOSE) logs --follow --tail=100 app db

status:
	@$(COMPOSE) ps

stop:
	@$(COMPOSE) stop

frontend-install:
	@npm --prefix frontend ci

frontend-dev:
	@npm --prefix frontend run dev

frontend-test:
	@python3 frontend/tests/run_browser.py $(URL)

frontend-unit-test:
	@npm --prefix frontend test

frontend-check:
	@npm --prefix frontend run check

frontend-build:
	@npm --prefix frontend run build

frontend-preview:
	@npm --prefix frontend run preview
