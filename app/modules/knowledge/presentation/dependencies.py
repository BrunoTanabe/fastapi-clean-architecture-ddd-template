from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_session
from app.core.database import get_async_session
from app.modules.knowledge.infrastructure.caches import RedisKnowledgeCache
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.presentation.dependencies import get_shared_use_cases
from app.modules.knowledge.application.interfaces import (
    IKnowledgeRepository,
    IKnowledgeCache,
)
from app.modules.knowledge.application.use_cases import KnowledgeUseCases
from app.modules.knowledge.infrastructure.repositories import (
    PostgresKnowledgeRepository,
)


def get_knowledge_cache(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> IKnowledgeCache:
    return RedisKnowledgeCache(cache=cache)


def get_knowledge_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> IKnowledgeRepository:
    return PostgresKnowledgeRepository(session=session)


def get_knowledge_use_cases(
    cache: Annotated[IKnowledgeCache, Depends(get_knowledge_cache)],
    repository: Annotated[IKnowledgeRepository, Depends(get_knowledge_repository)],
    shared_service: Annotated[SharedUseCases, Depends(get_shared_use_cases)],
) -> KnowledgeUseCases:
    return KnowledgeUseCases(
        cache=cache, repository=repository, shared_service=shared_service
    )
