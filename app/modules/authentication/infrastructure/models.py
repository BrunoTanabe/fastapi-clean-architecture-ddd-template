from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    String,
    Text,
    DateTime,
    func,
    UniqueConstraint,
    ForeignKey,
    UUID as SQUID,
    Index,
    Boolean,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.application.enums import Role
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.infrastructure.models import Base

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class SessionModel(Base):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_sessions"
    __mapper_args__ = {"eager_defaults": True}

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "user_agent",
            "device",
            name="uq_sessions_user_id_user_agent_device",
        ),
        Index(
            "ix_sessions_user_id_user_agent_device", "user_id", "user_agent", "device"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the session",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_users.id",
            ondelete="CASCADE",
        ),
        name="user_id",
        comment="Identifier of the user who owns the session",
        nullable=False,
    )

    ip_address: Mapped[str] = mapped_column(
        String(45),
        name="ip_address",
        comment="IP address used when the session was created",
        nullable=False,
    )

    device: Mapped[str] = mapped_column(
        String(255), name="device", comment="Human readable device name", nullable=False
    )

    user_agent: Mapped[str] = mapped_column(
        Text,
        name="user_agent",
        comment="User agent string of the client",
        nullable=False,
    )

    accept_language: Mapped[Optional[str]] = mapped_column(
        String(255),
        name="accept_language",
        comment="Accept-Language header value of the client",
        nullable=True,
        default=None,
    )

    accept_encoding: Mapped[Optional[str]] = mapped_column(
        String(255),
        name="accept-encoding",
        comment="Accept-Encoding header value of the client",
        nullable=True,
        default=None,
    )

    origin: Mapped[str] = mapped_column(
        String(255),
        name="origin",
        comment="Origin header value of the client",
        nullable=False,
    )

    referrer: Mapped[Optional[str]] = mapped_column(
        String(255),
        name="referrer",
        comment="Referrer header value of the client",
        nullable=False,
    )

    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        name="location",
        comment="Approximate geographic location of the client",
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the session was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="last_update_at",
        comment="Last time the session was updated",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    blacklisted: Mapped[bool] = mapped_column(
        Boolean,
        name="blacklisted",
        comment="Indicates whether the session is blacklisted",
        nullable=False,
        default=False,
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="sessions",
    )

    refresh_token: Mapped["RefreshTokenModel"] = relationship(
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RefreshTokenModel(Base):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_refresh_tokens"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            name="uq_refresh_tokens_session_id",
        ),
        Index(
            "ix_hashed_jti_revoked",
            "hashed_jti",
            "revoked",
        ),
    )
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the refresh token",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_sessions.id",
            ondelete="CASCADE",
        ),
        name="session_id",
        comment="Session associated with this refresh token",
        nullable=False,
    )

    hashed_jti: Mapped[str] = mapped_column(
        Text,
        name="hashed_jti",
        comment="Hashed JTI (JWT ID) value",
        nullable=False,
        unique=True,
    )

    previous_hashed_jti: Mapped[Optional[str]] = mapped_column(
        Text,
        name="previous_hashed_jti",
        comment="Hashed JTI (JWT ID) value of the previous refresh token",
        nullable=True,
        default=None,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the refresh token was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="updated_at",
        comment="Timestamp when the record was last updated",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        onupdate=func.now(),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the refresh token",
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        name="revoked",
        comment="Indicates whether the refresh token was revoked",
        nullable=False,
        default=False,
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        name="revoked_at",
        comment="Timestamp when the refresh token was revoked",
        nullable=True,
        default=None,
    )

    session: Mapped["SessionModel"] = relationship(
        back_populates="refresh_token",
        uselist=False,
    )

    access_token: Mapped["AccessTokenModel"] = relationship(
        back_populates="refresh_token",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AccessTokenModel(Base):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_access_tokens"
    __table_args__ = (
        UniqueConstraint(
            "refresh_id",
            name="uq_access_tokens_refresh_id",
        ),
        Index(
            "ix_hashed_jti_revoked",
            "hashed_jti",
            "revoked",
        ),
    )
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        name="id",
        comment="Unique identifier of the access token",
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    refresh_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            f"{settings.APPLICATION_TABLE_PREFIX}_refresh_tokens.id",
            ondelete="CASCADE",
        ),
        name="refresh_id",
        comment="Refresh token associated with this access token",
        nullable=False,
    )

    hashed_jti: Mapped[str] = mapped_column(
        Text,
        name="hashed_jti",
        comment="Hashed JTI (JWT ID) value",
        nullable=False,
        unique=True,
    )

    previous_hashed_jti: Mapped[Optional[str]] = mapped_column(
        Text,
        name="previous_hashed_jti",
        comment="Hashed JTI (JWT ID) value of the previous access token",
        nullable=True,
        default=None,
        unique=True,
    )

    permission: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role_enum"),
        name="permission",
        comment="Permission level associated with the access token",
        nullable=False,
        default=Role.USER,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="created_at",
        comment="Timestamp when the access token was created",
        default=lambda: datetime.now(BRASILIA_TZ),
        server_default=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        name="expires_at",
        comment="Expiration timestamp of the access token",
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        name="revoked",
        comment="Indicates whether the refresh token was revoked",
        nullable=False,
        default=False,
    )

    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        name="revoked_at",
        comment="Timestamp when the refresh token was revoked",
        nullable=True,
        default=None,
    )

    refresh_token: Mapped["RefreshTokenModel"] = relationship(
        back_populates="access_token",
        uselist=False,
    )
