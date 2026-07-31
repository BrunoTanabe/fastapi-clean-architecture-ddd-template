from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_session
from app.core.database import get_async_session
from app.modules.authentication.application.interfaces import (
    IAuthenticationRepository,
    IAuthenticationCache,
    ITokenService,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.infrastructure.caches import RedisAuthenticationCache
from app.modules.authentication.infrastructure.services import TokenService
from app.modules.authentication.infrastructure.repositories import (
    PostgresAuthenticationRepository,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.presentation.dependencies import get_shared_use_cases


def get_authentication_cache(
    cache: Redis = Depends(get_cache_session),
) -> IAuthenticationCache:
    return RedisAuthenticationCache(cache=cache)


def get_authentication_repository(
    session: AsyncSession = Depends(get_async_session),
) -> IAuthenticationRepository:
    return PostgresAuthenticationRepository(session=session)


def get_token_service() -> ITokenService:
    return TokenService()


def get_authentication_use_cases(
    cache: IAuthenticationCache = Depends(get_authentication_cache),
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    shared_service: SharedUseCases = Depends(get_shared_use_cases),
    token_service: ITokenService = Depends(get_token_service),
) -> AuthenticationUseCases:
    return AuthenticationUseCases(
        cache=cache,
        repository=repository,
        shared_service=shared_service,
        token_service=token_service,
    )
