from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Union
from uuid import UUID

from app.modules.shared.application.enums import Role
from app.modules.shared.presentation.exceptions import DomainError
from app.modules.user.application.enums import Gender
from app.modules.user.domain.value_objects import Name, Email, Phone


@dataclass(kw_only=True, slots=True)
class User:
    name: Name = field(default=None, repr=True, compare=False)
    gender: Gender = field(default=None, repr=False, compare=False)
    birthdate: date = field(default=None, repr=True, compare=False)
    email: Union[Email, str] = field(default=None, repr=True, compare=True)
    phone: Union[Phone, str] = field(default=None, repr=False, compare=False)
    password: str = field(default=None, repr=False, compare=False)

    # Application generated fields
    id: UUID = field(default=None, repr=True, compare=True)
    created_at: datetime = field(default=None, repr=False, compare=True)
    updated_at: datetime = field(default=None, repr=False, compare=False)
    is_active: bool = field(init=False, default=True, repr=False, compare=False)
    hashed_password: str = field(default=None, repr=False, compare=False)
    role: Role = field(default=Role.USER, repr=False, compare=False)

    def __post_init__(self):
        self._normalize()
        self._validate()

    def _normalize(self):
        if isinstance(self.email, str):
            self.email = Email(email=self.email)
        if isinstance(self.phone, str):
            self.phone = Phone(phone=self.phone)

    def _validate(self) -> None:
        if self.birthdate is None:
            return

        today = date.today()
        age = (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )
        if age < 18:
            raise DomainError("Users must be at least 18 years old.")
