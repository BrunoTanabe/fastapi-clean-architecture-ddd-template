# Feature Plan Template

The shape to use when presenting a feature plan. Wait for explicit confirmation before generating
code.

## Plan format

```
## Feature Plan: {Name}

### Summary
{One or two sentences: what the feature does and who uses it.}

### Scope
- New module: yes/no → {module_name}
- Affected modules: {list}
- Out of scope: {anything deliberately excluded}

### Entities
| Entity | New / Existing | Key fields | Paginated |
|--------|----------------|------------|-----------|

### Endpoints
| # | Method | Path | Auth tier | Status | Description |
|---|--------|------|-----------|--------|-------------|

### Business rules
| Rule | Enforced in | Exception | Status |
|------|-------------|-----------|--------|

### Integrations
- Caching: {none / which lookups, which TTL, which invalidation points}
- Notifications: {none / per-user or broadcast, target role}
- Services: {none / which external or stateful system}
- New settings: {none / list}

### Components
| File | Action |
|------|--------|
| domain/enums.py | new / update / — |
| domain/value_objects.py | new / update / — |
| domain/entities.py | new / update / — |
| application/exceptions.py | new / update / — |
| application/interfaces.py | new / update / — |
| application/mappers.py | new / update / — |
| application/use_cases.py | new / update / — |
| infrastructure/models.py | new / update / — |
| infrastructure/repositories.py | new / update / — |
| infrastructure/caches.py | new / update / — |
| infrastructure/services.py | new / update / — |
| presentation/schemas.py | new / update / — |
| presentation/docs.py | new / update / — |
| presentation/dependencies.py | new / update / — |
| presentation/routers.py | new / update / — |
| app/app.py | update (router + tag) |
| app/core/settings.py | update (allowlist rules) |
| migrations/env.py | update (if a new model) |

### Migration
{Required / not required.} {Table names and columns, if required.}
```

Keep the plan factual. It is a proposal to confirm, not an argument for the feature — the user has
already decided to build it.

Flag anything that looks wrong in a sentence, then continue with the plan as asked. Do not quietly
narrow the scope or substitute a different design.

## Progress board

Render after each completed layer, not after each file:

```
Feature: {Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Module scaffold
✅ Domain (enums, value objects, entities)
✅ Application (exceptions, interfaces, mappers, use cases)
⏳ Infrastructure (models, repositories, caches)
⬜ Presentation (schemas, docs, dependencies, routers)
⬜ Wiring (app.py, allowlists, migrations/env.py)
⬜ Migration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

`✅` done, `⏳` in progress, `⬜` pending. Omit rows that do not apply.

## Completion report

When generation finishes:

```
## {Name} — complete

**Endpoints**
- {METHOD} {path} — {auth tier}

**Files changed**
- {path} — {what changed}

**Migration**
{Revision id and whether it was applied, or "not required".}

**Not done**
{Anything deferred or blocked, and why. Write "nothing" only when that is true.}

**Next**
/create-test {module} · /verify {module}
```

Report failures plainly. A checklist item that did not pass belongs under **Not done**, not
omitted.
