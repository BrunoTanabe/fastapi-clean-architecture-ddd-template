from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.presentation.dependencies import get_shared_use_cases
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.application.use_cases import UserUseCases
from app.modules.user.infrastructure.repositories import PostgresUserRepository


def get_user_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IUserRepository:
    return PostgresUserRepository(session=session)


def get_user_use_cases(
    repository: IUserRepository = Depends(get_user_repository),
    shared_service: SharedUseCases = Depends(get_shared_use_cases),
) -> UserUseCases:
    return UserUseCases(repository=repository, shared_service=shared_service)
