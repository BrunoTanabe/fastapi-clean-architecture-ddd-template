---
name: create-feature
description: Orchestrates a complete business feature end to end — discovery, a confirmed plan, then ordered generation across every layer and any number of endpoints, ending with app and allowlist registration. Use when the user asks to build or implement a feature, add a capability, or describes a business need that spans several components or modules.
argument-hint: "[feature description]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Feature End-to-End

<task>Drive a feature from requirements to working code: gather what is needed, get a plan confirmed, then generate everything in dependency order.</task>

Existing modules:

!`ls app/modules`

## Scope

- **In scope:** every layer of every module the feature touches, plus registration and the
  migration for any new model.
- **Out of scope:** anything the user did not ask for. This skill generates the endpoints in the
  confirmed plan and stops. Do not add "while we're here" endpoints, extra fields, or speculative
  abstractions.
- **Done when:** the plan's components are all generated, ruff is clean, the app imports, and the
  post-generation checklist passes.

**Delegation:** do this work yourself. A single feature is a sequential pass over a small number of
files that repeatedly reference each other, so parallel agents would conflict. Delegate only when
the feature genuinely spans two or more independent modules with no shared files, and even then use
one agent per module, not more.

Copy this checklist and keep it updated:

```
Feature progress:
- [ ] Reference read
- [ ] Live patterns loaded
- [ ] Discovery answered
- [ ] Plan confirmed by the user
- [ ] Generation complete
- [ ] Post-generation checklist verified
```

## Step 1 — Load the reference

Read `.claude/architecture.md`. Add the reference files the feature actually needs:
`reference/persistence.md` for new tables, `reference/caching.md` for caching,
`reference/security.md` for auth tiers, `reference/shared-module.md` for notifications.

## Step 2 — Load live patterns

Read all four layers of `app/modules/key/` — the most complete module — and of the module the
feature extends, if it already exists. Read `app/app.py` and the allowlist tiers in
`app/core/settings.py`.

## Step 3 — Discovery

Ask these together, in one round, and mark anything the request already answers:

1. **Capability** — what problem it solves, in a sentence or two.
2. **Actors and permissions** — which roles, and whether permissions differ per operation.
3. **Data model** — a new entity or new operations on an existing one; the key fields.
4. **Operations** — per endpoint: method, path, input, output, status code.
5. **Business rules** — uniqueness, state transitions, cross-entity constraints, validation.
6. **Integrations** — notifications through `SharedUseCases`, caching, an external service, or
   effects on other modules.

Where a reasonable default exists, state the default and move on rather than asking. Ask only where
different answers lead to materially different code.

## Step 4 — Present the plan and wait

Use the shape in [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md). **Wait for explicit confirmation before
writing code.** Revising a plan is cheap; reworking eight generated files is not.

## Step 5 — Ordered generation

Strictly this order, so every import resolves when it is written:

1. **Module scaffold** — only for a new module. See [`create-module`](../create-module/SKILL.md).
2. **Domain** — `enums.py` → `value_objects.py` → `entities.py` (entity, plus `{Entity}List` and
   `{Entity}Pagination` when paginated).
3. **Application** — `exceptions.py` → `interfaces.py` → `mappers.py` → `use_cases.py`.
4. **Infrastructure** — `models.py` → `repositories.py` → `caches.py` (only when caching) →
   `services.py` (only when wrapping something).
5. **Presentation** — `schemas.py` → `docs.py` → `dependencies.py` → `routers.py`.
6. **Wiring** — router and OpenAPI tag in `app/app.py`, path rules in the allowlist tiers, new
   models in `migrations/env.py`.
7. **Migration** — generate, review, and apply, if a model changed.

Note that `mappers.py` comes before `use_cases.py`: the use case imports mappers only indirectly,
but the repository imports them directly, and writing them earlier keeps the field names settled
before three files depend on them.

Use `Edit` for existing files and `Write` only for new ones. Render the progress board from
[PLAN_TEMPLATE.md](PLAN_TEMPLATE.md#progress-board) after each layer, not after each file.

Per-component detail:

| Component | Skill |
|-----------|-------|
| Entity | [`create-entity`](../create-entity/SKILL.md) |
| Value object | [`create-value-object`](../create-value-object/SKILL.md) |
| Exceptions | [`create-exception`](../create-exception/SKILL.md) |
| ORM model | [`create-model`](../create-model/SKILL.md) |
| Schemas | [`create-schema`](../create-schema/SKILL.md) |
| Mappers | [`create-mapper`](../create-mapper/SKILL.md) |
| Repository methods | [`create-repository-method`](../create-repository-method/SKILL.md) |
| Cache | [`create-cache`](../create-cache/SKILL.md) |
| Services | [`create-service`](../create-service/SKILL.md) |
| Use cases | [`create-use-case`](../create-use-case/SKILL.md) |
| Docs | [`create-docs`](../create-docs/SKILL.md) |
| Router | [`create-router`](../create-router/SKILL.md) |
| Migration | [`create-migration`](../create-migration/SKILL.md) |
| Data seed | [`create-seed-migration`](../create-seed-migration/SKILL.md) |
| Settings | [`add-setting`](../add-setting/SKILL.md) |
| Registration | [`register-module`](../register-module/SKILL.md) |
| Tests | [`create-test`](../create-test/SKILL.md) |

## Step 6 — Close out

1. Run `uv run ruff check` on every touched file and `uv run ruff format` on them. Fix and re-run
   until clean.
2. Confirm the app still imports: `uv run python -c "import app.app"`.
3. Walk this checklist:
   ```
   - [ ] Entity fields ↔ schema fields ↔ ORM columns aligned
   - [ ] Every Protocol method has an implementation
   - [ ] Every router handler has a use-case method and a docs dict
   - [ ] Every route has both decorators
   - [ ] Every endpoint has both slash forms in the right allowlist tier
   - [ ] app.py registers the router and the OpenAPI tag
   - [ ] New models are in migrations/env.py, and the migration is applied
   - [ ] Cache invalidation covers every cached dimension
   ```
4. Report what was built, and name `/create-test` and `/verify` as the next steps.

If any item fails, say so plainly and fix it before reporting completion.
