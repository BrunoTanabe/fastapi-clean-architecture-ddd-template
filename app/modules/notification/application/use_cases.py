from loguru import logger

from app.modules.notification.application.exceptions import (
    NotificationException,
    NotificationNotFoundException,
)
from app.modules.notification.application.interfaces import INotificationRepository
from app.modules.notification.domain.entities import (
    Notification,
    NotificationList,
    NotificationPagination,
)
from app.modules.shared.application.exceptions import DomainException, StandardException
from app.modules.shared.domain.entities import DomainError


class NotificationUseCases:
    def __init__(self, repository: INotificationRepository) -> None:
        self.repository = repository

    # READ
    async def get_all(
        self,
        notification: Notification,
        pagination: NotificationPagination,
    ) -> NotificationList:
        try:
            logger.debug(
                f"Initializing get all notifications use case for user {notification.user.id}."
            )

            notification_list = await self.repository.get_all_by_user(
                notification, pagination
            )

            logger.debug(
                f"Get all notifications use case completed. Found {len(notification_list.items)} for user {notification.user.id}."
            )
            return notification_list
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get all notifications use case."
            )
            raise NotificationException()

    # UPDATE
    async def mark_as_read(self, notification: Notification) -> Notification:
        try:
            logger.debug(
                f"Initializing mark as read use case for notification {notification.id}."
            )

            existing = await self.repository.get_by_id(notification)
            if not existing:
                raise NotificationNotFoundException(str(notification.id))

            if existing.user.id != notification.user.id:
                raise NotificationNotFoundException(str(notification.id))

            existing.mark_as_read()
            updated = await self.repository.update(existing)

            logger.debug(
                f"Mark as read use case completed successfully for notification {notification.id}."
            )
            return updated
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the mark as read use case."
            )
            raise NotificationException()
