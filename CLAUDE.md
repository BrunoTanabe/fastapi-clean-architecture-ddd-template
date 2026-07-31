# FastAPI Clean Architecture and DDD Template

A reusable Python backend template organized by Clean Architecture layers (domain, application,
infrastructure, presentation) and Domain-Driven Design principles. It ships a working
authentication stack, API-key management, users, knowledge bases, notifications, WebSocket
delivery, Redis caching, Alembic migrations, Docker support, and scaffolding tooling.

This is a template, not a product. Build features on top of it; do not assume a business domain
that is not in the code.

## Stack

- **Python >= 3.14** · FastAPI · Pydantic v2 · SQLAlchemy 2 (async) · PostgreSQL 17 · Redis 8
- **Libraries:** py-automapper · loguru · alembic · pwdlib (argon2) · jwcrypto · cryptography · orjson · redis · asyncpg · psycopg 3 · stackprinter
- **Tooling:** uv (package manager) · ruff (lint + format) · uvicorn (dev) · hypercorn · make · ngrok (DEV only)

## Commands

```bash
uv sync                                   # install dependencies
make dev                                  # uvicorn app.app:app --reload
make start / make stop / make delete      # full Docker stack up / down / down + volumes
make dependencies-up / dependencies-down  # only database, database-admin, cache, cache-admin
make migrate                              # alembic upgrade head
make migration m="description"            # alembic revision --autogenerate
make lint / make format                   # ruff check / ruff format
make logs / make view-processes           # compose logs / docker ps -a
python scripts/create_module.py           # interactive module skeleton (empty files only)
```

Compose services: `api` (port 3000 in-container), `database` (`postgres:17-alpine`),
`database-admin` (pgAdmin), `cache` (`redis:8.6-alpine`), `cache-admin` (RedisInsight).
The app runs Alembic upgrade-to-head on startup, so a fresh stack self-migrates.

`migrations/versions/` ships empty by design — the first `make migration` in a new project
creates the initial revision.

## Architecture

Each module under `app/modules/{module}/` has four layers:

| Layer | Directory | Files | Responsibility |
|-------|-----------|-------|----------------|
| Domain | `domain/` | `entities.py`, `enums.py`, `value_objects.py` | Pure Python — no FastAPI, SQLAlchemy, or Pydantic imports |
| Application | `application/` | `use_cases.py`, `interfaces.py`, `mappers.py`, `exceptions.py`, `utils.py` | Orchestration; depends on `domain/` and `shared/` only |
| Infrastructure | `infrastructure/` | `models.py`, `repositories.py`, `caches.py`, `services.py` | SQLAlchemy models, Postgres repositories, Redis caches, service implementations |
| Presentation | `presentation/` | `routers.py`, `schemas.py`, `docs.py`, `dependencies.py` | FastAPI routers, Pydantic schemas, OpenAPI docs, DI factories |

Empty files are normal — a module keeps the full skeleton even when a layer file is unused.

The `shared` module exposes the base types every other module builds on.

Full architectural reference: @.claude/architecture.md

### Module status

| Module | Status | Notes |
|--------|--------|-------|
| `authentication` | implemented | login / refresh / logout, nested JWT (JWS+JWE) in cookies, `Authentication` sessions, Redis-cached |
| `key` | implemented | API keys: create, list, get, update, rotate, revoke — admin only; Redis-cached with tombstones |
| `user` | implemented | internal users (admin / manager / user roles), create + `/me` |
| `knowledge` | implemented | canonical CRUD + broadcast-notification reference |
| `notification` | implemented | per-user + broadcast fan-out, WebSocket dispatch via `SharedUseCases` |
| `websocket` | implemented | real-time delivery via `ConnectionManager` (in-memory, single-process) |
| `health` | implemented | liveness, docs redirect, alembic version (admin) |
| `example` | reference | minimal demo module used as a scaffolding example; no persistence |
| `shared` | base | base types, value objects, `UNSET` sentinel, `SharedUseCases` |

Known in-progress areas — keep them, never "clean them up":

- **WebSocket fan-out** is single-process: `ConnectionManager` holds connections in an in-memory
  dict on `app.state`. Cross-worker delivery is future work.
- **`knowledge` caching** is partial: `IKnowledgeCache` declares only `insert` and
  `KnowledgeUseCases` does not call its `cache` collaborator yet. Follow `key` for the complete
  pattern.
- **`SECURITY_API_KEY_ALLOWED_PATHS`** is an empty tier for a fully implemented mechanism —
  API-key authentication works; no endpoint has opted into it yet.

## Critical Rules

- Repositories call `session.flush()`, never `session.commit()` — the request lifecycle owns the transaction, so a commit inside a repository would break atomicity across use-case steps.
- Repositories return domain entities (via `model_entity_mapper`), never ORM models.
- **Three error-handling shapes, one per layer kind:**
  - *3-branch* (use cases, router handlers): `StandardException → raise`, `DomainError → raise DomainException(e)`, `Exception → logger.opt(exception=e).error(...) + raise {Module}Exception()`.
  - *2-branch* (repositories, services): no `DomainError` branch — those layers never touch domain rules.
  - *Never-raise* (caches): every method catches, logs, and returns `None`. A cache failure degrades to the database and must never fail the request.
