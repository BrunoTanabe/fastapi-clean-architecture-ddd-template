from app.modules.shared.domain.entities import DomainError


class RedirectUrl:
    def __init__(self, value: str) -> None:
        self.value = value
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.value = self.value.strip()

    def _validate(self) -> None:
        if not self.value:
            raise DomainError("Redirect URL must not be empty.")
        if not (self.value.startswith("http://") or self.value.startswith("https://")):
            raise DomainError("Redirect URL must start with http:// or https://.")
        if len(self.value) > 2048:
            raise DomainError("Redirect URL must not exceed 2048 characters.")

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)
