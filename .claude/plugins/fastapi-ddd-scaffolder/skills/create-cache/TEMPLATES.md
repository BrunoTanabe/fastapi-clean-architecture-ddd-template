# Cache Templates

Every block below mirrors `app/modules/key/infrastructure/caches.py`, the canonical
implementation. Full rationale: `.claude/reference/caching.md`.

## Contents

- [Key conventions](#key-conventions)
- [Cache mappers](#cache-mappers)
- [Interface](#interface)
- [Implementation skeleton](#implementation-skeleton)
- [Insert with tombstone guard](#insert-with-tombstone-guard)
- [Read](#read)
- [Delete with tombstone](#delete-with-tombstone)
- [Multiple dimensions](#multiple-dimensions)
- [DI factory](#di-factory)
- [Use-case policy blocks](#use-case-policy-blocks)

## Key conventions

| Shape | Key | Used for |
|-------|-----|----------|
| By id | `{prefix}id:{uuid}` | `get_by_id` / `insert` / `delete` |
| By another dimension | `{prefix}hashed_key:{hash}` | credential and natural-key lookups |
| Page of a list | `{prefix}list:{scope}:page:{n}` | cached list pages |
| Tombstone | `{prefix}tombstone:{suffix}` | suppressing repopulation after invalidation |

`prefix` is always `f"{settings.REDIS_NAMESPACE}:{module}:"`. `REDIS_NAMESPACE` already folds in
`REDIS_KEY_PREFIX` and `REDIS_CACHE_VERSION`, so never build a key from `REDIS_KEY_PREFIX`
directly.

## Cache mappers

`application/mappers.py`, under `# ENTITY / CACHE`. Write these first — the cache imports them.

```python
def entity_cache_mapper(entity: {Entity}) -> str:
    return json.dumps(
        {
            "id": str(entity.id) if entity.id else None,
            "name": entity.name,
            "description": entity.description if entity.description is not UNSET else None,
            "created_by": str(entity.created_by.id) if entity.created_by else None,
            "updated_by": str(entity.updated_by.id) if entity.updated_by else None,
            "is_active": entity.is_active,
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
        }
    )


def cache_entity_mapper(raw: str) -> {Entity}:
    data = json.loads(raw)

    entity = {Entity}(
        id=UUID(data["id"]) if data["id"] else None,
        name=data["name"],
        description=data["description"],
        created_by=User(id=UUID(data["created_by"])) if data["created_by"] else None,
        updated_by=User(id=UUID(data["updated_by"])) if data["updated_by"] else None,
        created_at=datetime.fromisoformat(data["created_at"]) if data["created_at"] else None,
        updated_at=datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else None,
    )
    entity.is_active = data["is_active"]
    return entity
```

`core/cache.py` builds the client with `decode_responses=True`, so `get` returns `str` and
`json.loads` works directly — no manual decoding.

## Interface

Next to the repository Protocol in `application/interfaces.py`, grouped by verb. `ttl=None` means
"use the settings default".

```python
from typing import Protocol
from uuid import UUID

from app.modules.{module}.domain.entities import {Entity}


class I{Entity}Cache(Protocol):
    # CREATE
    async def insert(self, entity: {Entity}, ttl: int | None = None) -> None: ...

    # READ
    async def get_by_id(self, id: UUID) -> {Entity} | None: ...

    # DELETE
    async def delete(self, entity: {Entity}) -> None: ...
```

Nothing returns a bool and nothing raises — a caller cannot tell a cache miss from a cache failure,
and does not need to.

## Implementation skeleton

```python
from loguru import logger
from redis.asyncio import Redis

from app.core.settings import settings
from app.modules.{module}.application.interfaces import I{Entity}Cache
from app.modules.{module}.application.mappers import (
    cache_entity_mapper,
    entity_cache_mapper,
)
from app.modules.{module}.domain.entities import {Entity}


class Redis{Entity}Cache(I{Entity}Cache):
    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:{module}:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"

    def _tombstone(self, suffix: str) -> str:
        return f"{self.prefix}tombstone:{suffix}"
```

## Insert with tombstone guard

```python
    # CREATE
    async def insert(self, entity: {Entity}, ttl: int | None = None) -> None:
        try:
            suffix = f"id:{entity.id}"

            # A reader that missed the cache may only reach this point after a
            # concurrent invalidation has already run its delete, in which case it
            # would write back the pre-invalidation snapshot and keep stale data
            # alive until the ttl expired. The tombstone left behind by that delete
            # suppresses the write.
            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(
                    f"{Entity} '{entity.id}' was invalidated while being read. Skipping cache insert."
                )
                return None

            logger.debug(f"Caching {entity} '{entity.id}' in cache.")

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(entity),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(f"{Entity} '{entity.id}' cached successfully.")
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert {module} cache. The request continues without caching."
            )
            return None
```

Keep the comment. It is the only place the race is explained, and the guard looks removable
without it.

## Read

```python
    # READ
    async def get_by_id(self, id: UUID) -> {Entity} | None:
        try:
            logger.debug("Getting {entity} by id from cache.")

            raw = await self.cache.get(self._key(f"id:{id}"))

            logger.debug(f"{Entity} {'found' if raw else 'not found'} by id in cache.")
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get {module} by id cache. Falling back to the database."
            )
            return None
```

Both the miss and the failure return `None`, and the caller treats them identically — it goes to
the database either way.

## Delete with tombstone

```python
    # DELETE
    async def delete(self, entity: {Entity}) -> None:
        try:
            if not entity.id:
                logger.warning(f"{Entity} has no id. Skipping cache delete.")
                return None

            logger.debug(f"Invalidating {entity} '{entity.id}' in cache.")

            suffix = f"id:{entity.id}"

            # The tombstone is written first so that it is already in place while
            # the entry is being dropped, leaving no instant in which a delayed
            # repopulation could slip through unguarded.
            await self.cache.set(
                self._tombstone(suffix),
                1,
                ex=settings.REDIS_TOMBSTONE_TTL_SECONDS,
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(f"{Entity} '{entity.id}' invalidated successfully in cache.")
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete {module} cache. The entry remains until its ttl expires."
            )
            return None
```

The guard clause returns rather than raising — a missing id means there is nothing to invalidate,
not that the request should fail.

## Multiple dimensions

When one entity is reachable by more than one key, give each dimension its own method pair, and
call every delete on every mutating path. Reference: `RedisAuthenticationCache`.

```python
class I{Entity}Cache(Protocol):
    # CREATE
    async def insert_by_access_token(self, entity: {Entity}, ttl: int | None = None) -> None: ...
    async def insert_by_refresh_token(self, entity: {Entity}, ttl: int | None = None) -> None: ...

    # READ
    async def get_by_access_token(self, entity: {Entity}) -> {Entity} | None: ...
    async def get_by_refresh_token(self, entity: {Entity}) -> {Entity} | None: ...

    # DELETE
    async def delete_by_access_token(self, entity: {Entity}) -> None: ...
    async def delete_by_refresh_token(self, entity: {Entity}) -> None: ...
```

Missing one delete leaves a live entry under the other key — the most common cache bug in this
codebase.

## DI factory

`presentation/dependencies.py`:

```python
from redis.asyncio import Redis

from app.core.cache import get_cache_session
from app.modules.{module}.infrastructure.caches import Redis{Entity}Cache


def get_{module}_cache(
    cache: Annotated[Redis, Depends(get_cache_session)],
) -> I{Entity}Cache:
    return Redis{Entity}Cache(cache=cache)


def get_{module}_use_cases(
    cache: Annotated[I{Entity}Cache, Depends(get_{module}_cache)],
    repository: Annotated[I{Entity}Repository, Depends(get_{module}_repository)],
) -> {Module}UseCases:
    return {Module}UseCases(cache=cache, repository=repository)
```

When another module needs this cache, add the factory to
`shared/presentation/dependencies.py` as well — that file exists to avoid cross-module
`presentation` imports.

## Use-case policy blocks

**Read-through** — check the cache, fall back to the database, populate on the way out:

```python
    async def get_by_id(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(f"Initializing get {module} by id use case for {entity.id}.")

            cached = await self.cache.get_by_id(entity.id)
            if cached is not None:
                logger.debug(f"{Entity} '{entity.id}' served from cache.")
                return cached

            existing = await self.repository.get_by_id(entity)
            if existing is None:
                logger.info(f"{Entity} with id '{entity.id}' not found. Raising exception.")
                raise {Entity}NotFoundException(id=str(entity.id))

            await self.cache.insert(existing)

            logger.debug(f"Get {module} by id use case completed for {entity.id}.")
            return existing
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get {module} by id use case."
            )
            raise {Module}Exception()
```

**Write-then-invalidate** — mutate the database first, then drop every cached dimension:

```python
            updated = await self.repository.update(merged)

            # Invalidate with the pre-update entity: it holds the key material that
            # is actually stored in the cache.
            await self.cache.delete(existing)

            return updated
```

Never invalidate before the write succeeds — a failed write would leave the cache cleared for no
reason, and worse, a concurrent read could repopulate it from the unchanged row.
