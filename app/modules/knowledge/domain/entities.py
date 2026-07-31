from dataclasses import dataclass, field

from app.modules.knowledge.domain.enums import KnowledgeSortField
from app.modules.shared.domain.entities import (
    BaseEntity,
    DomainErrors,
    PaginatedList,
    Pagination,
)
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN, UNSET
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Knowledge(BaseEntity):
    name: str = field(default=None, repr=True, compare=True)
    description: str | None = field(default=UNSET, repr=False, compare=False)
    created_by: User = field(default=None, repr=False, compare=False)
    updated_by: User = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if self.name is not UNSET and self.name is not None:
            self.name = " ".join(self.name.strip().split())
            if self.name:
                self.name = self.name[0].upper() + self.name[1:]

            if len(self.name) < 3:
                errors.append("Knowledge base name must be at least 3 characters long.")
            elif len(self.name) > 255:
                errors.append("Knowledge base name must not exceed 255 characters.")
            elif not RESOURCE_NAME_PATTERN.match(self.name):
                errors.append(
                    "Knowledge base name must contain only letters, numbers, spaces, hyphens, and underscores."
                )

        if self.description is not UNSET and self.description is not None:
            self.description = " ".join(self.description.strip().split())
            if self.description:
                self.description = self.description[0].upper() + self.description[1:]
            else:
                self.description = None

        if errors:
            raise DomainErrors(errors)

    def deactivate(self, updated_by: User) -> None:
        super().deactivate()
        self.updated_by = updated_by


@dataclass(kw_only=True, slots=True)
class KnowledgeList(PaginatedList):
    items: list[Knowledge] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class KnowledgePagination(Pagination):
    sort_by: KnowledgeSortField = field(
        default=KnowledgeSortField.UPDATED_AT, repr=False, compare=False
    )
