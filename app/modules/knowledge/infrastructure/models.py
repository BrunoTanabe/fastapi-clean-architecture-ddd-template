from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UUID as SQUID
from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.infrastructure.models import BaseModel

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class KnowledgeModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_knowledges"
    __table_args__ = (
        Index("ix_knowledges_name_is_active", "name", "is_active"),
        Index("ix_knowledges_created_by", "created_by"),
        Index("ix_knowledges_updated_by", "updated_by"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        name="name",
        comment="Unique name of the knowledge record",
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        name="description",
        comment="Detailed description of the knowledge record",
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
        comment="Identifier of the user who created the record",
        nullable=False,
    )

    updated_by: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="RESTRICT",
        ),
        name="updated_by",
        comment="Identifier of the user who last updated the record",
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
