---
name: create-seed-migration
description: Creates a hand-written Alembic data-seed revision that inserts reference rows with raw SQL and bound parameters, with a downgrade that removes exactly those rows. Use when the user asks to seed data, insert default rows, add a default admin or lookup values, or write a data migration. For schema changes, use create-migration.
argument-hint: "<what-to-seed>"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(uv run *), Bash(ls *)
---

# Create Data-Seed Migration

<task>Write a hand-authored Alembic revision that inserts reference data with bound parameters, and a downgrade that deletes exactly those rows.</task>

Existing revisions:

!`ls migrations/versions`

## Scope

- **In scope:** one seed revision, its downgrade, review, and application.
- **Out of scope:** schema changes. A revision never mixes the two — a rollback would then have to
  choose between losing data and keeping a column.
- **Done when:** the revision is reviewed, applied, and ruff is clean.

## Step 1 — Load the reference

1. Read `migrations/env.py` and the current head revision (the last file listed above) so
   `down_revision` chains correctly. If `migrations/versions/` is empty, the schema migration must
   be created and applied first — a seed cannot precede its table.
2. Read the target model in `infrastructure/models.py` for exact column names, nullability, and
   enum columns.
3. Read `app/core/settings.py` for any `settings.*` the seed needs.

## Step 2 — Discovery

- The target table and the rows to insert, value by value.
- Where each value comes from: a literal, or `settings.*`. Secrets — passwords, emails, tokens —
  always come from `settings`, never a literal in the file.
- The natural key that identifies the seeded rows, for the downgrade.
- Whether the upgrade should be idempotent (`ON CONFLICT DO NOTHING`). Prefer yes: it makes a
  partially applied migration re-runnable.

## Step 3 — Generate

Create the file with plain `revision`, never `--autogenerate`:

```bash
uv run alembic revision -m "insert_<what>"
```

Autogenerate would find no schema diff and emit an empty or destructive draft.

<example>
```python
from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

from app.core.security import password_hasher
from app.core.settings import settings

revision: str = "<generated>"
down_revision: Union[str, Sequence[str], None] = "<current head>"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(f"""
            INSERT INTO {settings.APPLICATION_TABLE_PREFIX}_users
            (id, first_name, last_name, preferred_name, email, hashed_password,
             role, gender, is_active, created_at, updated_at)
            VALUES
            (:id, :first_name, :last_name, :preferred_name, :email, :hashed_password,
             :role, :gender, :is_active, now(), now())
            ON CONFLICT (email) DO NOTHING
        """),
        {
            "id": str(uuid4()),
            "first_name": "System",
            "last_name": "Administrator",
            "preferred_name": "System",
            "email": settings.SECURITY_ADMIN_EMAIL,
            "hashed_password": password_hasher.hash(settings.SECURITY_ADMIN_PASSWORD),
            "role": "ADMIN",  # enum columns take the uppercase member NAME
            "gender": "OTHER",  # likewise
            "is_active": True,
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            f"DELETE FROM {settings.APPLICATION_TABLE_PREFIX}_users WHERE email = :email"
        ),
        {"email": settings.SECURITY_ADMIN_EMAIL},
    )
```
</example>

Importing application code (`settings`, `password_hasher`) is the established convention here —
it keeps the seed consistent with how the app hashes and where it reads configuration.

`ON CONFLICT` requires a unique constraint on the conflict target. Without one, guard with
`WHERE NOT EXISTS (SELECT 1 FROM ... WHERE ...)` instead.

## Step 4 — Review

```
- [ ] down_revision chains to the current head
- [ ] Every value is a bound parameter (:name) — the f-string interpolates only the table prefix
- [ ] Enum values are uppercase member NAMES
- [ ] Secrets come from settings, not literals
- [ ] Timestamps use SQL now(); ids use str(uuid4())
- [ ] The upgrade is idempotent, or the guard is deliberately omitted
- [ ] downgrade() deletes exactly the seeded rows, by natural key
- [ ] No schema operations in this file
```

Run `uv run ruff check migrations` and fix any finding.

## Step 5 — Confirm, then apply

Show the file and confirm with the user before applying — a seed writes rows that a downgrade may
not be able to distinguish from real data later.

```bash
uv run alembic upgrade head
```

Confirm the `Running upgrade` line.

## Rules

- `conn = op.get_bind()` plus `sa.text(...)`. The f-string interpolates only
  `settings.APPLICATION_TABLE_PREFIX`; every value is a bound parameter, which keeps the SQL
  injection-safe and correctly typed.
- Enum columns receive the uppercase member **NAME** (`"ADMIN"`, `"OTHER"`,
  `"KNOWLEDGE_CREATED"`). PostgreSQL stores names, not the lowercase Python values — this is the
  single most common seed bug.
- `downgrade()` deletes by the natural key used in `upgrade()`. Never `DELETE FROM table` without
  a predicate; it would remove rows the seed did not create.
- One seed concern per revision.
- Never edit an applied seed. Write a follow-up revision.
- The app auto-upgrades on startup, so a seed left in the tree will run on the next boot. Do not
  leave an unreviewed one behind.
