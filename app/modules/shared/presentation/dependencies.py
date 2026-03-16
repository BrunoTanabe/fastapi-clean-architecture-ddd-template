from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.infrastructure.repositories import (
    PostgresSessionRepository,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.infrastructure.repositories import PostgresUserRepository


def get_authentication_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IAuthenticationRepository:
    return PostgresSessionRepository(session=session)


def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return PostgresUserRepository(session=session)


def get_shared_use_cases(
    user_repository: IUserRepository = Depends(get_user_repository),
) -> SharedUseCases:
    return SharedUseCases(user_repository=user_repository)
