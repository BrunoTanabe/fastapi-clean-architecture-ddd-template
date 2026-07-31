from dataclasses import dataclass, field
from datetime import date, datetime

from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import BaseEntity, DomainError, DomainErrors
from app.modules.shared.domain.enums import Role
from app.modules.shared.domain.value_objects import Email, Name, Phone
from app.modules.user.domain.enums import Gender


@dataclass(kw_only=True, slots=True)
class User(BaseEntity):
    name: Name = field(default=None, repr=True, compare=False)
    gender: Gender = field(default=None, repr=False, compare=False)
    birthdate: date = field(default=None, repr=True, compare=False)
    email: Email | str = field(default=None, repr=True, compare=True)
    phone: Phone | str = field(default=None, repr=False, compare=False)
    password: str = field(default=None, repr=False, compare=False)

    # Application generated fields
    hashed_password: str = field(default=None, repr=False, compare=False)
    role: Role = field(default=Role.USER, repr=False, compare=False)

    # Cached censored values (calculated once)
    _censored_email: str = field(init=False, default="", repr=False, compare=False)
    _censored_phone: str = field(init=False, default="", repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if isinstance(self.email, str):
            try:
                self.email = Email(email=self.email)
            except DomainError as e:
                errors.append(e.message)

        if isinstance(self.phone, str):
            try:
                self.phone = Phone(phone=self.phone)
            except DomainError as e:
                errors.append(e.message)

        self._calculate_censored_values()

        if self.birthdate is not None:
            today = datetime.now(BRASILIA_TZ).date()
            age = (
                today.year
                - self.birthdate.year
                - (
                    (today.month, today.day)
                    < (self.birthdate.month, self.birthdate.day)
                )
            )
            if age < 18:
                errors.append("Users must be at least 18 years old.")

        if errors:
            raise DomainErrors(errors)

    def _calculate_censored_values(self) -> None:
        self._censored_email = self._censor_email()
        self._censored_phone = self._censor_phone()

    def _censor_email(self) -> str:
        if not self.email:
            return ""

        email_str = str(self.email)
        if "@" not in email_str:
            return ""

        local_part, domain = email_str.split("@", 1)

        if len(local_part) <= 1:
            censored_local = "*" * len(local_part)
        else:
            censored_local = local_part[0] + "*" * (len(local_part) - 1)

        return f"{censored_local}@{domain}"

    def _censor_phone(self) -> str:
        if not self.phone:
            return ""

        phone_str = str(self.phone)
        digits = "".join(filter(str.isdigit, phone_str))

        if len(digits) < 4:
            return "*" * len(phone_str)

        visible_digits = digits[-4:]
        censored_part = "*" * (len(digits) - 4)

        result = []
        digit_index = 0

        for char in phone_str:
            if char.isdigit():
                if digit_index < len(censored_part):
                    result.append("*")
                else:
                    result.append(visible_digits[digit_index - len(censored_part)])
                digit_index += 1
            else:
                result.append(char)

        return "".join(result)

    @property
    def censored_email(self) -> str:
        return self._censored_email

    @property
    def censored_phone(self) -> str:
        return self._censored_phone
