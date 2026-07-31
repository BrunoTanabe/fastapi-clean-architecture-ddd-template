# Canonical Project Sources

The files `sync-architecture` reads to derive the true patterns before reporting drift.

## Contents

- [Shared base types](#shared-base-types)
- [Reference modules](#reference-modules)
- [Core infrastructure](#core-infrastructure)
- [Wiring and configuration](#wiring-and-configuration)
- [Project metadata](#project-metadata)
- [Documentation targets](#documentation-targets)
- [What each file proves](#what-each-file-proves)

## Shared base types

Authoritative. A pattern here overrides a conflicting pattern in any single module.

```
app/modules/shared/domain/entities.py            BaseEntity, DomainError, DomainErrors, Pagination, PaginatedList
app/modules/shared/domain/value_objects.py       UNSET, RESOURCE_NAME_PATTERN, Email, Name, Phone
app/modules/shared/domain/enums.py               ApplicationEnvironment, CookieSameSite, ResponseMessages, Role, SortOrder
app/modules/shared/infrastructure/models.py      Base, BaseModel
app/modules/shared/application/exceptions.py     StandardException, DomainException, CoreException, OriginNotAllowedException
app/modules/shared/application/use_cases.py      SharedUseCases
app/modules/shared/application/utils.py          BRASILIA_TZ, current_timestamp, resolve_client_ip
app/modules/shared/presentation/schemas.py       StandardResponse, StandardDetailsResponse, PaginationParams, PaginationMeta, CreateResponse, UpdateResponse, DeleteResponse
app/modules/shared/presentation/dependencies.py  cross-module repository, cache, and SharedUseCases factories
```

## Reference modules

Never derive a convention from a single module. Read at least two and prefer what they share.

```
app/modules/key/**            most complete: cache with tombstones, service, full CRUD + rotate,
                              actor projections, transient secret handling
app/modules/knowledge/**      CRUD + broadcast notifications via SharedUseCases; partial cache
app/modules/authentication/** multi-dimension cache, token services, entity behaviour methods
app/modules/notification/**   reserved `metadata` rename, role-cascaded fan-out
app/modules/user/**           value-object conversion, censored fields
app/modules/websocket/**      stateful singleton service, WebSocket routing
app/modules/example/**        the minimal module shape
```

`shared` is not a module template — never derive a module pattern from it.

## Core infrastructure

```
app/core/settings.py          Settings fields, validators, computed fields, SECURITY_*_ALLOWED_PATHS tiers
app/core/security.py          authenticate_* dependencies, nested JWT, password and API-key helpers
app/core/cache.py             Redis pool, get_cache_session, init/flush/close
app/core/database.py          sync and async engines, get_async_session
app/core/resources.py         lifespan: startup order, app.state singletons, DEV extras
app/core/middleware.py        LogRequestMiddleware, ResponseFormattingMiddleware, DeviceIdMiddleware
app/core/exception_handler.py global handlers
app/core/migrations.py        Alembic auto-upgrade on startup
app/core/logging.py           loguru configuration
```

## Wiring and configuration

```
app/app.py                    router list, OpenAPI tags, security schemes, production toggles
migrations/env.py             the model registration list
migrations/versions/          whether any revision exists yet
scripts/create_module.py      MODULE_STRUCTURE — the authoritative module file layout
.env.example                  the configuration contract for a fresh clone
docker-compose.yaml           service images, ports, project name
Makefile                      the commands the docs advertise
```

`scripts/create_module.py` is the single best check for file-layout drift: if a canonical file
moved between layers, `MODULE_STRUCTURE` is where it shows up first.

## Project metadata

```
pyproject.toml                requires-python, dependencies, dev dependencies, tool config
.python-version               the pinned interpreter
Dockerfile                    the base image and exposed port
test/modules/                 which modules have test packages; whether pytest is installed
```

## Documentation targets

The files that may need updating once drift is confirmed:

```
CLAUDE.md
.claude/architecture.md
.claude/reference/{shared-module,persistence,caching,security}.md
.claude/README.md
.claude/plugins/fastapi-ddd-scaffolder/README.md
.claude/plugins/fastapi-ddd-scaffolder/.claude-plugin/plugin.json
.claude/plugins/fastapi-ddd-scaffolder/skills/*/SKILL.md
.claude/plugins/fastapi-ddd-scaffolder/skills/*/{TEMPLATES,CHECKLIST,PLAN_TEMPLATE,CANONICAL_SOURCES}.md
.claude/commands/*.md         frontmatter only
```

## What each file proves

| Question | Read |
|----------|------|
| What does a module's file layout look like? | `scripts/create_module.py` |
| Which fields are inherited? | `shared/domain/entities.py`, `shared/infrastructure/models.py` |
| Where does a value object live? | `shared/domain/value_objects.py` plus each module's |
| Which error shape belongs to which layer? | `key/application/use_cases.py`, `key/infrastructure/repositories.py`, `key/infrastructure/caches.py` |
| Is the cache layer live? | `key/infrastructure/caches.py` and whether `KeyUseCases` calls it |
| What does a router handler look like? | `key/presentation/routers.py` |
| Which auth dependencies exist? | `app/core/security.py` |
| Which endpoints are in which tier? | `app/core/settings.py` |
| Which modules are registered? | `app/app.py` |
| Which models does Alembic see? | `migrations/env.py` |
| What Python version? | `.python-version`, `pyproject.toml`, `Dockerfile` |
| What is the project actually called? | `pyproject.toml`, `docker-compose.yaml`, `.env.example` |
