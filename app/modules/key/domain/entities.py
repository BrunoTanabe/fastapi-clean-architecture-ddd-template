from dataclasses import dataclass, field
from datetime import datetime

from app.modules.key.domain.enums import KeySortField
from app.modules.shared.domain.entities import (
    BaseEntity,
    DomainErrors,
    PaginatedList,
    Pagination,
)
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN, UNSET
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Key(BaseEntity):
    name: str = field(default=None, repr=True, compare=True)
    description: str | None = field(default=UNSET, repr=False, compare=False)

    # Non-secret identity of the key
    prefix: str = field(default=None, repr=True, compare=False)
    last_four: str = field(default=None, repr=False, compare=False)

    # Secret handling: the raw key is never persisted. 'plain_key' is transient
    # and only carries the freshly generated secret to the response once (mirrors
    # User.password vs User.hashed_password); 'hashed_key' is the HMAC-SHA256 that
    # gets stored.
    hashed_key: str = field(default=None, repr=False, compare=True)
    plain_key: str | None = field(default=None, repr=False, compare=False)

    # Lifecycle
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    last_used_at: datetime | None = field(default=None, repr=False, compare=False)

    # Actorship (both required; equal on creation)
    created_by: User = field(default=None, repr=False, compare=False)
    updated_by: User = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if self.name is not UNSET and self.name is not None:
            self.name = " ".join(self.name.strip().split())
            if self.name:
                self.name = self.name[0].upper() + self.name[1:]

            if len(self.name) < 3:
                errors.append("Key name must be at least 3 characters long.")
            elif len(self.name) > 255:
                errors.append("Key name must not exceed 255 characters.")
            elif not RESOURCE_NAME_PATTERN.match(self.name):
                errors.append(
                    "Key name must contain only letters, numbers, spaces, hyphens, and underscores."
                )

        if self.description is not UNSET and self.description is not None:
            self.description = " ".join(self.description.strip().split())
            if self.description:
                self.description = self.description[0].upper() + self.description[1:]
            else:
                self.description = None

        if errors:
            raise DomainErrors(errors)

    def deactivate(self, updated_by: User) -> None:  # noqa
        super().deactivate()
        self.updated_by = updated_by


@dataclass(kw_only=True, slots=True)
class KeyList(PaginatedList):
    items: list[Key] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class KeyPagination(Pagination):
    sort_by: KeySortField = field(
        default=KeySortField.CREATED_AT, repr=False, compare=False
    )
