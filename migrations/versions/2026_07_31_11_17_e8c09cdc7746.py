"""
Revision Message: insert_admin_user

Revision ID: e8c09cdc7746
Revises: 93b93ee0f291
Create Date: 2026-07-31 11:17:22.774107

"""

from collections.abc import Sequence
from datetime import date

import sqlalchemy as sa
from alembic import op

from app.core.security import hash_password
from app.core.settings import settings

revision: str = "e8c09cdc7746"
down_revision: str | Sequence[str] | None = "93b93ee0f291"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    users_table = f"{settings.APPLICATION_TABLE_PREFIX}_users"

    op.get_bind().execute(
        sa.text(
            f"""
            INSERT INTO {users_table}
                (first_name, last_name, preferred_name, gender, birthdate, email, hashed_password, role)
            VALUES
                (:first_name, :last_name, :preferred_name, :gender, :birthdate, :email, :hashed_password, :role)
            ON CONFLICT (email) DO NOTHING
            """
        ),
        {
            "first_name": "System",
            "last_name": "Admin",
            "preferred_name": "Admin",
            "gender": "OTHER",
            "birthdate": date(1990, 1, 1),
            "email": settings.SECURITY_ADMIN_EMAIL,
            "hashed_password": hash_password(settings.SECURITY_ADMIN_PASSWORD),
            "role": "ADMIN",
        },
    )


def downgrade() -> None:
    users_table = f"{settings.APPLICATION_TABLE_PREFIX}_users"

    op.get_bind().execute(
        sa.text(f"DELETE FROM {users_table} WHERE email = :email"),
        {"email": settings.SECURITY_ADMIN_EMAIL},
    )
