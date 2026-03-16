from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.health.application.interfaces import IHealthRepository
from app.modules.health.application.use_cases import HealthUseCases
from app.modules.health.infrastructure.repositories import PostgresHealthRepository


def get_health_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IHealthRepository:
    return PostgresHealthRepository(session=session)


def get_health_use_cases(
    repository: IHealthRepository = Depends(get_health_repository),
) -> HealthUseCases:
    return HealthUseCases(
        repository=repository,
    )
