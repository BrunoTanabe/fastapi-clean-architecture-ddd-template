---
name: create-mapper
description: Creates conversion functions in application/mappers.py — schema to entity, entity to schema, model to entity, entity to model, and the cache JSON serializers — using py-automapper with explicit fields_mapping. Use when the user asks to add a mapper, wire up conversion functions, or connect a new schema, model, or cache to its entity.
argument-hint: "<module> <action>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Mapper Functions

<task>Add the conversion functions for an operation to `app/modules/{module}/application/mappers.py`, in the three-section layout: `# ENTITY / DTOS`, `# ENTITY / MODELS`, `# ENTITY / CACHE`.</task>

## Scope

- **In scope:** the mapper functions for the requested operation, and the small private helpers
  they need (`_actor_response`, `_model_user_mapper`).
- **Out of scope:** the schemas, model, and entity themselves — they must already exist, because
  every `fields_mapping` key is checked against them.
- **Done when:** the functions exist, every key matches a real attribute, and ruff is clean.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Mapper pattern). If the module caches, also read
`.claude/reference/caching.md` (cache mappers).

## Step 2 — Load live patterns

Read `app/modules/key/application/mappers.py` — the complete reference, with all three sections,
actor projections, the `_with_actors` variant, and the cache serializers. Read
`app/modules/notification/application/mappers.py` for the reserved `metadata` bridge, and
`app/modules/user/application/mappers.py` for value-object flattening.

Then read the target module's `domain/entities.py`, `infrastructure/models.py`, and
`presentation/schemas.py` so every field name lines up.

## Step 3 — Discovery

Most of this is derivable from the three files above. Ask only about:

- Which conversions the operation needs.
- Whether the response projects related actors (needs `_actor_response` plus a `_with_actors`
  model mapper) or only ids.
- Whether the model renames a reserved column.
- Whether the module caches (needs the `# ENTITY / CACHE` pair).

## Step 4 — Generate

Templates for every mapper shape are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Check field names, then lint

Walk every `fields_mapping` key against the target class attribute list. A typo here is silent:
automapper drops the unknown key and the field arrives as `None` at runtime.

Then run `uv run ruff check app/modules/{module}/application/mappers.py` and `uv run ruff format`
on it. Fix and re-run until clean.

## Rules

- `from automapper import mapper`, then `mapper.to(Target).map(source, fields_mapping={...})`.
  Build the target by hand instead when most fields need transforming — the update mapper and the
  cache mappers do exactly that.
- **Always list the inherited fields** (`id`, `is_active`, `created_at`, `updated_at`) in
  `fields_mapping` for both directions of model↔entity. automapper does not traverse parent
  dataclass `slots`, so omitting them silently drops the values.
- Three sections, in order: `# ENTITY / DTOS`, `# ENTITY / MODELS`, `# ENTITY / CACHE`.
- Naming: `{action}_entity_mapper` inbound, `entity_{action}_mapper` outbound,
  `model_entity_mapper`, `model_entity_with_actors_mapper`, `models_{entity}_list_mapper`,
  `entity_model_mapper`, `entity_cache_mapper`, `cache_entity_mapper`.
- Request mappers take `Authentication` and read the actor as `authentication.user` — never a bare
  `User`, never a `Session`.
- Update mappers set omitted fields to `UNSET` via `payload.model_fields_set`, and response mappers
  normalize `UNSET` back to `None`.
- Foreign keys become minimal entity stubs on the way in (`User(id=model.created_by)`) and are
  flattened to ids on the way out (`entity.created_by.id`). Never load a full related entity
  inside a mapper.
- Value objects serialize with `str(...)` (guarded for optionals) and are rebuilt either by the
  value-object constructor or by handing the raw string to the entity, whose `__post_init__`
  converts it.
- Renamed reserved columns bridge explicitly in both directions.
- Mappers restructure data and nothing else — no database access, no branching on business rules,
  no logging, no exceptions raised. Business decisions belong to the use case.
- `math.ceil` for `total_pages`, guarded against a zero `per_page`.
- Never map a transient secret into the cache or the model.
