---
name: create-entity
description: Creates a domain entity dataclass extending BaseEntity with __post_init__ validation, plus the companion {Entity}List and {Entity}Pagination dataclasses and the {Entity}SortField enum for paginated modules. Use when the user asks to add a domain entity, model a domain object, or add pure-Python types under domain/. For a standalone value object use create-value-object.
argument-hint: "<module> <EntityName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create Domain Entity

<task>Add an entity dataclass to `app/modules/{module}/domain/entities.py`, with its enums in `domain/enums.py`. Pure Python — no FastAPI, SQLAlchemy, or Pydantic imports.</task>

## Scope

- **In scope:** the entity dataclass, its validation, its module enums, and the paginated
  companions when the module lists records.
- **Out of scope:** the ORM model, mappers, schemas, and the repository. Name them as follow-ups;
  do not generate them here.
- **Done when:** the entity exists, ruff is clean, and the follow-up steps are listed.

## Step 1 — Load the reference

Read `.claude/architecture.md` (Domain entity pattern, Inherited fields) and
`.claude/reference/shared-module.md` (base entities, pagination types, value objects, the `UNSET`
sentinel).

## Step 2 — Load live patterns

Read `app/modules/key/domain/entities.py` and `app/modules/knowledge/domain/entities.py` — the
canonical shapes, including normalization, `RESOURCE_NAME_PATTERN` validation, and the paginated
companions. Read `app/modules/user/domain/entities.py` for the `str → value object` conversion and
sensitive-field censoring.

## Step 3 — Discovery

Ask only what you cannot infer from the module and the request:

- Business fields: name, Python type, required or optional, validation rules.
- Which fields are value objects. Reuse `Email`, `Name`, and `Phone` from
  `shared/domain/value_objects.py` when the semantics match.
- Which optional fields take part in partial updates — those default to `UNSET`, not `None`.
- Cross-field rules (a field required unless another is set; XOR ownership).
- Whether the module is paginated, and which fields are sortable.
- Whether `deactivate()` needs an override (for example to record who performed the soft delete).

## Step 4 — Generate

Templates for the entity, `UNSET` fields, value-object conversion, cross-field invariants,
paginated companions, sort-field enums, and censored fields are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Lint

Run `uv run ruff check app/modules/{module}/domain/` and `uv run ruff format` on the touched files.
Fix any finding and re-run until clean.

Then state the follow-ups the entity implies: `/create-model`, `/create-schema`, `/create-mapper`,
`/create-repository-method`.

## Rules

- `@dataclass(kw_only=True, slots=True)` always.
- Extend `BaseEntity`. Never redeclare `id`, `is_active`, `created_at`, `updated_at`. Override
  `deactivate()` only to add domain logic, and call `super().deactivate()` first.
- Every business field declares `field(default=..., repr=..., compare=...)` explicitly. `repr=True`
  only for identifying fields; `compare=True` only for identity.
- Fields that take part in partial updates default to `UNSET`, and every check on them is guarded
  with `is not UNSET`. Fields that do not default to `None`.
- Normalize before validating, inside `__post_init__`: collapse whitespace, capitalize, strip.
- `__post_init__` collects errors into a `list[str]` and raises `DomainErrors(errors)` once, so the
  caller sees every problem in one response. Value-object failures are caught as `DomainError` and
  appended to that list.
- Use `RESOURCE_NAME_PATTERN` from `shared/domain/value_objects.py` for resource-style names
  instead of writing a new regex.
- Paginated companions subclass `PaginatedList` (which supplies `total`) and `Pagination` (which
  supplies `page`, `per_page`, `sort_order`, `offset`). Never redeclare those fields.
- Enums go in `domain/enums.py` and always extend `(str, Enum)`. Reuse `Role` and `SortOrder` from
  `shared/domain/enums.py` rather than redefining them.
- Actor fields are typed as the `User` entity (`created_by: User`), not as a `UUID`. Mappers
  extract the id at the model boundary.
- Secrets follow the transient/persisted split: a transient plain field plus a persisted hashed
  field, with the transient one excluded from `repr` and `compare` (reference: `Key.plain_key` /
  `Key.hashed_key`).
- No FastAPI, SQLAlchemy, or Pydantic imports anywhere under `domain/`.
