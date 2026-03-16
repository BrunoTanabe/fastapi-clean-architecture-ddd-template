from app.modules.shared.presentation.exceptions import DomainError


class FullName:
    first_name: str
    last_name: str

    def __init__(self, first_name: str, last_name: str) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self._validate()
        self.first_name = self.first_name.capitalize().strip()
        self.last_name = self.last_name.capitalize().strip()

    def _validate(self) -> None:
        if not self.first_name or not self.last_name:
            raise DomainError("First name and last name are required.")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __eq__(self, other):
        return str(self) == str(other)
