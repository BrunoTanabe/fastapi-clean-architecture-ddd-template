from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_session
from app.core.database import get_async_session
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
)
from app.modules.authentication.infrastructure.caches import RedisAuthenticationCache
from app.modules.authentication.infrastructure.repositories import (
    PostgresAuthenticationRepository,
)
from app.modules.key.application.interfaces import IKeyCache, IKeyRepository
from app.modules.key.infrastructure.caches import RedisKeyCache
from app.modules.key.infrastructure.repositories import PostgresKeyRepository
from app.modules.notification.application.interfaces import INotificationRepository
from app.modules.notification.infrastructure.repositories import (
    PostgresNotificationRepository,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.infrastructure.repositories import PostgresUserRepository
from app.modules.websocket.application.interfaces import IConnectionManagerService
from app.modules.websocket.presentation.dependencies import get_connection_manager


def get_authentication_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IAuthenticationRepository:
    return PostgresAuthenticationRepository(session=session)


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IUserRepository:
    return PostgresUserRepository(session=session)


def get_notification_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> INotificationRepository:
    return PostgresNotificationRepository(session=session)


def get_key_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IKeyRepository:
    return PostgresKeyRepository(session=session)


def get_authentication_cache(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> IAuthenticationCache:
    return RedisAuthenticationCache(cache=cache)


def get_key_cache(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> IKeyCache:
    return RedisKeyCache(cache=cache)


def get_shared_use_cases(
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    notification_repository: Annotated[
        INotificationRepository, Depends(get_notification_repository)
    ],
    connection_manager: Annotated[
        IConnectionManagerService, Depends(get_connection_manager)
    ],
) -> SharedUseCases:
    return SharedUseCases(
        user_repository=user_repository,
        notification_repository=notification_repository,
        connection_manager=connection_manager,
    )
