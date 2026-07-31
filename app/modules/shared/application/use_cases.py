from loguru import logger

from app.modules.notification.application.exceptions import NotificationException
from app.modules.notification.application.interfaces import INotificationRepository
from app.modules.notification.domain.entities import Notification
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import (
    UserEmailNotFoundException,
    UserException,
    UserIdNotFoundException,
)
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.domain.entities import User
from app.modules.websocket.application.interfaces import IConnectionManagerService
from app.modules.websocket.domain.entities import WebSocketMessage


class SharedUseCases:
    def __init__(
        self,
        user_repository: IUserRepository,
        notification_repository: INotificationRepository,
        connection_manager: IConnectionManagerService,
    ) -> None:
        self.user_repository = user_repository
        self.notification_repository = notification_repository
        self.connection_manager = connection_manager
        self._raise_exceptions = True

    @property
    def raise_exceptions(self) -> bool:
        return self._raise_exceptions

    def enable_exceptions(self) -> None:
        self._raise_exceptions = True

    def disable_exceptions(self) -> None:
        self._raise_exceptions = False

    # NOTIFICATION
    async def create_notification(self, notification: Notification) -> Notification:
        try:
            logger.debug(
                f"Initializing create notification use case for user {notification.user.id}."
            )

            result = await self.notification_repository.create(notification)
            await self._dispatch_user_notification_message(result)

            logger.debug(
                f"Create notification use case completed successfully for user {notification.user.id}."
            )
            return result
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create notification use case."
            )
            raise NotificationException()

    async def create_broadcast_notification(
        self, notification: Notification
    ) -> list[Notification]:
        try:
            logger.debug(
                f"Initializing create broadcast notification use case "
                f"targeting role '{notification.originated_from_broadcast}'."
            )

            result = await self.notification_repository.create_broadcast(notification)
            if result:
                await self._dispatch_broadcast_notification_message(result[0])

            logger.debug(
                f"Broadcast notification use case completed. Created {len(result)} notification(s)."
            )
            return result
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create broadcast notification use case."
            )
            raise NotificationException()

    async def _dispatch_user_notification_message(
        self, notification: Notification
    ) -> None:
        try:
            ws_message = WebSocketMessage(
                user_id=notification.user.id,
                body=notification,
            )
            await self.connection_manager.send_to_user(ws_message)
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to dispatch user WebSocket notification message "
                f"for user '{notification.user.id}'; continuing best-effort."
            )

    async def _dispatch_broadcast_notification_message(
        self, notification: Notification
    ) -> None:
        try:
            ws_message = WebSocketMessage(body=notification)
            await self.connection_manager.broadcast_to(
                ws_message,
                minimum_role=notification.originated_from_broadcast,
            )
        except Exception as e:
            logger.opt(exception=e).warning(
                f"Failed to dispatch broadcast WebSocket notification message "
                f"targeting role '{notification.originated_from_broadcast}'; "
                f"continuing best-effort."
            )

    # USER
    async def get_user_by_id(self, user: User) -> User | None:
        try:
            logger.debug(
                f"Initializing get user by identifier use case for user: {user.id}."
            )

            db_user: User | None = await self.user_repository.get_by_id(user)

            if db_user is None and self._raise_exceptions:
                logger.info(
                    f"User with identifier {user.id} not found. Raising exception."
                )
                raise UserIdNotFoundException(str(user.id))

            logger.debug(f"User with identifier {user.id} retrieved successfully.")
            return db_user
        except StandardException:
            if self._raise_exceptions:
                raise
            return None
        except DomainError as e:
            if self._raise_exceptions:
                raise DomainException(e)
            return None
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get user by identifier use case."
            )
            if self._raise_exceptions:
                raise UserException()
            return None

    async def get_user_by_email(self, user: User) -> User | None:
        try:
            logger.debug(
                f"Initializing get user by email for user {user.censored_email}."
            )

            db_user: User | None = await self.user_repository.get_by_email(user)

            if db_user is None and self._raise_exceptions:
                logger.info(
                    f"User with email {user.email} not found. Raising exception."
                )
                raise UserEmailNotFoundException(email=str(user.email))

            logger.debug(f"User {user.email} retrieved from database successfully.")
            return db_user
        except StandardException:
            if self._raise_exceptions:
                raise
            return None
        except DomainError as e:
            if self._raise_exceptions:
                raise DomainException(e)
            return None
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get user by email use case."
            )
            if self._raise_exceptions:
                raise UserException()
            return None
