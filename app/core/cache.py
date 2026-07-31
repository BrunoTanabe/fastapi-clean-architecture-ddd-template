from typing import AsyncIterator

from loguru import logger
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError

from app.core.settings import settings
from app.modules.shared.application.exceptions import StandardException


# connection pool
redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    socket_connect_timeout=settings.REDIS_CONNECTION_TIMEOUT_SECONDS,
    socket_timeout=settings.REDIS_SOCKET_TIMEOUT_SECONDS,
    decode_responses=True,
)

redis_client = Redis(connection_pool=redis_pool)


async def get_cache_session() -> AsyncIterator[Redis]:
    try:
        yield redis_client
    except StandardException:
        raise
    except RedisError as e:
        logger.opt(exception=e).error("A cache error occurred during the operation.")
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred during the cache operation."
        )
        raise


# cache connection for resources
async def init_cache_client() -> None:
    try:
        logger.info("Establishing cache connection.")

        await redis_client.ping()

        logger.info("Cache connection established successfully.")
    except StandardException:
        raise
    except RedisError as e:
        logger.opt(exception=e).error("An error occurred while initializing the cache.")
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while initializing the cache."
        )
        raise


async def flush_cache_namespace() -> None:
    try:
        logger.info("Flushing application cache namespace...")

        deleted = 0

        async for key in redis_client.scan_iter(
            match=f"{settings.REDIS_KEY_PREFIX}:*", count=500
        ):
            await redis_client.unlink(key)
            deleted += 1

        logger.info(f"Cache namespace flushed successfully. {deleted} keys removed.")
    except RedisError as e:
        logger.opt(exception=e).error(
            "An error occurred while flushing the cache namespace. The application continues without it."
        )
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while flushing the cache namespace. The application continues without it."
        )


async def close_cache_client() -> None:
    try:
        await redis_client.aclose()
        await redis_pool.disconnect()

        logger.info("Cache connection closed successfully.")
    except RedisError as e:
        logger.opt(exception=e).error(
            "An error occurred while closing the cache connection."
        )
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred while closing the cache connection."
        )
        raise
