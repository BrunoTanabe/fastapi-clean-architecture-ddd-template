---
name: create-service
description: Creates a service for a module — an I{Name}Service Protocol in application/interfaces.py, its implementation in infrastructure/services.py, and the DI factory, for wrapping an external system or a stateful in-process component such as email, storage, queues, token generation, or real-time delivery. Use when the user asks to add a service, integrate an external system, or put infrastructure logic behind a Protocol.
argument-hint: "<module> <ServiceName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Service

<task>Add a service to a module: the `I{Name}Service` Protocol, the implementation in `infrastructure/services.py`, and the `get_{name}_service` factory. Use cases depend on the Protocol only.</task>

## Scope

- **In scope:** the Protocol, the implementation, the factory, and the constructor wiring in the
  use case that will call it.
- **Out of scope:** the business logic that decides *when* to call the service — that stays in the
  use case.
- **Done when:** the Protocol and implementation signatures match, the factory returns the Protocol
  type, and ruff is clean.

## Step 1 — Decide whether this is a service at all

A service wraps an external system or a stateful in-process component. It is not the right home
for:

- database access — that is a repository;
- Redis access — that is a cache;
- pure computation over domain data — that belongs in the entity or `application/utils.py`;
- orchestration across collaborators — that is the use case.

If none of those fit, continue.

## Step 2 — Load the reference

Read `.claude/architecture.md` (Service pattern, Dependencies pattern).

## Step 3 — Load live patterns

Three live references, each a different shape:

- `app/modules/key/infrastructure/services.py` — the **stateless** minimum: `KeyService` wraps one
  `core.security` helper behind `IKeyService`.
- `app/modules/authentication/application/interfaces.py` — `ITokenService`, a stateless service
  with a wider surface.
- `app/modules/websocket/infrastructure/services.py` plus
  `app/modules/websocket/presentation/dependencies.py` — the **stateful singleton**:
  `ConnectionManager` is created in the lifespan, stored on `app.state`, and retrieved by
  `get_connection_manager`.

## Step 4 — Discovery

- Module and service name (`notification` + `EmailSender` → `IEmailSenderService`).
- The method surface: domain entities in, domain entities or `None` out. Never schemas, never ORM
  models.
- Lifecycle: **stateless per-request** (constructed in the factory) or **stateful singleton**
  (created in the lifespan, stored on `app.state`).
- Which `settings.*` values it needs. New env vars go through `/add-setting`, never `os.environ`.
- Whether a failure should break the request or degrade gracefully.

## Step 5 — Generate

Templates are in [TEMPLATES.md](TEMPLATES.md). Generate in this order so imports always resolve:

1. `I{Name}Service` in `application/interfaces.py` (bodies `...`).
2. The implementation in `infrastructure/services.py`.
3. `get_{name}_service` in `presentation/dependencies.py`. For a singleton, also add its creation
   to `startup()` in `app/core/resources.py`.
4. `service: I{Name}Service` on the use-case constructor and on `get_{module}_use_cases`.

Use `Edit` for files that already exist.

## Step 6 — Lint

Run `uv run ruff check` on every touched file and `uv run ruff format` on them. Fix and re-run
until clean.

Confirm the Protocol and implementation signatures match exactly — `Protocol` conformance is
structural and unchecked at runtime.

## Rules

- 2-branch try/except, the same shape as repositories: `except StandardException: raise`, then
  `except Exception as e: logger.opt(exception=e).error(...); raise {Module}Exception()`. Services
  have no `DomainError` branch — they never evaluate domain rules.
- A trivially thin wrapper over a `core` helper may skip the try/except entirely when the helper
  already handles its own errors — `KeyService.generate` is a one-line delegation and does exactly
  that. Add the branches as soon as the method does real work.
- The factory's return annotation is the Protocol, never the concrete class. That annotation is
  what keeps the implementation swappable.
- Stateless services are constructed per request in the factory, with no arguments where possible.
- Stateful singletons are created in the lifespan in `app/core/resources.py`, stored on
  `app.state`, and read from `HTTPConnection.app.state` in the factory. Never a module-level global.
- Configuration comes from `settings`, never `os.environ` and never a hardcoded host, URL, or
  credential.
- Never surface an upstream system's raw error text to the client — it can leak internal hosts and
  credentials. Log the original and raise the module's own exception.
- Failures the caller treats as best-effort are logged with `logger.opt(exception=e).warning(...)`
  by the *caller*, not swallowed by the service. Reference:
  `SharedUseCases._dispatch_user_notification_message`.
- `domain/` never imports a service; use cases depend on the Protocol only.
