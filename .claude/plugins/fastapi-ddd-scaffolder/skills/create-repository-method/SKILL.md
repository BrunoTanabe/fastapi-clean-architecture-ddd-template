---
name: create-repository-method
description: Adds a repository method to a module — the Protocol signature in application/interfaces.py and the Postgres implementation in infrastructure/repositories.py, interface first. Use when the user asks to add a repository method, implement a database query, add a CRUD operation, or wire persistence for a new use case.
argument-hint: "<module> <method>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Repository Method

<task>Add one repository method: the signature in `app/modules/{module}/application/interfaces.py` and the implementation in `app/modules/{module}/infrastructure/repositories.py`. Interface first, always.</task>

## Scope

- **In scope:** the Protocol signature, the implementation, and the `models_{entity}_list_mapper`
  companion when the method is a paginated read.
- **Out of scope:** the use case that calls it and the endpoint above it. Name them as follow-ups.
- **Done when:** both signatures match exactly, ruff is clean, and the caller is named.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Repository pattern) and `.claude/reference/persistence.md`
(session and transaction rules).

## Step 2 — Load live patterns

Read `app/modules/key/infrastructure/repositories.py` — the canonical reference, covering create,
get-by-id with `joinedload`, paginated `get_all` with a window function, a lookup that deliberately
skips the `is_active` filter, and two update variants. Read the module's existing
`application/interfaces.py` for the Protocol shape.

## Step 3 — Discovery

- The operation: `create`, `get_by_id`, `get_by_{field}`, `get_all` (paginated), `update`,
  `delete`, `exists_by_{field}`, or a get-or-create keyed on a natural key.
- Input parameters and return type — an entity, `{Entity}List`, `bool`, or `None`.
- Whether the read must return soft-deleted rows. Default is no; the exception is a lookup whose
  caller has to tell "revoked" from "absent".
- Whether the response needs related actors — that decides whether the query eager-loads and which
  mapper it returns through.

## Step 4 — Generate

Templates for every method shape are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Lint

Run `uv run ruff check` on both touched files and `uv run ruff format` on them. Fix and re-run
until clean.

Confirm the Protocol signature and the implementation signature match exactly — parameter names
included. `Protocol` conformance is structural and not checked at runtime, so a mismatch surfaces
only when the use case calls it.

Then name the caller: `/create-use-case` to consume the new method.

## Rules

- Update `application/interfaces.py` first, then implement. The interface is the contract the use
  case depends on; writing it first keeps the application layer from reaching for a concrete class.
- Interface methods are grouped under `# CREATE`, `# READ`, `# UPDATE`, `# DELETE` headers, and
  their bodies are `...`.
- Inputs and outputs are domain entities — never ORM models, never dicts. An ORM model escaping
  the repository leaks lazy loading and session state into the application layer.
- Methods take the whole entity (`get_by_id(self, key: Key)`), not loose primitives, so the
  repository can log the actor and the use case keeps one object in flight. The exception is a
  lookup by a value that is not an entity field on the caller's side — `get_key_by_hashed_key`
  takes a bare `str`.
- `await self.session.flush()` — never `commit()`. The request lifecycle owns the transaction.
- `entity_model_mapper` before persisting; `model_entity_mapper` (or
  `model_entity_with_actors_mapper`) before returning.
- 2-branch try/except, no `DomainError` branch: `except StandardException: raise`, then
  `except Exception as e: logger.opt(exception=e).error(...); raise {Module}Exception()`.
- `logger.info` at entry and at exit of every method, including the identifying value and the
  requesting actor where available.
- Reads filter `Model.is_active.is_(True)` unless the caller must distinguish revoked from absent
  — when you omit it, leave a comment explaining why, as `get_key_by_hashed_key` does.
- Paginated reads compute the total in the same statement with `func.count(Model.id).over()`, then
  `order_by`, `offset`, `limit`. Never issue a separate `COUNT(*)`.
- Sort columns are resolved with `getattr(Model, pagination.sort_by.value)` — which is why every
  `{Entity}SortField` member must be a real column name.
- `joinedload(...)` when the response projects a related row; without it, touching the
  relationship raises a lazy-load error under async SQLAlchemy.
- A "not found" read returns `None`. Raising the not-found exception is the use case's job — the
  repository does not know whether absence is an error.
- Merging partial updates is the use case's job too. The repository receives a complete entity and
  assigns fields unconditionally; it never inspects `UNSET`.
