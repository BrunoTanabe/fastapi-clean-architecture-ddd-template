# Use Case Templates

Every block mirrors `app/modules/key/application/use_cases.py`.

## Contents

- [File header and class skeleton](#file-header-and-class-skeleton)
- [Create](#create)
- [Create with a transient secret](#create-with-a-transient-secret)
- [Get by id](#get-by-id)
- [Get by id with read-through cache](#get-by-id-with-read-through-cache)
- [Get all](#get-all)
- [Update with the UNSET merge](#update-with-the-unset-merge)
- [Soft delete](#soft-delete)
- [Rotate](#rotate)
- [Broadcast notification](#broadcast-notification)
- [SharedUseCases lookups](#sharedusecases-lookups)

## File header and class skeleton

```python
from loguru import logger

from app.modules.{module}.application.exceptions import (
    {Module}Exception,
    {Entity}NotFoundException,
    {Entity}NotModifiedException,
)
from app.modules.{module}.application.interfaces import (
    I{Entity}Cache,
    I{Entity}Repository,
    I{Name}Service,
)
from app.modules.{module}.domain.entities import {Entity}, {Entity}List, {Entity}Pagination
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.domain.value_objects import UNSET


class {Module}UseCases:
    def __init__(
        self,
        cache: I{Entity}Cache,
        repository: I{Entity}Repository,
        service: I{Name}Service,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.service = service
```

Omit collaborators the module does not use. `example` has none at all — `ExampleUseCases.hello` is
a `@staticmethod`.

With `SharedUseCases`, set the lookup mode in `__init__`:

```python
        self.shared_service = shared_service
        self.shared_service.disable_exceptions()
```

## Create

```python
    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(
                f"Initializing create {module} use case for '{entity.name}'. "
                f"Requested by user {entity.created_by.id}."
            )

            if await self.repository.exists_by_name(entity):
                logger.info(
                    f"{Entity} with name '{entity.name}' already exists. Raising exception."
                )
                raise {Entity}NameAlreadyExistsException(name=entity.name)

            entity = await self.repository.create(entity)

            logger.debug(f"Create {module} use case completed successfully for {entity.id}.")
            return entity
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create {module} use case."
            )
            raise {Module}Exception()
```

The `exists_by_name` check produces a clear 409; the database's unique constraint stays as the
backstop against a race.

## Create with a transient secret

The repository returns the entity rebuilt from the model, and the model has no secret column — so
the plain value must be carried across by hand. Reference: `KeyUseCases.create`.

```python
            entity = await self.service.generate(entity)
            plain_key = entity.plain_key

            entity = await self.repository.create(entity)
            entity.plain_key = plain_key
```

Never log `plain_key`, never cache it, and return it only from the create and rotate responses.

## Get by id

```python
    # READ
    async def get_by_id(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(
                f"Initializing get {module} by id use case for {entity.id}. "
                f"Requested by user {entity.created_by.id}."
            )

            existing = await self.repository.get_by_id(entity)
            if existing is None:
                logger.info(f"{Entity} with id '{entity.id}' not found. Raising exception.")
                raise {Entity}NotFoundException(id=str(entity.id))

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

The repository returns `None`; turning that into a 404 is this layer's decision.

## Get by id with read-through cache

```python
            cached = await self.cache.get_by_id(entity.id)
            if cached is not None:
                logger.debug(f"{Entity} '{entity.id}' served from cache.")
                return cached

            existing = await self.repository.get_by_id(entity)
            if existing is None:
                logger.info(f"{Entity} with id '{entity.id}' not found. Raising exception.")
                raise {Entity}NotFoundException(id=str(entity.id))

            await self.cache.insert(existing)

            return existing
```

Only populate the cache after a successful read. Never cache a miss.

## Get all

```python
    async def get_all(
        self, entity: {Entity}, pagination: {Entity}Pagination
    ) -> {Entity}List:
        try:
            logger.debug(
                f"Initializing get all {entity_plural} use case. "
                f"Requested by user {entity.created_by.id}."
            )

            entity_list = await self.repository.get_all(entity, pagination)

            logger.debug(
                f"Get all {entity_plural} use case completed. "
                f"Found {len(entity_list.items)} of {entity_list.total} total."
            )
            return entity_list
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get all {entity_plural} use case."
            )
            raise {Module}Exception()
```

An empty page is a valid result — never raise not-found from a list operation.

## Update with the UNSET merge

The core of partial updates. Fetch, merge, detect a no-op, persist, invalidate.

```python
    # UPDATE
    async def update(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(
                f"Initializing update {module} use case for {entity.id}. "
                f"Requested by user {entity.updated_by.id}."
            )

            existing = await self.repository.get_by_id(entity)
            if existing is None:
                logger.info(f"{Entity} with id '{entity.id}' not found. Raising exception.")
                raise {Entity}NotFoundException(id=str(entity.id))

            merged = {Entity}(
                id=existing.id,
                name=entity.name if entity.name is not UNSET else existing.name,
                description=entity.description
                if entity.description is not UNSET
                else existing.description,
                created_by=existing.created_by,
                updated_by=entity.updated_by,
            )

            if merged.name == existing.name and merged.description == existing.description:
                logger.info(f"{Entity} '{entity.id}' has no changes. Raising exception.")
                raise {Entity}NotModifiedException(id=str(entity.id))

            updated = await self.repository.update(merged)

            # Invalidate with the pre-update entity: it holds the key material that
            # is actually stored in the cache.
            await self.cache.delete(existing)

            logger.debug(f"Update {module} use case completed successfully for {entity.id}.")
            return updated
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the update {module} use case."
            )
            raise {Module}Exception()
```

Three details that are easy to get wrong:

- `created_by=existing.created_by` — an update must never rewrite authorship.
- Constructing `{Entity}(...)` re-runs `__post_init__`, so the merged result is validated. That is
  why the merge builds a new entity instead of mutating `existing`.
- Invalidate **after** the write succeeds, using the pre-update entity.

## Soft delete

Deactivation is a domain operation, so the entity performs it and the repository just persists.

```python
    # DELETE
    async def delete(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(
                f"Initializing delete {module} use case for {entity.id}. "
                f"Requested by user {entity.updated_by.id}."
            )

            existing = await self.repository.get_by_id(entity)
            if existing is None:
                logger.info(f"{Entity} with id '{entity.id}' not found. Raising exception.")
                raise {Entity}NotFoundException(id=str(entity.id))

            existing.deactivate(updated_by=entity.updated_by)
            deleted = await self.repository.update(existing)

            await self.cache.delete(existing)

            logger.debug(f"Delete {module} use case completed successfully for {entity.id}.")
            return deleted
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the delete {module} use case."
            )
            raise {Module}Exception()
```

Invalidating the cache on a revocation is not optional — a cached credential that outlives its
revocation is a security bug. This is exactly what the tombstone protocol protects.

## Rotate

A narrow mutation gets its own method rather than a flag on `update`.

```python
            existing = await self.repository.get_by_id(entity)
            if existing is None:
                raise {Entity}NotFoundException(id=str(entity.id))

            regenerated = await self.service.generate(existing)
            plain_key = regenerated.plain_key

            rotated = await self.repository.rotate(regenerated)
            rotated.plain_key = plain_key

            # The stored cache entry is keyed on the OLD material, so invalidate
            # with the pre-rotation entity.
            await self.cache.delete(existing)
```

## Broadcast notification

Persist first, then notify. Reference: `KnowledgeUseCases.create`.

```python
from app.modules.notification.domain.entities import Notification
from app.modules.notification.domain.enums import NotificationType
from app.modules.shared.domain.enums import Role


            creator = entity.created_by
            entity = await self.repository.create(entity)

            await self.shared_service.create_broadcast_notification(
                Notification(
                    originated_from_broadcast=Role.MANAGER,
                    notification_type=NotificationType.{ENTITY}_CREATED,
                    title="{Entity} created",
                    body=f"{Entity} '{entity.name}' was created by {creator.name}.",
                )
            )
```

Capture `entity.created_by` before the repository call — the returned entity carries only a minimal
`User(id=...)` stub, so `creator.name` would be `None` afterwards.

`SharedUseCases` dispatches over WebSocket best-effort: a delivery failure logs a warning and never
breaks the database write.

## SharedUseCases lookups

```python
            user = await self.shared_service.get_user_by_id(User(id=entity.created_by.id))
            if user is None:
                raise {Entity}NotFoundException(id=str(entity.id))
```

With `disable_exceptions()` set in `__init__`, the lookups return `None` on miss and the use case
decides what that means. Without it, they raise `UserIdNotFoundException` directly.
