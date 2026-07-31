---
name: create-use-case
description: Creates or extends the {Module}UseCases class in application/use_cases.py — Protocol collaborators on the constructor, the 3-branch try/except, business-rule checks, the UNSET merge for partial updates, cache-aside policy, and SharedUseCases notifications. Use when the user asks to add a use case, add business logic, orchestrate a new operation, or wire the application layer of an endpoint.
argument-hint: "<module> <operation>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Use Case

<task>Add a method to `{Module}UseCases` in `app/modules/{module}/application/use_cases.py` — or create the class — orchestrating its collaborators behind the standard 3-branch error shape.</task>

## Scope

- **In scope:** the use-case method, its constructor collaborators, and the module exceptions it
  needs to raise.
- **Out of scope:** the repository method, cache method, schema, mapper, and router. If any is
  missing, say so and name the skill that creates it rather than generating it inline.
- **Done when:** the method exists, every branch is covered, ruff is clean, and the missing
  neighbours are named.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Use case pattern, Error-handling shapes). If the operation touches
the cache, read `.claude/reference/caching.md` (cache-aside policy in the use case). If it
notifies or looks up users, read `.claude/reference/shared-module.md` (`SharedUseCases`).

## Step 2 — Load live patterns

- `app/modules/key/application/use_cases.py` — the canonical reference: cache + repository +
  service, the `UNSET` merge, a not-modified check, rotation.
- `app/modules/knowledge/application/use_cases.py` — the `SharedUseCases` variant with broadcast
  notifications and `disable_exceptions()`.
- `app/modules/shared/application/use_cases.py` — best-effort dispatch after a successful write.

Then read the module's `application/interfaces.py` and `application/exceptions.py` so you call
methods that exist and raise exceptions that exist.

## Step 3 — Discovery

- The operation and its signature — entity in, entity or `{Entity}List` out.
- The business rules to enforce, and which exception each maps to. Uniqueness checks, existence
  checks, and "nothing changed" checks are the common three.
- Whether the operation reads through the cache, invalidates it, or neither.
- Whether it notifies (per-user or broadcast) and to which role.
- For an update: which fields participate in the `UNSET` merge.

## Step 4 — Generate

Templates for the class skeleton, every CRUD shape, the merge, cache-aside, notifications, and
secret handling are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Lint

Run `uv run ruff check app/modules/{module}/application/use_cases.py` and `uv run ruff format` on
it. Fix and re-run until clean.

Then name what the operation still needs: `/create-repository-method`, `/create-cache`,
`/create-mapper`, `/create-router`, `/create-docs`.

## Rules

- One class per module, `{Module}UseCases`. Collaborators are Protocols on the constructor, in the
  order `cache`, `repository`, `service`, `shared_service`. Never instantiate a concrete
  repository, cache, or service inside the class.
- Methods are grouped under `# CREATE`, `# READ`, `# UPDATE`, `# DELETE` headers, mirroring the
  repository.
- **The 3-branch shape, in this exact order:**
  ```python
  except StandardException:
      raise
  except DomainError as e:
      raise DomainException(e)
  except Exception as e:
      logger.opt(exception=e).error("An unexpected error occurred during the ... use case.")
      raise {Module}Exception()
  ```
  `StandardException` must come first — it is an `HTTPException`, so a later branch would swallow
  every deliberate failure into a 500.
- `logger.debug` at entry and exit, `logger.info` before every raise of a business-rule exception
  and for notable decisions. Log ids and names, never secrets.
- Business rules live here, not in the router and not in the repository. A repository returning
  `None` becomes a `NotFoundException` here.
- Partial updates: fetch the stored record, merge field by field keeping the existing value
  wherever the incoming one `is UNSET`, then persist the merged entity. The repository receives a
  complete entity and never sees `UNSET`.
- Restore `created_by` from the stored record on every update — an update must never rewrite
  authorship.
- The use case owns cache policy: read-through on gets, invalidate after a successful write, TTL
  selection. Invalidate with the entity whose fields produce the *stored* key.
- Notifications go through `SharedUseCases`, never directly to `ConnectionManager`. Persist first,
  dispatch second.
- Call `self.shared_service.disable_exceptions()` in `__init__` when user lookups should return
  `None` instead of raising.
- Transient secrets are carried across a repository round-trip by hand — the repository never
  returns them.
- No FastAPI imports, no SQLAlchemy imports, no Redis imports, and nothing from
  `infrastructure/`. The use case knows only Protocols and domain types.
