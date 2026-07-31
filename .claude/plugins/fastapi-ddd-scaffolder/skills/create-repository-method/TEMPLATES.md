# Repository Templates

## Contents

- [Interface](#interface)
- [Implementation header](#implementation-header)
- [Create](#create)
- [Get by id](#get-by-id)
- [Get by a non-entity value](#get-by-a-non-entity-value)
- [Exists check](#exists-check)
- [Paginated list](#paginated-list)
- [Update](#update)
- [Soft delete](#soft-delete)
- [Get or create on a natural key](#get-or-create-on-a-natural-key)
- [Companion list mapper](#companion-list-mapper)

## Interface

`application/interfaces.py`. Bodies are `...`; grouped by verb.

```python
from typing import Protocol

from app.modules.{module}.domain.entities import {Entity}, {Entity}List, {Entity}Pagination


class I{Entity}Repository(Protocol):
    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}: ...

    # READ
    async def get_by_id(self, entity: {Entity}) -> {Entity} | None: ...

    async def get_all(
        self, entity: {Entity}, pagination: {Entity}Pagination
    ) -> {Entity}List: ...

    async def exists_by_name(self, entity: {Entity}) -> bool: ...

    # UPDATE
    async def update(self, entity: {Entity}) -> {Entity}: ...

    # DELETE
    async def delete(self, entity: {Entity}) -> {Entity}: ...
```

## Implementation header

```python
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import SortOrder
from app.modules.{module}.application.exceptions import {Module}Exception
from app.modules.{module}.application.interfaces import I{Entity}Repository
from app.modules.{module}.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    model_entity_with_actors_mapper,
    models_{entity}_list_mapper,
)
from app.modules.{module}.domain.entities import {Entity}, {Entity}List, {Entity}Pagination
from app.modules.{module}.infrastructure.models import {Entity}Model


class Postgres{Entity}Repository(I{Entity}Repository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
```

## Create

```python
    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        try:
            logger.info(
                f"Creating {entity} '{entity.name}' in database. "
                f"Requested by user {entity.created_by.id}."
            )

            db_model: {Entity}Model = entity_model_mapper(entity)

            self.session.add(db_model)
            await self.session.flush()

            logger.info(
                f"{Entity} '{entity.name}' created successfully in database "
                f"by user {entity.created_by.id}."
            )
            return model_entity_mapper(db_model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create {entity} repository."
            )
            raise {Module}Exception()
```

`flush()` populates the server-generated `id` and timestamps on `db_model`, which is why the return
mapper runs after it and not before.

## Get by id

`joinedload` when the response projects the actors; then return through the `_with_actors` mapper.

```python
    # READ
    async def get_by_id(self, entity: {Entity}) -> {Entity} | None:
        try:
            logger.info(f"Getting {entity} '{entity.id}' from database.")

            model = await self.session.scalar(
                select({Entity}Model)
                .options(
                    joinedload({Entity}Model.creator),
                    joinedload({Entity}Model.updater),
                )
                .where(
                    {Entity}Model.id == entity.id,
                    {Entity}Model.is_active.is_(True),
                )
            )

            logger.info(
                f"{Entity} '{entity.id}' {'found' if model else 'not found'} in database."
            )
            return model_entity_with_actors_mapper(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get {entity} by id repository."
            )
            raise {Module}Exception()
```

Returning `None` is correct here. Deciding that absence is a 404 belongs to the use case.

## Get by a non-entity value

Takes a bare value when the caller does not hold an entity — the API-key auth path is the live
example. Note the deliberate omission of the `is_active` filter, and the comment that explains it.

```python
    async def get_{entity}_by_{field}(self, {field}: str) -> {Entity} | None:
        try:
            logger.info("Getting {entity} by {field} from database.")

            # No is_active filter here (unlike the other reads): the auth path must
            # distinguish a revoked record (found but inactive) from an invalid one
            # (not found), so revoked rows must still be returned.
            model = await self.session.scalar(
                select({Entity}Model).where({Entity}Model.{field} == {field})
            )

            logger.info(
                f"{Entity} {'found' if model else 'not found'} by {field} in database."
            )
            return model_entity_mapper(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get {entity} by {field} repository."
            )
            raise {Module}Exception()
```

## Exists check

Select the id only and `limit(1)` — never load the row to answer a boolean.

```python
    async def exists_by_name(self, entity: {Entity}) -> bool:
        try:
            logger.debug(f"Checking whether {entity} '{entity.name}' exists in database.")

            result = await self.session.scalar(
                select({Entity}Model.id)
                .where(
                    {Entity}Model.name == entity.name,
                    {Entity}Model.is_active.is_(True),
                )
                .limit(1)
            )

            return result is not None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the exists {entity} by name repository."
            )
            raise {Module}Exception()
```

## Paginated list

One statement: the rows and the total together, via a window function.

```python
    async def get_all(
        self, entity: {Entity}, pagination: {Entity}Pagination
    ) -> {Entity}List:
        try:
            logger.info(
                f"Getting all active {entity_plural} from database. "
                f"Requested by user {entity.created_by.id}."
            )

            col = getattr({Entity}Model, pagination.sort_by.value)
            ordering = (
                col.asc() if pagination.sort_order == SortOrder.ASC else col.desc()
            )

            statement = (
                select(
                    {Entity}Model,
                    func.count({Entity}Model.id).over().label("total"),
                )
                .where({Entity}Model.is_active.is_(True))
                .order_by(ordering)
                .offset(pagination.offset)
                .limit(pagination.per_page)
            )

            result = await self.session.execute(statement)
            rows = result.all()

            entity_list = models_{entity}_list_mapper(rows)

            logger.info(
                f"Retrieved {len(entity_list.items)} of {entity_list.total} "
                f"active {entity_plural} from database."
            )
            return entity_list
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get all {entity_plural} repository."
            )
            raise {Module}Exception()
```

`func.count(...).over()` is an unbounded window, so every returned row carries the same total for
the whole filtered set — the count is not affected by `offset` or `limit`.

Add ownership filters to the `where` clause when the endpoint is scoped to the caller
(`{Entity}Model.created_by == entity.created_by.id`).

## Update

The use case has already merged, so the entity is complete and the repository assigns
unconditionally. It never inspects `UNSET`.

```python
    # UPDATE
    async def update(self, entity: {Entity}) -> {Entity}:
        try:
            logger.info(
                f"Updating {entity} '{entity.id}' in database. "
                f"Requested by user {entity.updated_by.id}."
            )

            model = await self.session.get({Entity}Model, entity.id)

            model.name = entity.name
            model.description = entity.description
            model.updated_by = entity.updated_by.id
            model.is_active = entity.is_active

            await self.session.flush()

            logger.info(f"{Entity} '{entity.id}' updated successfully in database.")
            return model_entity_mapper(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update {entity} repository."
            )
            raise {Module}Exception()
```

`session.get` is the right call for a primary-key fetch — it checks the identity map first.

A narrower mutation gets its own method rather than a flag on `update`. Reference:
`PostgresKeyRepository.rotate`, which touches only the key material.

## Soft delete

Deletion is `is_active = False` through the same `update` path. Because the entity's
`deactivate(updated_by)` already flipped the flag and recorded the actor, the use case can reuse
`update` instead of a dedicated method:

```python
existing.deactivate(updated_by=entity.updated_by)  # in the use case
return await self.repository.update(existing)
```

Add an explicit `delete` method only when the row must be physically removed.

## Get or create on a natural key

```python
    async def get_or_create(self, entity: {Entity}) -> {Entity}:
        try:
            existing = await self.session.scalar(
                select({Entity}Model).where(
                    {Entity}Model.user_id == entity.user.id,
                    {Entity}Model.device == entity.device,
                )
            )

            if existing is not None:
                logger.info(f"Existing {entity} found for the natural key. Reusing it.")
                return model_entity_mapper(existing)

            return await self.create(entity)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get or create {entity} repository."
            )
            raise {Module}Exception()
```

Back this with the matching `UniqueConstraint`, so a concurrent insert fails at the database rather
than creating a duplicate.

## Companion list mapper

Lives in `application/mappers.py`, under `# ENTITY / MODELS`:

```python
def models_{entity}_list_mapper(rows: list) -> {Entity}List:
    """Convert window-function rows [(Model, total), ...] into a {Entity}List."""
    return {Entity}List(
        items=[model_entity_mapper(row[0]) for row in rows],
        total=rows[0][1] if rows else 0,
    )
```
