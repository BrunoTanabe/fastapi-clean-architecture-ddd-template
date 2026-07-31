from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    UUID as SQUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.infrastructure.models import BaseModel

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class KeyModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_keys"
    __table_args__ = (
        UniqueConstraint("hashed_key", name="uq_keys_hashed_key"),
        Index("ix_keys_prefix", "prefix"),
        Index("ix_keys_created_by", "created_by"),
        Index("ix_keys_updated_by", "updated_by"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        name="name",
        comment="Human-readable name of the API key",
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        name="description",
        comment="Optional description of the API key",
        nullable=True,
        default=None,
    )

    prefix: Mapped[str] = mapped_column(
        String(32),
        name="prefix",
        comment="Public, non-secret identifier fragment of the key",
        nullable=False,
    )

    last_four: Mapped[str] = mapped_column(
        String(4),
        name="last_four",
        comment="Last four characters of the raw key, for masked display",
        nullable=False,
    )

    hashed_key: Mapped[str] = mapped_column(
        String(255),
        name="hashed_key",
        comment="HMAC-SHA256 hash of the raw key; the raw key is never stored",
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the key; null means it never expires",
        nullable=True,
        default=None,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="last_used_at",
        comment="Timestamp of the last time the key was used to authenticate",
        nullable=True,
        default=None,
    )

    created_by: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="RESTRICT",
        ),
        name="created_by",
        comment="Identifier of the user who created the key",
        nullable=False,
    )

    updated_by: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="RESTRICT",
        ),
        name="updated_by",
        comment="Identifier of the user who last updated the key",
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
