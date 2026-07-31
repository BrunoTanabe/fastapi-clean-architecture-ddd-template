from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings
from app.modules.key.application.interfaces import IKeyCache
from app.modules.key.application.mappers import (
    cache_entity_mapper,
    entity_cache_mapper,
)
from app.modules.key.domain.entities import Key


class RedisKeyCache(IKeyCache):
    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:key:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"

    def _tombstone(self, suffix: str) -> str:
        return f"{self.prefix}tombstone:{suffix}"

    # CREATE
    async def insert(self, key: Key, ttl: int | None = None) -> None:
        try:
            suffix = f"hashed_key:{key.hashed_key}"

            # A reader that missed the cache may only reach this point after a
            # concurrent revocation has already run its delete, in which case it
            # would write back the pre-revocation snapshot and keep a revoked key
            # authenticating until the ttl expired. The tombstone left behind by
            # that delete suppresses the write.
            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"Api key '{key.prefix}...{key.last_four}' was invalidated while being read. Skipping cache insert."
                )
                return None

            logger.debug(f"Caching api key '{key.prefix}...{key.last_four}' in cache.")

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(key),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(
                f"Api key '{key.prefix}...{key.last_four}' cached successfully."
            )
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert key cache. The request continues without caching."
            )
            return None

    # READ
    async def get_by_hashed_key(self, hashed_key: str) -> Key | None:
        try:
            logger.debug("Getting api key by hashed key from cache.")

            raw = await self.cache.get(self._key(f"hashed_key:{hashed_key}"))

            logger.debug(
                f"Api key {'found' if raw else 'not found'} by hashed key in cache."
            )
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get key by hashed key cache. Falling back to the database."
            )
            return None

    # DELETE
    async def delete(self, key: Key) -> None:
        try:
            if not key.hashed_key:
                logger.warning(
                    f"Api key '{key.id}' has no hashed key. Skipping cache delete."
                )
                return None

            logger.debug(f"Invalidating api key '{key.id}' in cache.")

            suffix = f"hashed_key:{key.hashed_key}"

            # The tombstone is written first so that it is already in place while
            # the entry is being dropped, leaving no instant in which a delayed
            # repopulation could slip through unguarded.
            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(f"Api key '{key.id}' invalidated successfully in cache.")
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete key cache. The entry remains until its ttl expires."
            )
            return None
