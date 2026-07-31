from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_session
from app.core.database import get_async_session
from app.modules.key.application.interfaces import (
    IKeyCache,
    IKeyRepository,
    IKeyService,
)
from app.modules.key.application.use_cases import KeyUseCases
from app.modules.key.infrastructure.caches import RedisKeyCache
from app.modules.key.infrastructure.repositories import PostgresKeyRepository
from app.modules.key.infrastructure.services import KeyService


def get_key_cache(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> IKeyCache:
    return RedisKeyCache(cache=cache)


def get_key_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IKeyRepository:
    return PostgresKeyRepository(session=session)


def get_key_service() -> IKeyService:
    return KeyService()


def get_key_use_cases(
    cache: Annotated[IKeyCache, Depends(get_key_cache)],
    repository: Annotated[IKeyRepository, Depends(get_key_repository)],
    service: Annotated[IKeyService, Depends(get_key_service)],
) -> KeyUseCases:
    return KeyUseCases(cache=cache, repository=repository, service=service)
