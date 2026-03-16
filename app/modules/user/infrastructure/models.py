from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Enum as SQLEnum, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.application.enums import Role
from app.modules.shared.infrastructure.models import BaseModel
from app.modules.user.application.enums import Gender
from app.modules.user.domain.value_objects import Phone, Email

if TYPE_CHECKING:
    from app.modules.authentication.infrastructure.models import SessionModel


class UserModel(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_users"
    __table_args__ = (
        UniqueConstraint("email", "is_active", name="uq_users_email_is_active"),
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        name="first_name",
        comment="First name of the user",
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        name="last_name",
        comment="Last name of the user",
        nullable=False,
    )

    preferred_name: Mapped[str] = mapped_column(
        String(100),
        name="preferred_name",
        comment="Preferred name of the user",
        nullable=False,
    )

    gender: Mapped[Gender] = mapped_column(
        SQLEnum(Gender, name="gender_enum"),
        name="gender",
        comment="Gender of the user",
        nullable=False,
    )

    birthdate: Mapped[date] = mapped_column(
        Date,
        name="birthdate",
        comment="Birthdate of the user",
        nullable=False,
    )

    email: Mapped[Email] = mapped_column(
        String(255),
        name="email",
        comment="Email address of the user",
        nullable=False,
    )

    phone: Mapped[Optional[Phone]] = mapped_column(
        String(18),
        name="phone",
        comment="Phone number of the user",
        nullable=True,
        default=None,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        name="hashed_password",
        comment="Hashed password of the user",
        nullable=False,
    )

    role: Mapped[Role] = mapped_column(
        SQLEnum(Role, name="role_enum"),
        name="role",
        comment="Role of the user",
        nullable=False,
        default=Role.USER,
    )

    sessions: Mapped[list["SessionModel"]] = relationship(
        "SessionModel",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
