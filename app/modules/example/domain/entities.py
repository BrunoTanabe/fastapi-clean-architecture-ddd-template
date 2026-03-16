from dataclasses import dataclass, field

from app.modules.example.domain.value_objects import FullName
from app.modules.shared.presentation.exceptions import DomainError


@dataclass(kw_only=True, slots=True)
class Example:
    full_name: FullName = field(init=True, compare=True, repr=True)

    def __post_init__(self):
        self._validate()

    def _validate(self) -> None:
        if not self.full_name:
            raise DomainError("Full name is required.")
        if self.full_name == "John Doe":
            raise DomainError("John Doe name is not allowed.")

    @property
    def message(self) -> str:
        return f"Hello, {self.full_name}!"