- Double-route decorators on every endpoint, including parameterized ones: `/{id}/` visible plus `/{id}` with `include_in_schema=False` — the security allowlists register both slash forms.
- `BaseModel` (ORM) and `BaseEntity` (domain) already provide `id`, `is_active`, `created_at`, `updated_at` — never redeclare them. Override `deactivate()` only when extra domain logic is needed, and call `super().deactivate()` (see `Key.deactivate`, `Knowledge.deactivate`).
- Enums extend `(str, Enum)` for JSON serialization. Enum columns use `SQLEnum(X, name="{snake}_enum")` without `create_type`; PostgreSQL stores the uppercase member **NAMES** (`"ADMIN"`, `"KNOWLEDGE_CREATED"`), which matters for seed migrations and raw SQL.
- An entity field named `metadata` renames the model attribute to `{module}_metadata` with `name="metadata"` on the column (SQLAlchemy reserves `metadata`); mappers bridge the two names. Reference: `NotificationModel`.
- Mappers explicitly map inherited fields (`id`, `is_active`, `created_at`, `updated_at`) in `fields_mapping` — automapper does not traverse parent dataclass `slots`, so omitting them silently drops values.
- `shared/domain/value_objects.py` owns `UNSET`, `RESOURCE_NAME_PATTERN`, and the reusable value objects `Email`, `Name`, and `Phone`. `Email` enforces `SECURITY_EMAIL_ALLOWED_DOMAINS` unless constructed with `enforce_allowed_domains=False`. Keep a value object in its module until a second module needs it.
- Paginated modules declare `{Entity}List(PaginatedList)` and `{Entity}Pagination(Pagination)` next to the entity. `PaginatedList` supplies `total`; the subclass adds only `items`.
- Router handlers receive `Authentication` (from the `authentication` module), not `User` — read the actor as `authentication.user`.
- Use case collaborators are Protocols injected through the constructor: `repository` always; `cache: I{Entity}Cache` when the module caches; `service: I{Name}Service` when it wraps an external or stateful system; `shared_service: SharedUseCases` when it notifies or looks up users (call `disable_exceptions()` for `None`-on-miss lookups).
- Partial updates use the `UNSET` sentinel: the update mapper sets omitted fields to `UNSET`; the use case keeps the existing value wherever a field `is UNSET`.
- Postgres is the source of truth; Redis is cache-aside. The **use case** owns TTL and invalidation policy; cache classes only execute reads and writes. Keys hang off `settings.REDIS_NAMESPACE` (`{REDIS_KEY_PREFIX}:v{REDIS_CACHE_VERSION}`) — bump `REDIS_CACHE_VERSION` to strand a stale payload format instead of flushing.
- Cache invalidation writes a tombstone **before** deleting the entry, and `insert` skips the write when a tombstone exists — this closes the race where a slow reader repopulates a just-revoked entry. Reference: `RedisKeyCache`.
- New ORM models must be imported in `migrations/env.py` and added to its `_ = [...]` list, or Alembic autogenerate will not see them.
- New endpoints must be registered in the matching `SECURITY_*_ALLOWED_PATHS` tier in `app/core/settings.py` (both slash forms) — a missing entry returns 403 even with a valid token.
- WebSocket routes authenticate with `authenticate_websocket`, which validates the `Origin` header against `SECURITY_ALLOW_ORIGINS` before checking the cookie-borne token; `CORSMiddleware` does not cover the WS handshake.

## Naming Conventions

| Component | Pattern | Example |
|-----------|---------|---------|
| Module directory | snake_case | `knowledge`, `notification` |
| Domain entity | PascalCase | `Key`, `Knowledge` |
| Paginated companions | `{Entity}List`, `{Entity}Pagination` | `KeyList`, `KeyPagination` |
| ORM model | PascalCase + Model | `KeyModel`, `NotificationModel` |
| Repository interface | I + PascalCase + Repository | `IKeyRepository` |
| Repository implementation | Postgres + PascalCase + Repository | `PostgresKeyRepository` |
| Cache interface | I + PascalCase + Cache | `IKeyCache` |
| Cache implementation | Redis + PascalCase + Cache | `RedisKeyCache` |
| Service interface | I + PascalCase + Service | `IKeyService`, `IConnectionManagerService` |
| Service implementation | PascalCase (describes the service) | `KeyService`, `ConnectionManager` |
| Use case class | PascalCase + UseCases | `KeyUseCases` |
| Generic exception | PascalCase + Exception | `KeyException` |
| Specific exception | PascalCase + describes the failure | `KeyNotFoundException` |
| Request schema | PascalCase + Request | `CreateRequest`, `UpdateRequest` |
| Response schema | PascalCase + Response | `CreateResponse`, `GetAllResponse` |
| Pagination params | PascalCase + PaginationParams | `KeyPaginationParams` |
| Mapper functions | `{action}_entity_mapper`, `entity_{action}_mapper`, `model_entity_mapper`, `entity_model_mapper`, `entity_cache_mapper`, `cache_entity_mapper` | |
| Database table | `{APPLICATION_TABLE_PREFIX}_{plural_snake}` | `..._keys`, `..._knowledges` |
| Enum type name | `{snake}_enum` | `role_enum`, `notification_type_enum` |
| Constraint / index names | `uq_/ix_/ck_{plural}_{cols}` | `uq_keys_hashed_key`, `ix_keys_prefix` |
| Router prefix | `/api/v1/{kebab}` | `/api/v1/key` |
| Test file | `test_{layer}_{file}.py` | `test/modules/key/test_application_use_cases.py` |

