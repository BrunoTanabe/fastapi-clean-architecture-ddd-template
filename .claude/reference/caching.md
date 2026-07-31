# Reference — Redis Caching

The cache-aside layer: namespacing, key shapes, the tombstone protocol, and the never-raise
error policy. `RedisKeyCache` (`app/modules/key/infrastructure/caches.py`) is the canonical
implementation.

## Contents

- [Division of responsibility](#division-of-responsibility)
- [Connection layer](#connection-layer)
- [Namespace and versioning](#namespace-and-versioning)
- [Key shapes](#key-shapes)
- [The Protocol](#the-protocol)
- [The implementation](#the-implementation)
- [The tombstone protocol](#the-tombstone-protocol)
- [The never-raise policy](#the-never-raise-policy)
- [Cache mappers](#cache-mappers)
- [Cache-aside policy in the use case](#cache-aside-policy-in-the-use-case)
- [Dependency wiring](#dependency-wiring)
- [Settings](#settings)

## Division of responsibility

| Concern | Owner |
|---------|-------|
| Connection pool, lifecycle, startup flush | `app/core/cache.py` |
| Key layout, serialization, Redis commands | `infrastructure/caches.py` |
| Contract | `application/interfaces.py` (`I{Entity}Cache`) |
| **Policy** — when to read, when to invalidate, which TTL | `application/use_cases.py` |
| Serialization functions | `application/mappers.py` |

The cache class is a dumb executor. It never decides whether a read should happen, never chooses a
TTL beyond the default, and never invalidates on its own.

Postgres is always the source of truth. Redis is an accelerator that the application must be able
to lose at any moment.

## Connection layer

`app/core/cache.py` owns a module-level `ConnectionPool` and a single `Redis` client with
`decode_responses=True` (so values come back as `str`, not `bytes`).

- `get_cache_session() -> AsyncIterator[Redis]` — the DI generator every cache factory depends on.
- `init_cache_client()` — startup `PING`.
- `flush_cache_namespace()` — `scan_iter` + `unlink` over `{REDIS_KEY_PREFIX}:*`, run at startup
  when `REDIS_FLUSH_ON_STARTUP` is set. Best-effort: it logs and continues on failure.
- `close_cache_client()` — graceful shutdown.

## Namespace and versioning

```python
# settings.py
@computed_field
@cached_property
def REDIS_NAMESPACE(self) -> str:
    return f"{self.REDIS_KEY_PREFIX}:v{self.REDIS_CACHE_VERSION}"
```

Every key hangs off `REDIS_NAMESPACE`. Bumping `REDIS_CACHE_VERSION` makes the previous generation
unreachable, so entries written in an old payload format are never read back — they simply expire
by TTL.

**Bump `REDIS_CACHE_VERSION` whenever you change what `entity_cache_mapper` writes.** That is the
correct response to a format change, not flushing the cache and not adding migration logic to
`cache_entity_mapper`.

## Key shapes

```python
self.prefix = f"{settings.REDIS_NAMESPACE}:{module}:"

def _key(self, suffix: str) -> str:
    return f"{self.prefix}{suffix}"

def _tombstone(self, suffix: str) -> str:
    return f"{self.prefix}tombstone:{suffix}"
```

Suffixes name the lookup dimension, so one entity can be cached under several access paths:

| Suffix | Example key |
|--------|-------------|
| `id:{uuid}` | `app:v1:key:id:0b7f…` |
| `hashed_key:{hash}` | `app:v1:key:hashed_key:9c2a…` |
| `list:{scope}:page:{n}` | `app:v1:key:list:all:page:1` |

Every cached dimension must be invalidated on mutation. Caching an entity under two suffixes and
deleting only one is the most common cache bug in this codebase.

## The Protocol

Declared next to the repository interface in `application/interfaces.py`, grouped by CRUD verb:

```python
class IKeyCache(Protocol):
    # CREATE
    async def insert(self, key: Key, ttl: int | None = None) -> None: ...

    # READ
    async def get_by_hashed_key(self, hashed_key: str) -> Key | None: ...

    # DELETE
    async def delete(self, key: Key) -> None: ...
```

Writes accept an optional `ttl: int | None = None` that falls back to
`settings.REDIS_DEFAULT_TTL_SECONDS`. Reads return `Entity | None`. Nothing returns a bool or
raises.

## The implementation

```python
class RedisMyEntityCache(IMyEntityCache):
    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:my_module:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"

    def _tombstone(self, suffix: str) -> str:
        return f"{self.prefix}tombstone:{suffix}"

    # CREATE
    async def insert(self, entity: MyEntity, ttl: int | None = None) -> None:
        try:
            suffix = f"id:{entity.id}"

            if await self.cache.exists(self._tombstone(suffix)):
                logger.info(f"Entity '{entity.id}' was invalidated while being read. Skipping cache insert.")
                return None

            logger.debug(f"Caching entity '{entity.id}' in cache.")

            await self.cache.set(
                self._key(suffix),
                entity_cache_mapper(entity),
                ex=ttl if ttl is not None else settings.REDIS_DEFAULT_TTL_SECONDS,
            )

            logger.debug(f"Entity '{entity.id}' cached successfully.")
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the insert my_module cache. The request continues without caching."
            )
            return None

    # READ
    async def get_by_id(self, id: UUID) -> MyEntity | None:
        try:
            logger.debug("Getting entity by id from cache.")

            raw = await self.cache.get(self._key(f"id:{id}"))

            logger.debug(f"Entity {'found' if raw else 'not found'} by id in cache.")
            return cache_entity_mapper(raw) if raw else None
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get my_module by id cache. Falling back to the database."
            )
            return None

    # DELETE
    async def delete(self, entity: MyEntity) -> None:
        try:
            if not entity.id:
                logger.warning("Entity has no id. Skipping cache delete.")
                return None

            logger.debug(f"Invalidating entity '{entity.id}' in cache.")

            suffix = f"id:{entity.id}"

            await self.cache.set(
                self._tombstone(suffix), 1, ex=settings.REDIS_TOMBSTONE_TTL_SECONDS
            )
            await self.cache.delete(self._key(suffix))

            logger.debug(f"Entity '{entity.id}' invalidated successfully in cache.")
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete my_module cache. The entry remains until its ttl expires."
            )
            return None
```

## The tombstone protocol

Without tombstones this interleaving silently resurrects revoked data:

```
reader:  cache miss → read from DB → ................. → write snapshot to cache
writer:                    → revoke in DB → delete cache key
```

The reader's write lands after the writer's delete, and a revoked entity keeps authenticating
until its TTL expires.

The protocol closes it:

1. `delete` writes the tombstone **first**, then removes the entry. Doing it in that order leaves
   no instant where a delayed repopulation is unguarded.
2. `insert` checks the tombstone **before** writing and skips the write if one exists.
3. Tombstones expire after `REDIS_TOMBSTONE_TTL_SECONDS`, which must exceed the longest plausible
   read-then-write window.

Apply it to any entity whose staleness has a security or correctness consequence — credentials,
permissions, revocations. A read-mostly display cache can skip it.

## The never-raise policy

**Cache methods never raise, never propagate, and never fail a request.** Every method wraps its
body in `try`/`except Exception`, logs with `logger.opt(exception=e).error(...)`, and returns
`None`.

There is deliberately no `except StandardException: raise` branch — that is what separates this
shape from the 2-branch repository shape. A cache is an optimization; losing it degrades
performance, not correctness.

The log message states the consequence so the operator knows the impact:

- read failure → "Falling back to the database."
- write failure → "The request continues without caching."
- delete failure → "The entry remains until its ttl expires."

Guard clauses return early rather than raising: a missing id or hash logs a `warning` and returns.

## Cache mappers

Serialization lives in `application/mappers.py` under `# ENTITY / CACHE`, never inside the cache
class.

```python
def entity_cache_mapper(entity: MyEntity) -> str:
    return json.dumps(
        {
            "id": str(entity.id) if entity.id else None,
            "name": entity.name,
            "description": entity.description if entity.description is not UNSET else None,
            "created_by": str(entity.created_by.id) if entity.created_by else None,
            "is_active": entity.is_active,
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
        }
    )


def cache_entity_mapper(raw: str) -> MyEntity:
    data = json.loads(raw)

    entity = MyEntity(
        id=UUID(data["id"]) if data["id"] else None,
        name=data["name"],
        description=data["description"],
        created_by=User(id=UUID(data["created_by"])) if data["created_by"] else None,
        created_at=datetime.fromisoformat(data["created_at"]) if data["created_at"] else None,
        updated_at=datetime.fromisoformat(data["updated_at"]) if data["updated_at"] else None,
    )
    entity.is_active = data["is_active"]
    return entity
```

Rules:

- Round-trip every field the consumer reads. A field silently dropped here becomes `None` on a
  cache hit and correct on a cache miss — an intermittent bug that only appears under load.
- `UUID` → `str`, `datetime` → `.isoformat()`, `UNSET` → `None`.
- Related entities are stored as bare ids and rebuilt as minimal entities (`User(id=...)`).
- `is_active` is `init=False` on `BaseEntity`, so assign it after construction.
- Changing this payload means bumping `REDIS_CACHE_VERSION`.
- Never cache a secret. `Key.plain_key` is transient and must never reach `entity_cache_mapper`.

## Cache-aside policy in the use case

The use case decides; the cache executes.

**Read-through:**

```python
cached = await self.cache.get_by_id(entity.id)
if cached is not None:
    return cached

existing = await self.repository.get_by_id(entity)
if existing is None:
    raise MyEntityNotFoundException(id=str(entity.id))

await self.cache.insert(existing)
return existing
```

**Write-then-invalidate** — mutate the database first, then drop every cached dimension:

```python
updated = await self.repository.update(merged)
await self.cache.delete(existing)   # pass the pre-update entity: it holds the old key material
return updated
```

Invalidate with the entity whose fields produce the *stored* keys. Rotating an API key changes
`hashed_key`, so the delete must use the pre-rotation entity or the old entry outlives the
rotation. `AuthenticationUseCases` shows the multi-dimension form —
`delete_by_access_token` and `delete_by_refresh_token` are both called on logout, refresh, and
re-login.

Never cache inside a repository, and never invalidate from a router.

## Settings

| Setting | Purpose |
|---------|---------|
| `REDIS_KEY_PREFIX` | Root of the namespace |
| `REDIS_CACHE_VERSION` | Generation counter; bump on payload-format change |
| `REDIS_DEFAULT_TTL_SECONDS` | Fallback TTL for writes |
| `REDIS_SESSION_TTL_SECONDS` | TTL for authentication entries |
| `REDIS_TOMBSTONE_TTL_SECONDS` | How long a tombstone suppresses repopulation |
| `REDIS_FLUSH_ON_STARTUP` | Wipe the namespace during lifespan startup |
| `REDIS_MAX_CONNECTIONS` | Pool size |
| `REDIS_CONNECTION_TIMEOUT_SECONDS` / `REDIS_SOCKET_TIMEOUT_SECONDS` | Pool timeouts |
| `REDIS_SSL`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_USERNAME`, `REDIS_PASSWORD` | Connection (composed into `REDIS_URL`) |
