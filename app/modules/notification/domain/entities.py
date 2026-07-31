from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.notification.domain.enums import (
    NotificationSortField,
    NotificationType,
)
from app.modules.notification.domain.value_objects import RedirectUrl
from app.modules.shared.domain.entities import (
    BaseEntity,
    DomainError,
    DomainErrors,
    PaginatedList,
    Pagination,
)
from app.modules.shared.domain.enums import Role
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Notification(BaseEntity):
    # Business fields
    user: User = field(default=None, repr=True, compare=True)
    notification_type: NotificationType = field(default=None, repr=True, compare=False)
    title: str = field(default=None, repr=True, compare=False)
    body: str = field(default=None, repr=False, compare=False)
    redirect_url: RedirectUrl | str | None = field(
        default=None, repr=False, compare=False
    )
    metadata: dict | None = field(default=None, repr=False, compare=False)

    # Tracks the broadcast role that originated this notification (fan-out context)
    originated_from_broadcast: Role | None = field(
        default=None, repr=False, compare=False
    )

    # Read tracking (always per-user since every notification is personal)
    is_read: bool = field(default=False, repr=False, compare=False)
    read_at: datetime | None = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if not self.originated_from_broadcast and (not self.user or not self.user.id):
            errors.append("Notification must have a target user.")

        if self.title is not None:
            if len(self.title) < 3:
                errors.append("Title must be at least 3 characters long.")
            elif len(self.title) > 150:
                errors.append("Title must not exceed 150 characters.")

        if self.body is not None:
            if len(self.body) < 1:
                errors.append("Body must not be empty.")
            elif len(self.body) > 1000:
                errors.append("Body must not exceed 1000 characters.")

        if isinstance(self.redirect_url, str):
            try:
                self.redirect_url = RedirectUrl(value=self.redirect_url)
            except DomainError as e:
                errors.append(e.message)

        if errors:
            raise DomainErrors(errors)

    def mark_as_read(self) -> None:
        self.is_read = True
        self.read_at = datetime.now(tz=ZoneInfo("America/Sao_Paulo"))


@dataclass(kw_only=True, slots=True)
class NotificationList(PaginatedList):
    items: list[Notification] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class NotificationPagination(Pagination):
    sort_by: NotificationSortField = field(
        default=NotificationSortField.CREATED_AT, repr=False, compare=False
    )
