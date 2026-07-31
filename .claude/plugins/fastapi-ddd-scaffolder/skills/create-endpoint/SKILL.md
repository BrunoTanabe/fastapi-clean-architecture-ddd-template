---
name: create-endpoint
description: Creates one complete endpoint across every layer of an existing module — schema, mapper, Protocol signature, repository method, use case, cache wiring, OpenAPI docs, router handler — and registers both path forms in the security allowlist. Use when the user asks to add an endpoint, create a CRUD operation, or wire a route end to end.
argument-hint: "<module> <operation>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Endpoint Across All Layers

<task>Add one endpoint and every piece it needs to an existing module, then register its path in the security allowlist.</task>

## Scope

- **In scope:** one endpoint, end to end, in one module.
- **Out of scope:** a second endpoint, a new module, and a migration. If the entity gained a
  persisted field, say so and point at `/create-migration` rather than generating the revision.
- **Done when:** the checklist below passes, ruff is clean, and any remaining follow-up is named.
- **Do not delegate this to subagents.** It is a single ordered pass over one module; splitting it
  across agents costs more than it saves and risks conflicting edits to the same files.

Copy this checklist and tick it off as you go:

```
Endpoint progress:
- [ ] Reference and module read
- [ ] Discovery answered
- [ ] Entity / enums updated (if needed)
- [ ] Schemas
- [ ] Mappers
- [ ] Protocol signature
- [ ] Repository method
- [ ] Cache wiring (if the module caches)
- [ ] Use case method
- [ ] Exceptions
- [ ] OpenAPI docs
- [ ] Router handler (both decorators)
- [ ] Allowlist rules (both slash forms)
- [ ] ruff clean
```

## Step 1 — Load the reference

Read `.claude/architecture.md`. Add `.claude/reference/caching.md` if the module caches and
`.claude/reference/security.md` for the allowlist tier.

## Step 2 — Read the target module

Read all four layers of the target module — you are extending it, and duplicating a type that
already exists is the most common failure here. Read `app/modules/key/` as the canonical example
of a fully built module.

## Step 3 — Discovery

1. **Purpose** — operation, HTTP method and path, one sentence of business intent.
2. **Authentication** — which `authenticate_*` dependency, which allowlist tier.
3. **Request** — fields, types, optionality, validation.
4. **Response** — shape, status code, whether related actors are projected.
5. **Business rules** — uniqueness, existence, state transitions, notifications.
6. **Persistence** — which repository methods are needed, and whether the operation reads through
   or invalidates the cache.

Ask these together, not one at a time. Where the module's existing endpoints already answer a
question, take the existing answer and say so.

## Step 4 — Generate in order

Strictly this order, so every import resolves when it is written:

1. **Entity / enums** — `domain/`, only if new fields or sort fields are required.
2. **Exceptions** — `application/exceptions.py`, for each new business rule.
3. **Schemas** — `presentation/schemas.py`.
4. **Mappers** — `application/mappers.py`.
5. **Protocol signature** — `application/interfaces.py`.
6. **Repository method** — `infrastructure/repositories.py`.
7. **Cache method** — `infrastructure/caches.py`, if the module caches.
8. **Use case method** — `application/use_cases.py`.
9. **Docs dict** — `presentation/docs.py`.
10. **Router handler** — `presentation/routers.py`, both decorators.
11. **Allowlist rules** — `app/core/settings.py`, both slash forms.

Use `Edit` throughout. Never rewrite a whole file.

For the detail of any one layer, defer to its skill: [`create-schema`](../create-schema/SKILL.md),
[`create-mapper`](../create-mapper/SKILL.md),
[`create-repository-method`](../create-repository-method/SKILL.md),
[`create-cache`](../create-cache/SKILL.md), [`create-use-case`](../create-use-case/SKILL.md),
[`create-docs`](../create-docs/SKILL.md), [`create-router`](../create-router/SKILL.md).

Reference code for the pieces most often written from scratch here is in
[TEMPLATES.md](TEMPLATES.md).

## Step 5 — Lint and close out

Run `uv run ruff check` on every touched file and `uv run ruff format` on them. Fix and re-run
until clean.

Then report:

- Whether the module is registered in `app/app.py`; if not, point at `/register-module`.
- Whether a model field changed; if so, point at `/create-migration`.

## Rules

- Every rule from the per-layer skills applies. The ones that most often go wrong when generating
  a whole endpoint in one pass:
- Two route decorators, including on parameterized paths, and both slash forms in the allowlist.
  Missing either produces a 403 that looks like an auth bug.
- Handlers inject `Authentication`, never `User`.
- The handler body is `payload → mapper → use case → mapper → return`, nothing else.
- The 3-branch try/except in the router and the use case, `StandardException` first; the 2-branch
  form in the repository; never-raise in the cache.
- `await self.session.flush()`, never `commit()`.
- Repositories return entities, never ORM models.
- Inherited fields are listed explicitly in every model↔entity `fields_mapping`.
- Partial updates merge in the use case; the repository never sees `UNSET`.
- The response model in the docs dict matches the handler's return annotation.
