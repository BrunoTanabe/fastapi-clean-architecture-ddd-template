.DEFAULT_GOAL := help
COMPOSE := docker compose
DEPENDENCIES := database database-admin cache cache-admin

.PHONY: help
help:
	@grep -hE '^[a-zA-Z_-]+:' $(MAKEFILE_LIST) | cut -d: -f1 | sort -u

.PHONY: start
start:
	$(COMPOSE) up -d --build --remove-orphans
	$(COMPOSE) logs -f

.PHONY: start-silent
start-silent:
	$(COMPOSE) up -d --build --remove-orphans

.PHONY: stop
stop:
	$(COMPOSE) down --remove-orphans

.PHONY: delete
delete:
	$(COMPOSE) down -v --remove-orphans

.PHONY: dependencies-up
dependencies-up:
	$(COMPOSE) up -d --remove-orphans $(DEPENDENCIES)
	$(COMPOSE) logs -f $(DEPENDENCIES)

.PHONY: dependencies-up-silent
dependencies-up-silent:
	$(COMPOSE) up -d --remove-orphans $(DEPENDENCIES)

.PHONY: dependencies-down
dependencies-down:
	$(COMPOSE) down --remove-orphans

.PHONY: logs
logs:
	$(COMPOSE) logs -f

.PHONY: view-processes
view-processes:
	docker ps -a

.PHONY: dev
dev:
	uv run uvicorn app.app:app --reload

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: format
format:
	uv run ruff format .

.PHONY: migrate
migrate:
	uv run alembic upgrade head

.PHONY: migration
migration:
	uv run alembic revision --autogenerate -m "$(m)"
