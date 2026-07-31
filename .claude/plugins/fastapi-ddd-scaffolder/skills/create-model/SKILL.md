---
name: create-model
description: Creates a SQLAlchemy ORM model extending BaseModel in infrastructure/models.py — columns with name and comment, enum columns, foreign keys, relationships, constraints and indexes — then registers it in migrations/env.py so Alembic autogenerate can see it. Use when the user asks to add a database model, create an ORM model, add a table, or persist an entity.
argument-hint: "<module> <EntityName>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *)
---

# Create SQLAlchemy ORM Model

<task>Add an ORM model to `app/modules/{module}/infrastructure/models.py` extending `BaseModel`, then register it in `migrations/env.py`.</task>

## Scope

- **In scope:** the model class, its constraints and relationships, and the `migrations/env.py`
  registration.
- **Out of scope:** generating or applying the migration. Registration is required here because
  autogenerate is blind without it; running the revision is `/create-migration`.
- **Done when:** the model exists, it is in the `_ = [...]` list, ruff is clean, and the migration
  step is named as the follow-up.

## Step 1 — Load the reference

Read `.claude/reference/persistence.md` — column declarations, enum columns, the reserved
`metadata` name, foreign keys and relationships, constraints, Alembic registration.

## Step 2 — Load live patterns

1. Read `app/modules/key/infrastructure/models.py` — the canonical `BaseModel` reference, with
   dual actor FKs, disambiguated relationships, a unique constraint and three indexes.
2. Read `app/modules/notification/infrastructure/models.py` for the enum column and the reserved
   `metadata` rename.
3. Read `app/modules/shared/infrastructure/models.py` to confirm the inherited fields.
4. Read `migrations/env.py` for the registration list.

The authentication token models and `AlembicModel` extend `Base` directly — they are lifecycle
records, not a template to copy.

## Step 3 — Discovery

Derive what you can from the entity in `domain/entities.py`; ask only about what the entity cannot
tell you:

- Table suffix in plural snake_case (becomes `{APPLICATION_TABLE_PREFIX}_{plural}`).
- Per column: SQL type and length, nullable, default, unique, indexed.
- Which entity fields are *not* persisted — transient secrets such as `plain_key` never get a
  column.
- Enum columns, and whether the PG type name is new or shared with an existing model.
- Foreign keys: target table, `ondelete` semantics, and whether the response needs the related row
  (which decides if a `relationship` is worth declaring).
- Composite unique constraints (natural keys) and CHECK constraints.
- Any field named `metadata` — it needs the reserved-name rename.

## Step 4 — Generate

Templates for every column and constraint shape are in [TEMPLATES.md](TEMPLATES.md).

## Step 5 — Register for Alembic

Two edits in `migrations/env.py`:

```python
from app.modules.{module}.infrastructure.models import {Entity}Model

_ = [
    ...,
    {Entity}Model,   # keep the list alphabetical
    ...,
]
```

A model missing from that list is invisible to autogenerate, and worse — autogenerate will emit a
`drop_table` for its live table.

## Step 6 — Lint

Run `uv run ruff check app/modules/{module}/infrastructure/models.py migrations/env.py` and
`uv run ruff format` on the same files. Fix and re-run until clean.

Then name the follow-up: `/create-migration` to autogenerate, review, and apply the revision.

## Rules

- Extend `BaseModel` from `shared.infrastructure.models`. Never redeclare `id`, `is_active`,
  `created_at`, `updated_at`.
- `__tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_{plural_snake}"` — always the f-string
  form. Never hardcode a prefix into a table name, an index name, or a `ForeignKey` target.
- Every `mapped_column` declares, in order: the SQLAlchemy type, `name=`, `comment=`, `nullable=`,
  then optional `default=` / `server_default=`.
- `String(n)` for bounded text, `Text` for unbounded, `DateTime(timezone=True)` for timestamps,
  `SQUID(as_uuid=True)` for UUIDs, `JSONB` for JSON.
- Enum columns: `SQLEnum(EnumClass, name="{snake}_enum")` — never pass `create_type`. The type name
  must be unique across the database, and reused verbatim when two models store the same enum.
  PostgreSQL stores the uppercase member NAMES, which matters for seed migrations and raw SQL.
- An entity field named `metadata` renames the Python attribute to `{module}_metadata` and keeps
  `name="metadata"` on the column — `metadata` is reserved by SQLAlchemy Declarative.
- Relationships always declare `lazy="noload"`. Two FKs to the same table require
  `foreign_keys=[...]` on each relationship or SQLAlchemy cannot disambiguate.
- `ondelete="RESTRICT"` for actor references, `ondelete="CASCADE"` for owned children. The parent
  side of a cascade adds `cascade="all, delete-orphan", passive_deletes=True`.
- Cross-module model imports go under `if TYPE_CHECKING:` with the string form in
  `relationship("OtherModel", ...)`.
- `__table_args__` is a tuple — a single element needs a trailing comma. Names follow
  `uq_{plural}_{cols}`, `ix_{plural}_{cols}`, `ck_{plural}_{rule}`, without the table prefix.
- Index every foreign key you filter or sort on; Postgres does not create them automatically.
- Never persist a transient secret. Store the hash plus a non-secret identity fragment.
