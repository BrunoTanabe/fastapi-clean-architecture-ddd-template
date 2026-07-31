from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings
from app.modules.authentication.application.interfaces import IAuthenticationCache
from app.modules.authentication.application.mappers import (
    cache_entity_mapper,
    entity_cache_mapper,
)
from app.modules.authentication.domain.entities import Authentication


class RedisAuthenticationCache(IAuthenticationCache):
    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:authentication:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"

    def _tombstone(self, suffix: str) -> str:
        return f"{self.prefix}tombstone:{suffix}"

    # CREATE
    async def insert_by_access_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no access token hashed_jti. Skipping cache insert."
                )
                return

            suffix = f"access_token:{hashed_jti}"

            # A reader that missed the cache may only reach this point after a
            # concurrent logout or refresh has already run its delete, in which
            # case it would write back the pre-revocation snapshot and keep a
            # revoked authentication authenticating until the ttl expired. The tombstone
            # left behind by that delete suppresses the write.
            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Authentication '{authentication.id}' was invalidated while being read. Skipping cache insert by access token."
                )
                return

            logger.debug(
                f"Caching authentication '{authentication.id}' by access token."
            )

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(authentication),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Authentication '{authentication.id}' cached successfully by access token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert authentication by access token cache. The request continues without caching."
            )
            return

    async def insert_by_refresh_token(
        self, authentication: Authentication, ttl: int | None = None
    ) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no refresh token hashed_jti. Skipping cache insert."
                )
                return

            suffix = f"refresh_token:{hashed_jti}"

            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Authentication '{authentication.id}' was invalidated while being read. Skipping cache insert by refresh token."
                )
                return

            logger.debug(
                f"Caching authentication '{authentication.id}' by refresh token."
            )

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(authentication),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Authentication '{authentication.id}' cached successfully by refresh token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert authentication by refresh token cache. The request continues without caching."
            )
            return

    # READ
    async def get_by_access_token(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                return None

            logger.debug("Getting authentication by access token from cache.")

            raw = await self.cache.get(self._key(f"access_token:{hashed_jti}"))

            logger.debug(
                f"Authentication {'found' if raw else 'not found'} by access token in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by access token cache. Falling back to the database."
            )
            return None

    async def get_by_refresh_token(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                return None

            logger.debug("Getting authentication by refresh token from cache.")

            raw = await self.cache.get(self._key(f"refresh_token:{hashed_jti}"))

            logger.debug(
                f"Authentication {'found' if raw else 'not found'} by refresh token in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by refresh token cache. Falling back to the database."
            )
            return None

    # DELETE
    async def delete_by_access_token(self, authentication: Authentication) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.access_token.hashed_jti
                if authentication.refresh_token
                and authentication.refresh_token.access_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no access token hashed_jti. Skipping cache delete."
                )
                return

            logger.debug(
                f"Invalidating authentication '{authentication.id}' by access token."
            )

            suffix = f"access_token:{hashed_jti}"

            # The tombstone is written first so that it is already in place while
            # the entry is being dropped, leaving no instant in which a delayed
            # repopulation could slip through unguarded.
            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(
                f"Authentication '{authentication.id}' invalidated successfully by access token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication by access token cache. The entry remains until its ttl expires."
            )
            return

    async def delete_by_refresh_token(self, authentication: Authentication) -> None:
        try:
            hashed_jti = (
                authentication.refresh_token.hashed_jti
                if authentication.refresh_token
                else None
            )

            if not hashed_jti:
                logger.warning(
                    f"Authentication '{authentication.id}' has no refresh token hashed_jti. Skipping cache delete."
                )
                return

            logger.debug(
                f"Invalidating authentication '{authentication.id}' by refresh token."
            )

            suffix = f"refresh_token:{hashed_jti}"

            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(
                f"Authentication '{authentication.id}' invalidated successfully by refresh token."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication by refresh token cache. The entry remains until its ttl expires."
            )
            return
