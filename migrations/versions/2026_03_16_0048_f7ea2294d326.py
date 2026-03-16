"""
Revision Message: initial_schemas

Revision ID: f7ea2294d326
Revises:
Create Date: 2026-03-16 00:48:00.248313

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7ea2294d326"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fastapi_clean_architecture_ddd_template_users",
        sa.Column(
            "first_name",
            sa.String(length=100),
            nullable=False,
            comment="First name of the user",
        ),
        sa.Column(
            "last_name",
            sa.String(length=100),
            nullable=False,
            comment="Last name of the user",
        ),
        sa.Column(
            "preferred_name",
            sa.String(length=100),
            nullable=False,
            comment="Preferred name of the user",
        ),
        sa.Column(
            "gender",
            sa.Enum("MALE", "FEMALE", "NON_BINARY", "OTHER", name="gender_enum"),
            nullable=False,
            comment="Gender of the user",
        ),
        sa.Column(
            "birthdate", sa.Date(), nullable=False, comment="Birthdate of the user"
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            comment="Email address of the user",
        ),
        sa.Column(
            "phone",
            sa.String(length=18),
            nullable=True,
            comment="Phone number of the user",
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
            comment="Hashed password of the user",
        ),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "MANAGER", "USER", name="role_enum"),
            nullable=False,
            comment="Role of the user",
        ),
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Unique identifier of the record",
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the record was created",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the record was last updated",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", "is_active", name="uq_users_email_is_active"),
    )
    op.create_table(
        "fastapi_clean_architecture_ddd_template_sessions",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Unique identifier of the session",
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
            comment="Identifier of the user who owns the session",
        ),
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=False,
            comment="IP address used when the session was created",
        ),
        sa.Column(
            "device",
            sa.String(length=255),
            nullable=False,
            comment="Human readable device name",
        ),
        sa.Column(
            "user_agent",
            sa.Text(),
            nullable=False,
            comment="User agent string of the client",
        ),
        sa.Column(
            "accept_language",
            sa.String(length=255),
            nullable=True,
            comment="Accept-Language header value of the client",
        ),
        sa.Column(
            "accept-encoding",
            sa.String(length=255),
            nullable=True,
            comment="Accept-Encoding header value of the client",
        ),
        sa.Column(
            "origin",
            sa.String(length=255),
            nullable=False,
            comment="Origin header value of the client",
        ),
        sa.Column(
            "referrer",
            sa.String(length=255),
            nullable=False,
            comment="Referrer header value of the client",
        ),
        sa.Column(
            "location",
            sa.String(length=255),
            nullable=True,
            comment="Approximate geographic location of the client",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the session was created",
        ),
        sa.Column(
            "last_update_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last time the session was updated",
        ),
        sa.Column(
            "blacklisted",
            sa.Boolean(),
            nullable=False,
            comment="Indicates whether the session is blacklisted",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["fastapi_clean_architecture_ddd_template_users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "user_agent",
            "device",
            name="uq_sessions_user_id_user_agent_device",
        ),
    )
    op.create_index(
        "ix_sessions_user_id_user_agent_device",
        "fastapi_clean_architecture_ddd_template_sessions",
        ["user_id", "user_agent", "device"],
        unique=False,
    )
    op.create_table(
        "fastapi_clean_architecture_ddd_template_refresh_tokens",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Unique identifier of the refresh token",
        ),
        sa.Column(
            "session_id",
            sa.UUID(),
            nullable=False,
            comment="Session associated with this refresh token",
        ),
        sa.Column(
            "hashed_jti", sa.Text(), nullable=False, comment="Hashed JTI (JWT ID) value"
        ),
        sa.Column(
            "previous_hashed_jti",
            sa.Text(),
            nullable=True,
            comment="Hashed JTI (JWT ID) value of the previous refresh token",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the refresh token was created",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the record was last updated",
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Expiration timestamp of the refresh token",
        ),
        sa.Column(
            "revoked",
            sa.Boolean(),
            nullable=False,
            comment="Indicates whether the refresh token was revoked",
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when the refresh token was revoked",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["fastapi_clean_architecture_ddd_template_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", name="uq_refresh_tokens_session_id"),
    )
    op.create_table(
        "fastapi_clean_architecture_ddd_template_access_tokens",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Unique identifier of the access token",
        ),
        sa.Column(
            "refresh_id",
            sa.UUID(),
            nullable=False,
            comment="Refresh token associated with this access token",
        ),
        sa.Column(
            "hashed_jti", sa.Text(), nullable=False, comment="Hashed JTI (JWT ID) value"
        ),
        sa.Column(
            "previous_hashed_jti",
            sa.Text(),
            nullable=True,
            comment="Hashed JTI (JWT ID) value of the previous access token",
        ),
        sa.Column(
            "permission",
            sa.Enum("ADMIN", "MANAGER", "USER", name="role_enum"),
            nullable=False,
            comment="Permission level associated with the access token",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Timestamp when the access token was created",
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Expiration timestamp of the access token",
        ),
        sa.Column(
            "revoked",
            sa.Boolean(),
            nullable=False,
            comment="Indicates whether the refresh token was revoked",
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when the refresh token was revoked",
        ),
        sa.ForeignKeyConstraint(
            ["refresh_id"],
            ["fastapi_clean_architecture_ddd_template_refresh_tokens.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hashed_jti"),
        sa.UniqueConstraint("previous_hashed_jti"),
        sa.UniqueConstraint("refresh_id", name="uq_access_tokens_refresh_id"),
    )
    op.create_index(
        "ix_hashed_jti",
        "fastapi_clean_architecture_ddd_template_access_tokens",
        ["hashed_jti"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_hashed_jti",
        table_name="fastapi_clean_architecture_ddd_template_access_tokens",
    )
    op.drop_table("fastapi_clean_architecture_ddd_template_access_tokens")
    op.drop_table("fastapi_clean_architecture_ddd_template_refresh_tokens")
    op.drop_index(
        "ix_sessions_user_id_user_agent_device",
        table_name="fastapi_clean_architecture_ddd_template_sessions",
    )
    op.drop_table("fastapi_clean_architecture_ddd_template_sessions")
    op.drop_table("fastapi_clean_architecture_ddd_template_users")
