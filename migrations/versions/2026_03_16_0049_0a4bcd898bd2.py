"""
Revision Message: insert_admin_user

Revision ID: 0a4bcd898bd2
Revises: f7ea2294d326
Create Date: 2026-03-16 00:49:32.072123

"""

from datetime import date
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

from app.core.security import password_hasher
from app.core.settings import settings


revision: str = "0a4bcd898bd2"
down_revision: Union[str, Sequence[str], None] = "f7ea2294d326"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    hashed_password = password_hasher.hash(settings.SECURITY_ADMIN_PASSWORD)

    conn.execute(
        sa.text(f"""
                    INSERT INTO {settings.APPLICATION_TABLE_PREFIX}_users 
                    (id, first_name, last_name, preferred_name, gender, birthdate, email, hashed_password, role, is_active, created_at, updated_at)
                    VALUES 
                    (:id, :first_name, :last_name, :preferred_name, :gender, :birthdate, :email, :hashed_password, :role, :is_active, now(), now())
                """),
        {
            "id": str(uuid4()),
            "first_name": "System",
            "last_name": "Administrator",
            "preferred_name": "Admin",
            "gender": "OTHER",
            "birthdate": date(1999, 12, 31),
            "email": settings.SECURITY_ADMIN_EMAIL,
            "hashed_password": hashed_password,
            "role": "ADMIN",
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
