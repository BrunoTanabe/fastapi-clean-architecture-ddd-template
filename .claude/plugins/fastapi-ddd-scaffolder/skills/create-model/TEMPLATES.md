# ORM Model Templates

## Contents

- [Every column shape](#every-column-shape)
- [Dual actor foreign keys](#dual-actor-foreign-keys)
- [Reserved `metadata` JSONB column](#reserved-metadata-jsonb-column)
- [Composite unique plus lookup index](#composite-unique-plus-lookup-index)
- [XOR-owner CheckConstraint](#xor-owner-checkconstraint)
- [Parent/child with delete cascade](#parentchild-with-delete-cascade)
- [ARRAY column](#array-column)
- [Self-referential relationship](#self-referential-relationship)
- [Registration in migrations/env.py](#registration-in-migrationsenvpy)

## Every column shape

```python
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum as SQLEnum, ForeignKey, Index,
    Integer, String, Text, UniqueConstraint, UUID as SQUID,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.infrastructure.models import BaseModel
from app.modules.{module}.domain.enums import {Module}Status

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class {Entity}Model(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_{plural_snake}"
    __table_args__ = (
        UniqueConstraint("name", name="uq_{plural_snake}_name"),
        Index("ix_{plural_snake}_status", "status"),
    )

    # STRING
    name: Mapped[str] = mapped_column(
        String(255),
        name="name",
        comment="Display name of the {entity}",
        nullable=False,
    )

    # NULLABLE UNBOUNDED TEXT
    description: Mapped[str | None] = mapped_column(
        Text,
        name="description",
        comment="Optional long-form description",
        nullable=True,
        default=None,
    )

    # INTEGER
    priority: Mapped[int] = mapped_column(
        Integer,
        name="priority",
        comment="Priority of the {entity}, from 1 to 10",
        nullable=False,
        server_default="5",
    )

    # BOOLEAN
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        name="is_pinned",
        comment="Whether this entry is pinned to the top",
        nullable=False,
        server_default="false",
    )

    # ENUM — never pass create_type; autogenerate emits the PG type.
    # PostgreSQL stores the uppercase member NAMES ("ACTIVE"), not the values.
    status: Mapped[{Module}Status] = mapped_column(
        SQLEnum({Module}Status, name="{module}_status_enum"),
        name="status",
        comment="Current status of the {entity}",
        nullable=False,
    )

    # NULLABLE TIMESTAMP
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="completed_at",
        comment="Timestamp of when the {entity} was completed",
        nullable=True,
        default=None,
    )

    # FOREIGN KEY
    user_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="CASCADE",
        ),
        name="user_id",
        comment="Identifier of the owning user",
        nullable=False,
    )

    # RELATIONSHIP — string target + TYPE_CHECKING import
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="{plural_snake}",
        lazy="noload",
    )
```

## Dual actor foreign keys

The most common shape in this project — `created_by` and `updated_by` both point at the user
table, so each relationship must declare `foreign_keys` or SQLAlchemy cannot disambiguate.
Reference: `KeyModel`.

```python
__table_args__ = (
    Index("ix_{plural_snake}_created_by", "created_by"),
    Index("ix_{plural_snake}_updated_by", "updated_by"),
)

created_by: Mapped[UUID] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(
        f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
        ondelete="RESTRICT",
    ),
    name="created_by",
    comment="Identifier of the user who created the {entity}",
    nullable=False,
)

updated_by: Mapped[UUID] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(
        f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
        ondelete="RESTRICT",
    ),
    name="updated_by",
    comment="Identifier of the user who last updated the {entity}",
    nullable=False,
)

creator: Mapped["UserModel"] = relationship(
    "UserModel",
    foreign_keys=[created_by],
    lazy="noload",
)

updater: Mapped["UserModel"] = relationship(
    "UserModel",
    foreign_keys=[updated_by],
    lazy="noload",
)
```

`ondelete="RESTRICT"` on actor references: an audited row must not lose its author. The
`creator` / `updater` relationships exist so the repository can `joinedload` them for responses
that project the actor — pair them with `model_entity_with_actors_mapper`.

## Reserved `metadata` JSONB column

`metadata` is reserved by SQLAlchemy Declarative. Rename the Python attribute, keep the database
column name. Reference: `NotificationModel.notification_metadata`.

```python
# '{module}_metadata' in Python, 'metadata' in the database
{module}_metadata: Mapped[dict | None] = mapped_column(
    JSONB,
    name="metadata",
    comment="Optional JSON payload with internal context data",
    nullable=True,
    default=None,
)
```

The mapper bridges both directions — see the `create-mapper` templates.

## Composite unique plus lookup index

A natural key gets the constraint and a matching index for lookups. Reference:
`AuthenticationModel` — one authentication per `(user_id, user_agent, device)` triple.

```python
__table_args__ = (
    UniqueConstraint(
        "user_id",
        "user_agent",
        "device",
        name="uq_authentications_user_id_user_agent_device",
    ),
    Index("ix_authentications_user_id_user_agent_device", "user_id", "user_agent", "device"),
)
```

For a single-column natural key the constraint alone is enough — Postgres backs a
`UniqueConstraint` with an index automatically. Reference: `uq_keys_hashed_key`.

## XOR-owner CheckConstraint

For a row owned by exactly one of two parents. Mirror the rule in the entity's `__post_init__`.

```python
__table_args__ = (
    CheckConstraint(
        "num_nonnulls(owner_a_id, owner_b_id) = 1",
        name="ck_{plural_snake}_single_owner",
    ),
    Index("ix_{plural_snake}_owner_a_id", "owner_a_id"),
    Index("ix_{plural_snake}_owner_b_id", "owner_b_id"),
)

owner_a_id: Mapped[UUID | None] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_{owner_a_plural}.id", ondelete="CASCADE"),
    name="owner_a_id",
    comment="First possible owner, when the {entity} belongs to it",
    nullable=True,
    default=None,
)

owner_b_id: Mapped[UUID | None] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_{owner_b_plural}.id", ondelete="CASCADE"),
    name="owner_b_id",
    comment="Second possible owner, when the {entity} belongs to it",
    nullable=True,
    default=None,
)
```

## Parent/child with delete cascade

Live 1:1 reference: `AuthenticationModel.refresh_token` → `RefreshTokenModel`. The parent declares
the cascade; the child FK carries `ondelete="CASCADE"`.

```python
# parent side — 1:1, so uselist=False
refresh_token: Mapped["RefreshTokenModel | None"] = relationship(
    back_populates="authentication",
    uselist=False,
    cascade="all, delete-orphan",
    passive_deletes=True,
    lazy="noload",
)

# child side
authentication_id: Mapped[UUID] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(
        f"{settings.APPLICATION_TABLE_PREFIX}_authentications.id",
        ondelete="CASCADE",
    ),
    name="authentication_id",
    comment="Authentication associated with this refresh token",
    nullable=False,
)

authentication: Mapped["AuthenticationModel"] = relationship(
    back_populates="refresh_token",
    uselist=False,
    lazy="noload",
)
```

For a 1:N collection the parent side becomes a list and drops `uselist`. A composite unique keeps
child ordering consistent when the child carries a `position`:

```python
# parent side — 1:N
children: Mapped[list["{Child}Model"]] = relationship(
    "{Child}Model",
    back_populates="{parent_snake}",
    cascade="all, delete-orphan",
    passive_deletes=True,
    lazy="noload",
)

# child side
__table_args__ = (
    UniqueConstraint(
        "{parent_snake}_id", "position",
        name="uq_{children_plural}_{parent_snake}_id_position",
    ),
    Index(
        "ix_{children_plural}_{parent_snake}_id_position",
        "{parent_snake}_id", "position",
    ),
)
```

## ARRAY column

```python
tags: Mapped[list[str]] = mapped_column(
    ARRAY(String(50)),
    name="tags",
    comment="Tags applied to this {entity}",
    nullable=False,
    server_default="{}",
)
```

## Self-referential relationship

```python
parent_id: Mapped[UUID | None] = mapped_column(
    SQUID(as_uuid=True),
    ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_{plural_snake}.id", ondelete="CASCADE"),
    name="parent_id",
    comment="Parent {entity} when this row is a child",
    nullable=True,
    default=None,
)

parent: Mapped["{Entity}Model | None"] = relationship(
    "{Entity}Model",
    remote_side=lambda: [{Entity}Model.id],
    back_populates="children",
    lazy="noload",
)

children: Mapped[list["{Entity}Model"]] = relationship(
    "{Entity}Model",
    back_populates="parent",
    lazy="noload",
)
```

## Registration in migrations/env.py

```python
from app.modules.{module}.infrastructure.models import {Entity}Model

_ = [
    ...,
    {Entity}Model,   # keep the list alphabetical
    ...,
]
```

Without this the table is invisible to autogenerate, and the next revision will emit a
`drop_table` for it.