## Authentication

Tokens are **nested JWTs** — a JWS signed with Ed25519 wrapped in a JWE encrypted with
ECDH-ES + A256GCM (`jwcrypto`) — delivered in **cookies**, not `Authorization` headers, alongside
a device-id cookie from `DeviceIdMiddleware`. HMAC-SHA256 fingerprints of each token's `jti` are
stored so tokens can be revoked and tampering detected. Key pairs load from PEM files under
`secrets/keys/` and auto-generate on first boot when `JWT_AUTO_GENERATE_KEYS` is set.

```python
from typing import Annotated

from fastapi import Depends

from app.core.security import (
    authenticate_user,
    authenticate_manager,
    authenticate_admin,
    no_authentication,
)
from app.modules.authentication.domain.entities import Authentication


authentication: Annotated[Authentication, Depends(authenticate_user)]     # any authenticated user
authentication: Annotated[Authentication, Depends(authenticate_manager)]  # manager role or above
authentication: Annotated[Authentication, Depends(authenticate_admin)]    # admin only
_: Annotated[None, Depends(no_authentication)]                            # public endpoint
```

Read the actor as `authentication.user` (a `User` entity). Role tiers are enforced twice: by the
dependency and by the `SECURITY_*_ALLOWED_PATHS` allowlists. Other dependencies:
`authenticate_refresh`, `authenticate_logout`, `authenticate_websocket`, `authenticate_api_key`.

## Registering a New Module

After a module gains routes, wire it in two places (or run `/register-module`):

1. `app/app.py` — import the router, append it to the `routers` list (alphabetical), and add the tag inside `custom_openapi()`.
2. `app/core/settings.py` — add each endpoint's path rules (both slash forms) to the matching `SECURITY_*_ALLOWED_PATHS` tier. Tiers cascade: `USER` includes `NO_AUTH`, `MANAGER` includes `USER`, `ADMIN` includes `MANAGER`.

## Available Slash Commands

Commands in `.claude/commands/` are thin entry points that `@`-include the full procedure from
the paired skill in `.claude/plugins/fastapi-ddd-scaffolder/skills/`. The skill file is the
single source of truth, so the two surfaces cannot diverge: commands are manual `/name`
triggers, and the same skills are invoked automatically when the task is described naturally.

| Command | What it does |
|---------|--------------|
| `/create-feature` | End-to-end feature: discovery → confirmed plan → ordered generation across layers |
| `/create-module` | Scaffolds a full four-layer module with canonical stub files |
| `/create-endpoint` | One endpoint across every layer + allowlist registration |
| `/create-entity` | Domain entity dataclass with validation and paginated companions |
| `/create-value-object` | Value object with `_normalize` / `_validate` / `__str__` / `__eq__` |
| `/create-exception` | Generic `{Module}Exception` plus one exception per business rule |
| `/create-model` | SQLAlchemy ORM model extending `BaseModel` + Alembic registration |
| `/create-migration` | Autogenerate, review, and apply an Alembic revision |
| `/create-seed-migration` | Hand-written data seed with raw SQL and a reversible downgrade |
| `/create-schema` | Pydantic v2 request/response schemas with full `Field` and `ConfigDict` |
| `/create-mapper` | automapper functions for schema↔entity, model↔entity, and cache serialization |
| `/create-repository-method` | Repository method: Protocol signature + Postgres implementation |
| `/create-cache` | `I{Entity}Cache` + `Redis{Entity}Cache` with namespace, TTL, and tombstones |
| `/create-service` | `I{Name}Service` Protocol + `infrastructure/services.py` implementation + DI |
| `/create-use-case` | `{Module}UseCases` methods with the 3-branch shape and cache-aside policy |
| `/create-docs` | `router_docs` plus per-endpoint `{action}_docs` dicts |
| `/create-router` | Endpoint handler with double-route, DI, mapper flow, error handling |
| `/register-module` | Wires a module into `app/app.py` and the security allowlists |
| `/add-setting` | Adds an env var across `.env.example`, `.env`, `settings.py`, and compose |
| `/create-test` | pytest tests via Protocol fakes; bootstraps pytest on first run |
| `/check-standards` | Audits modules against the conventions; fixes with permission |
| `/verify` | Read-only smoke check: ruff, imports, registration |
| `/sync-architecture` | Detects drift between the code and `.claude/` docs and updates them |

## Working Style

Keep responses focused and concise. Lead with the outcome, then supporting detail. Deliver what
was asked at the scope intended — if a better approach exists, say so in a sentence and continue
with the task as asked rather than quietly widening it.
