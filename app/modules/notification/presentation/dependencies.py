from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.notification.application.interfaces import INotificationRepository
from app.modules.notification.application.use_cases import NotificationUseCases
from app.modules.notification.infrastructure.repositories import (
    PostgresNotificationRepository,
)


def get_notification_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> INotificationRepository:
    return PostgresNotificationRepository(session=session)


def get_notification_use_cases(
    repository: Annotated[
        INotificationRepository, Depends(get_notification_repository)
    ],
) -> NotificationUseCases:
    return NotificationUseCases(repository=repository)
