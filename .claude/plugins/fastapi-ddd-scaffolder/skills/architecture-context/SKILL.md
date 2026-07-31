---
name: architecture-context
description: Loads the canonical architecture of this FastAPI Clean Architecture and DDD template — the four layers, module file layout, shared base types, the three error-handling shapes, and naming conventions. Use before generating or modifying any module component (entity, value object, model, repository, cache, service, use case, mapper, schema, router, docs, dependencies), and when the user asks to explain the architecture or the project conventions.
user-invocable: false
allowed-tools: Read, Glob, Grep
---

# Architecture Context

Read `.claude/architecture.md` now, before generating or modifying code. It is the canonical
description of layer responsibilities, shared types, conventions, and error patterns.

## What the reference covers

- Project layout, the nine modules with their real status, and per-layer file responsibilities.
- The three error-handling shapes and which layer each belongs to.
- The `shared` module surface: `BaseEntity`, `PaginatedList`, `Pagination`, the `UNSET` sentinel,
  the shared value objects `Email` / `Name` / `Phone`, `RESOURCE_NAME_PATTERN`, exceptions,
  response schemas, cross-module dependencies, and `SharedUseCases`.
- Inherited fields from `BaseModel` (ORM) and `BaseEntity` (domain), and which models extend
  `Base` directly instead.
- Canonical code for every pattern: entity, use case, repository, mapper, schema, router,
  dependencies, docs, service.
- Middleware, lifespan, and WebSocket delivery.
- Module registration in `app/app.py` and the `SECURITY_*_ALLOWED_PATHS` tiers.
- Testing layout and the full naming reference.

## Deeper references

Read the one that matches the work — each is self-contained and linked directly from
`architecture.md`:

- `.claude/reference/shared-module.md` — the `shared` export surface, `SharedUseCases` semantics,
  the `UNSET` partial-update protocol, value-object placement policy.
- `.claude/reference/persistence.md` — ORM columns, enum storage, the reserved `metadata` rename,
  constraints, cascades, Alembic registration and the migration workflow.
- `.claude/reference/caching.md` — Redis namespace and versioning, key shapes, the tombstone
  protocol, the never-raise policy, cache mappers, cache-aside policy.
- `.claude/reference/security.md` — nested JWT, the `authenticate_*` dependencies, WebSocket and
  API-key authentication, the allowlist tiers.

## Facts that are easy to get wrong

- Routers inject `Authentication` (from the `authentication` module), never `User`. The actor is
  `authentication.user`.
- `Email`, `Name`, and `Phone` live in `shared/domain/value_objects.py`, not in `user/`.
- Paginated modules subclass `PaginatedList` — they do not declare their own `total`.
- Module enums live in `domain/enums.py`; exceptions in `application/exceptions.py`; mappers in
  `application/mappers.py`.
- The cache layer is implemented and in production use (`key`, `authentication`). Caches never
  raise.
- `key` is the most complete module and the best model for anything new.

## When a pattern is ambiguous

Read two recently modified non-`shared`, non-`example` modules directly. Patterns repeated across
modules are authoritative; a deviation in a single module is likely a bug, not a new convention.
