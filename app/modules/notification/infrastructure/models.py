from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    UUID as SQUID,
)
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.notification.domain.enums import NotificationType
from app.modules.shared.infrastructure.models import BaseModel

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class NotificationModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_notifications"
    __table_args__ = (
        Index("ix_notifications_user_id_is_active", "user_id", "is_active"),
        Index("ix_notifications_user_id_is_read", "user_id", "is_read"),
    )

    user_id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="CASCADE",
        ),
        name="user_id",
        comment="Identifier of the user who receives this notification",
        nullable=False,
    )

    notification_type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType, name="notification_type_enum"),
        name="notification_type",
        comment="Event type that triggered this notification",
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(150),
        name="title",
        comment="Short title of the notification",
        nullable=False,
    )

    body: Mapped[str] = mapped_column(
        Text,
        name="body",
        comment="Full body text of the notification",
        nullable=False,
    )

    redirect_url: Mapped[str | None] = mapped_column(
        String(2048),
        name="redirect_url",
        comment="Optional URL for deep linking from the notification",
        nullable=True,
        default=None,
    )

    notification_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        name="metadata",
        comment="Optional JSON payload with internal context data (resource_id, etc.)",
        nullable=True,
        default=None,
    )

    originated_from_broadcast: Mapped[str | None] = mapped_column(
        String(20),
        name="originated_from_broadcast",
        comment="Role targeted by the fan-out broadcast that created this notification, if any",
        nullable=True,
        default=None,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        name="is_read",
        comment="Whether the user has read this notification",
        nullable=False,
        default=False,
        server_default="false",
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        name="read_at",
        comment="Timestamp when the notification was marked as read",
        nullable=True,
        default=None,
    )

    recipient: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[user_id],
        lazy="noload",
    )
