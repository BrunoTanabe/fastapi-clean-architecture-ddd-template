---
name: create-module
description: Scaffolds a complete four-layer module skeleton — every canonical file with a working stub, plus the mirrored test package. Use when the user asks to create a new module, scaffold a module, bootstrap a bounded context, or start a new area of the application. Follow up with create-endpoint to populate logic.
argument-hint: "<module-name>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Scaffold a New Module

<task>Generate the four-layer tree for a new module with canonical stubs. No business logic — the shell that downstream skills extend.</task>

Existing modules:

!`ls app/modules`

## Scope

- **In scope:** the module tree, the stub bodies, and `test/modules/{module}/__init__.py`.
- **Out of scope:** endpoints, migrations, and registration in `app/app.py`. A new module has no
  routes yet, so registering it would add an empty router. Name the follow-ups instead.
- **Done when:** the tree exists, ruff is clean, and the next steps are listed.

Copy this checklist and tick it off:

```
Scaffold progress:
- [ ] Reference read
- [ ] Live patterns loaded
- [ ] Discovery answered
- [ ] Tree generated
- [ ] Test package created
- [ ] ruff clean
```

## Step 1 — Load the reference

Read `.claude/architecture.md` (Project layout, Layer responsibilities).

## Step 2 — Load live patterns

Read `app/modules/key/` — the most complete module — for naming and import style. Read
`app/modules/example/` for the minimal shape a module can have.

`scripts/create_module.py` creates this exact tree with **empty** files. Prefer it when the user
wants only the bare skeleton; use this skill when the stubs should carry working bodies.

## Step 3 — Discovery

- Module name, snake_case and singular (`key`, not `keys`).
- Primary entity name, PascalCase.
- Table suffix in plural snake_case, if the module persists anything.
- The minimal business fields — just enough to scaffold.
- Whether the module needs a cache, a service, or `SharedUseCases`. When unsure, leave
  `caches.py` and `services.py` empty; adding them later is a one-file change.

## Step 4 — Generate the tree

```
app/modules/{module}/
├── __init__.py
├── application/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── interfaces.py
│   ├── mappers.py
│   ├── use_cases.py
│   └── utils.py
├── domain/
│   ├── __init__.py
│   ├── entities.py
│   ├── enums.py
│   └── value_objects.py
├── infrastructure/
│   ├── __init__.py
│   ├── caches.py
│   ├── models.py
│   ├── repositories.py
│   └── services.py
└── presentation/
    ├── __init__.py
    ├── dependencies.py
    ├── docs.py
    ├── routers.py
    └── schemas.py
```

This matches `MODULE_STRUCTURE` in `scripts/create_module.py` exactly. Every `__init__.py` is
empty; the rest use the stubs in [TEMPLATES.md](TEMPLATES.md).

Also create `test/modules/{module}/__init__.py`, empty.

## Step 5 — Lint

Run `uv run ruff check app/modules/{module}` and `uv run ruff format app/modules/{module}`. Fix and
re-run until clean.

Then list the follow-ups in order: `/create-entity`, `/create-model`, `/create-migration`,
`/create-endpoint`, `/register-module`.

## Rules

- Refuse to scaffold over an existing module directory. Check `ls app/modules` first.
- Create every file in the structure, even the ones that stay empty. The full skeleton is the
  convention — an empty `caches.py` is not a missing file.
- All `__init__.py` files are empty. This project does not re-export through packages.
- The entity extends `BaseEntity` and never redeclares `id`, `is_active`, `created_at`,
  `updated_at`.
- Reuse `UNSET`, `RESOURCE_NAME_PATTERN`, `Email`, `Name`, and `Phone` from
  `shared/domain/value_objects.py` instead of scaffolding duplicates.
- Import `CreateResponse`, `UpdateResponse`, `DeleteResponse` from `shared.presentation.schemas` —
  never redefine them.
- Mappers list the inherited fields explicitly in `fields_mapping` in both directions.
- Never copy from `shared/` — it defines base types, not a module template.
- Do not register the module in `app/app.py` or the allowlists yet. That happens once it has
  routes.
