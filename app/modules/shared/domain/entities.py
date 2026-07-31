from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.shared.domain.enums import SortOrder


# DOMAIN EXCEPTIONS
class DomainError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DomainErrors(DomainError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__(
            message=errors[0] if errors else "Domain validation errors occurred."
        )
        self.errors = errors


@dataclass(kw_only=True, slots=True)
class BaseEntity:
    id: UUID = field(default=None, repr=True, compare=True)
    is_active: bool = field(init=False, default=True, repr=False, compare=False)
    created_at: datetime = field(default=None, repr=False, compare=False)
    updated_at: datetime = field(default=None, repr=False, compare=False)

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(kw_only=True, slots=True)
class Pagination:
    page: int = field(default=1, repr=True, compare=True)
    per_page: int = field(default=20, repr=True, compare=True)
    sort_order: SortOrder = field(default=SortOrder.DESC, repr=False, compare=False)
    offset: int = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if self.page < 1:
            errors.append("Page must be at least 1.")
        if self.per_page < 1:
            errors.append("Per page must be at least 1.")
        elif self.per_page > 100:
            errors.append("Per page must not exceed 100.")

        if errors:
            raise DomainErrors(errors)

        self.offset = (self.page - 1) * self.per_page


@dataclass(kw_only=True, slots=True)
class PaginatedList:
    total: int = field(default=0, repr=True, compare=False)

    def __post_init__(self):
        if self.total < 0:
            raise DomainErrors(["Total must be zero or greater."])
