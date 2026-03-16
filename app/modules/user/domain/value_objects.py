import re

from app.core.settings import settings
from app.modules.shared.presentation.exceptions import DomainError


class Name:
    first_name: str
    last_name: str
    preferred_name: str = None

    def __init__(
        self, first_name: str, last_name: str, preferred_name: str = None
    ) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.preferred_name = preferred_name
        self._normalize()
        self._validate()

    def _validate(self) -> None:
        if not self.first_name or not self.last_name:
            raise DomainError("First name and last name are required.")
        if not self.first_name or not self.last_name:
            raise DomainError("First name and last name are required.")
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", self.first_name):
            raise DomainError(
                "First name must contain only letters, spaces, apostrophes, and hyphens."
            )
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", self.last_name):
            raise DomainError(
                "Last name must contain only letters, spaces, apostrophes, and hyphens."
            )
        if len(self.first_name.strip()) < 3:
            raise DomainError("First name must be at least 3 characters long.")
        if len(self.last_name.strip()) < 3:
            raise DomainError("Last name must be at least 3 characters long.")
        if len(self.first_name.strip()) > 100:
            raise DomainError("First name must not exceed 100 characters.")
        if len(self.last_name.strip()) > 100:
            raise DomainError("Last name must not exceed 100 characters.")

    def _normalize(self) -> None:
        self.first_name = self.first_name.strip().capitalize()
        self.last_name = self.last_name.strip().capitalize()
        if not self.preferred_name:
            self.preferred_name = self.first_name
        else:
            self.preferred_name = self.preferred_name.strip().capitalize()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.preferred_name})"

    def __eq__(self, other):
        return str(self) == str(other)


class Email:
    email: str

    _EMAIL_REGEX = re.compile(
        r"^(?=[a-zA-Z0-9._%+\-]{1,64}@)"
        r"[a-zA-Z0-9._%+\-]+"
        r"(?<!\.)@"
        r"(?=[a-zA-Z0-9\-\.]{1,253}$)"
        r"(?:[a-zA-Z0-9\-]+"
        r"(?:\.[a-zA-Z0-9\-]+)*)"
        r"\.[a-zA-Z]{2,}$"
    )

    def __init__(self, email: str) -> None:
        self.email = email
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.email = self.email.lower().strip()

    def _validate(self) -> None:
        if not self.email:
            raise DomainError("Email is required.")

        if len(self.email) > 254:
            raise DomainError("Email must not exceed 254 characters.")

        if not self._EMAIL_REGEX.match(self.email):
            raise DomainError(f"Invalid email format: '{self.email}'.")

        local, domain = self.email.rsplit("@", 1)

        if local.startswith(".") or local.endswith("."):
            raise DomainError("Email local part must not start or end with a dot.")

        if ".." in local:
            raise DomainError("Email local part must not contain consecutive dots.")

        if ".." in domain:
            raise DomainError("Email domain must not contain consecutive dots.")

        if (
            settings.SECURITY_EMAIL_ALLOWED_DOMAINS
            and domain not in settings.SECURITY_EMAIL_ALLOWED_DOMAINS
        ):
            raise DomainError(f"Email domain '{domain}' is not allowed.")

    def __str__(self) -> str:
        return self.email

    def __eq__(self, other) -> bool:
        return str(self) == str(other)


class Phone:
    phone: str

    def __init__(self, phone: str) -> None:
        self.phone = phone
        self._normalize()
        self._validate()

    def _normalize(self):
        cleaned = re.sub(r"[\s\-()\[\]]", "", self.phone.strip())
        if not cleaned.startswith("+"):
            cleaned = "+" + cleaned

        self.phone = cleaned

    def _validate(self) -> None:
        if not self.phone:
            raise DomainError("Phone is required.")

        digits = self.phone[1:]

        if not digits.isdigit():
            raise DomainError(
                "Phone number must contain only digits (optionally preceded by '+')."
            )

        if not (7 <= len(digits) <= 15):
            raise DomainError("Phone number must contain between 7 and 15 digits.")

    def __str__(self) -> str:
        return self.phone

    def __eq__(self, other) -> bool:
        return str(self) == str(other)
