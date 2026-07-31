# Reference — Persistence (ORM, Constraints, Migrations)

SQLAlchemy 2 model conventions and the Alembic workflow.

## Contents

- [Model skeleton](#model-skeleton)
- [Column declarations](#column-declarations)
- [Enum columns](#enum-columns)
- [The reserved `metadata` name](#the-reserved-metadata-name)
- [Foreign keys and relationships](#foreign-keys-and-relationships)
- [Constraints and indexes](#constraints-and-indexes)
- [Models that extend `Base` directly](#models-that-extend-base-directly)
- [Alembic registration](#alembic-registration)
- [Schema migration workflow](#schema-migration-workflow)
- [Data seed migrations](#data-seed-migrations)
- [Session and transaction rules](#session-and-transaction-rules)

## Model skeleton

`KeyModel` is the canonical reference. Every business table extends `BaseModel`, which supplies
`id`, `is_active`, `created_at`, and `updated_at` — never redeclare them.

```python
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint, UUID as SQUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.infrastructure.models import BaseModel

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class MyEntityModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_my_entities"
    __table_args__ = (
        UniqueConstraint("name", name="uq_my_entities_name"),
        Index("ix_my_entities_created_by", "created_by"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        name="name",
        comment="Human-readable name of the record",
        nullable=False,
    )
```

`__tablename__` is always the f-string form so the prefix stays env-driven.
`APPLICATION_TABLE_PREFIX` is empty in `.env.example` — never hardcode a literal prefix into a
table name, an index name, or a `ForeignKey` target.

## Column declarations

Every `mapped_column` declares, in this order: the SQLAlchemy type, `name=`, `comment=`,
`nullable=`, then optional `default=` / `server_default=` / `unique=` / `index=`.

| Need | Type |
|------|------|
| Bounded text | `String(n)` |
| Unbounded text | `Text` |
| Timestamps | `DateTime(timezone=True)` |
| UUID | `SQUID(as_uuid=True)` (`from sqlalchemy import UUID as SQUID`) |
| JSON payload | `JSONB` |
| Boolean flag | `Boolean` |
| Enum | `SQLEnum(...)` — see below |

Nullable columns declare `Mapped[T | None]` and `default=None`.

## Enum columns

```python
from sqlalchemy import Enum as SQLEnum

notification_type: Mapped[NotificationType] = mapped_column(
    SQLEnum(NotificationType, name="notification_type_enum"),
    name="notification_type",
    comment="Event type that triggered this notification",
    nullable=False,
)
```

- Never pass `create_type` — no model in the project does; Alembic autogenerate emits the PG type.
- The `name` must be unique across the whole database. Reuse the same `name` when two models store
  the same enum (`role_enum` is shared by `UserModel` and `AccessTokenModel`).
- **PostgreSQL stores the uppercase member NAMES** (`ADMIN`, `KNOWLEDGE_CREATED`), not the
  lowercase Python values. The ORM converts automatically, but raw SQL and seed migrations must
  use the uppercase names.

Known deviation: `NotificationModel.originated_from_broadcast` stores a `Role` as `String(20)`
because it is a nullable provenance marker, not a constrained domain column. New enum columns use
`SQLEnum`.

## The reserved `metadata` name

`metadata` is reserved by SQLAlchemy's Declarative API. When an entity has a `metadata` field, the
model renames the Python attribute and keeps the database column name:

```python
notification_metadata: Mapped[dict | None] = mapped_column(
    JSONB,
    name="metadata",
    comment="Optional JSON payload with internal context data (resource_id, etc.)",
    nullable=True,
    default=None,
)
```

The mapper bridges the two names in both directions:

```python
"metadata": model.notification_metadata          # model → entity
"notification_metadata": entity.metadata         # entity → model
```

## Foreign keys and relationships

```python
created_by: Mapped[UUID] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_users.id", ondelete="RESTRICT"),
    name="created_by",
    comment="Identifier of the user who created the record",
    nullable=False,
)

creator: Mapped["UserModel"] = relationship(
    "UserModel",
    foreign_keys=[created_by],
    lazy="noload",
)
```

- Cross-module model imports go under `if TYPE_CHECKING:` with the string form in
  `relationship("OtherModel", ...)` to avoid circular imports.
- `lazy="noload"` on every relationship — loading is explicit via `joinedload(...)` in the
  repository when a response needs the related row.
- When a model has two FKs to the same table (`created_by` / `updated_by`), each relationship must
  declare `foreign_keys=[...]` or SQLAlchemy cannot disambiguate.
- `ondelete` choice: `RESTRICT` for actor references (an audited row must not lose its author),
  `CASCADE` for owned children.

Parent-owned cascade (reference: `AuthenticationModel.refresh_token`):

```python
refresh_token: Mapped["RefreshTokenModel | None"] = relationship(
    back_populates="authentication",
    uselist=False,
    cascade="all, delete-orphan",
    passive_deletes=True,
    lazy="noload",
)
```

For a 1:N collection the shape is the same with `Mapped[list["ChildModel"]]` and no `uselist`.
The child's FK carries `ondelete="CASCADE"`.

## Constraints and indexes

`__table_args__` is a tuple — a single element needs a trailing comma.

```python
__table_args__ = (
    UniqueConstraint("hashed_key", name="uq_keys_hashed_key"),
    Index("ix_keys_prefix", "prefix"),
    Index("ix_keys_created_by", "created_by"),
)
```

Naming: `uq_{plural}_{cols}`, `ix_{plural}_{cols}`, `ck_{plural}_{rule}` — the short plural form,
without the table prefix.

A natural key gets a composite `UniqueConstraint` plus a matching `Index` for lookups:

```python
__table_args__ = (
    UniqueConstraint("user_id", "user_agent", "device", name="uq_authentications_user_id_user_agent_device"),
    Index("ix_authentications_user_id_user_agent_device", "user_id", "user_agent", "device"),
)
```

For XOR ownership (a row owned by exactly one of two parents), pair a `CheckConstraint` with an
entity `__post_init__` check:

```python
CheckConstraint("num_nonnulls(a_id, b_id) = 1", name="ck_my_entities_single_owner")
```

Index every FK you filter or sort on — Postgres does not create them automatically.

## Models that extend `Base` directly

`AlembicModel` (the `alembic_version` table) and the authentication token models
(`AuthenticationModel`, `RefreshTokenModel`, `AccessTokenModel`) extend `Base`, not `BaseModel`.
They are lifecycle records with their own columns, not soft-deletable business rows. Do not copy
them as a template, and do not "fix" them to extend `BaseModel`.

## Alembic registration

A model invisible to `migrations/env.py` is invisible to autogenerate. Two edits per new model:

```python
from app.modules.my_module.infrastructure.models import MyEntityModel

_ = [
    AccessTokenModel,
    AlembicModel,
    AuthenticationModel,
    KeyModel,
    KnowledgeModel,
    MyEntityModel,        # keep the list alphabetical
    NotificationModel,
    RefreshTokenModel,
    UserModel,
]
```

## Schema migration workflow

```bash
uv run alembic revision --autogenerate -m "create_my_entity_model"
# review the generated file, then:
uv run alembic upgrade head
```

`make migration m="create_my_entity_model"` and `make migrate` wrap the same commands.

Review the generated revision before applying:

- `down_revision` chains to the current head.
- Constraint and index names match the short convention (autogenerate sometimes invents names).
- Column `comment=` values survived.
- Enum types are created before the columns that use them.
- `downgrade()` reverses the change. By project convention it drops tables and indexes but does
  **not** drop PG enum types.
- No unrelated drops — a model missing from `env.py` makes autogenerate emit a `drop_table` for a
  live table.

`migrations/versions/` ships empty. In a fresh project the first autogenerate produces the initial
schema, and the app applies it on startup via `core/migrations.py`.

## Data seed migrations

Write seeds by hand — never autogenerate them.

```bash
uv run alembic revision -m "seed_default_roles"
```

Rules:

- Raw SQL through `op.execute(sa.text(...))` with **bound parameters**, never f-string
  interpolation.
- Enum values use the uppercase member NAMES (`'ADMIN'`, `'OTHER'`), matching what PostgreSQL
  stores.
- `downgrade()` must remove exactly the rows the upgrade inserted — match on a stable natural key,
  never `DELETE FROM table`.
- Make the upgrade idempotent (`ON CONFLICT DO NOTHING` or a `WHERE NOT EXISTS` guard) so a
  partially applied migration can be re-run.
- Never read `settings` for secrets at migration time except where the existing admin seed already
  does; the revision must be reproducible.

## Session and transaction rules

- Repositories call `await self.session.flush()`, never `commit()`. The request lifecycle owns the
  transaction, so a commit inside a repository would break atomicity across use-case steps.
- Repositories return domain entities via mappers, never ORM models. An ORM model escaping the
  infrastructure layer leaks lazy-loading and session state into the application layer.
- `self.session.get(Model, id)` for a primary-key fetch, `select(...)` with `scalar()` /
  `execute()` for anything else.
- Filter `is_active.is_(True)` on reads unless the caller must distinguish "revoked" from "absent"
  — `PostgresKeyRepository.get_key_by_hashed_key` deliberately omits the filter so the API-key
  auth path can tell a revoked key from an invalid one.
