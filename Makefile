.DEFAULT_GOAL := help

# Docker Desktop may be installed without CLI symlinks on macOS.
ifneq ($(wildcard /Applications/Docker.app/Contents/Resources/bin/docker),)
export PATH := /Applications/Docker.app/Contents/Resources/bin:$(PATH)
endif

DOCKER ?= $(if $(wildcard /Applications/Docker.app/Contents/Resources/bin/docker),/Applications/Docker.app/Contents/Resources/bin/docker,docker)
COMPOSE = env PATH="$(PATH)" "$(DOCKER)" compose
RUN = $(COMPOSE) run --rm app

.PHONY: help build db dev migrate makemigrations check test ingest health openapi logs status stop

help:
	@printf '%s\n' \
	  'make dev             Build, migrate, and start the local API with reload' \
	  'make migrate         Apply committed database migrations' \
	  'make makemigrations  Generate migrations in backend/ (review before applying)' \
	  'make check           Check Django configuration and model/migration consistency' \
	  'make test            Run PostgreSQL-backed ingestion and health tests' \
	  'make ingest          Import /data/raw; add ARGS=--dry-run to validate only' \
	  'make health          Check API/database readiness' \
	  'make openapi         Export the live schema to artifacts/openapi.json for Bruno' \
	  'make logs            Follow API and database container logs' \
	  'make status          Show service state and published ports' \
	  'make stop            Stop services without removing persistent data'

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
	@$(RUN) python manage.py test patents config

ingest: migrate
	@$(RUN) python manage.py ingest_patents /data/raw $(ARGS)

health:
	@$(COMPOSE) exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=5).read().decode())"

openapi:
	@mkdir -p artifacts
	@$(COMPOSE) exec -T app python -c "import json, urllib.request; print(json.dumps(json.load(urllib.request.urlopen('http://127.0.0.1:8000/api/openapi.json', timeout=5)), indent=2))" > artifacts/openapi.json
	@printf '%s\n' 'OpenAPI exported to artifacts/openapi.json'

logs:
	@$(COMPOSE) logs --follow --tail=100 app db

status:
	@$(COMPOSE) ps

stop:
	@$(COMPOSE) stop
