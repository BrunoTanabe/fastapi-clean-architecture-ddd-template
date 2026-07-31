from typing import Protocol

from app.modules.notification.domain.entities import (
    Notification,
    NotificationList,
    NotificationPagination,
)


class INotificationRepository(Protocol):
    # CREATE
    async def create(self, notification: Notification) -> Notification: ...

    async def create_broadcast(
        self, notification: Notification
    ) -> list[Notification]: ...

    # READ
    async def get_by_id(self, notification: Notification) -> Notification | None: ...

    async def get_all_by_user(
        self,
        notification: Notification,
        pagination: NotificationPagination,
    ) -> NotificationList: ...

    # UPDATE
    async def update(self, notification: Notification) -> Notification: ...
