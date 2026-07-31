from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.application.use_cases import UserUseCases
from app.modules.user.infrastructure.repositories import PostgresUserRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IUserRepository:
    return PostgresUserRepository(session=session)


def get_user_use_cases(
    repository: Annotated[IUserRepository, Depends(get_user_repository)],
) -> UserUseCases:
    return UserUseCases(repository=repository)
