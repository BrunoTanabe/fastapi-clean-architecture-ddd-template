# Module Stub Templates

Stub bodies for a freshly scaffolded module. Replace `{Module}`, `{Entity}`, `{module}`,
`{module-kebab}`, and `{plural_snake}` with the names from discovery.

## Contents

- [domain/entities.py](#domainentitiespy)
- [domain/enums.py](#domainenumspy)
- [domain/value_objects.py](#domainvalue_objectspy)
- [application/exceptions.py](#applicationexceptionspy)
- [application/interfaces.py](#applicationinterfacespy)
- [application/mappers.py](#applicationmapperspy)
- [application/use_cases.py](#applicationuse_casespy)
- [application/utils.py](#applicationutilspy)
- [infrastructure/models.py](#infrastructuremodelspy)
- [infrastructure/repositories.py](#infrastructurerepositoriespy)
- [infrastructure/caches.py](#infrastructurecachespy)
- [infrastructure/services.py](#infrastructureservicespy)
- [presentation/schemas.py](#presentationschemaspy)
- [presentation/docs.py](#presentationdocspy)
- [presentation/dependencies.py](#presentationdependenciespy)
- [presentation/routers.py](#presentationrouterspy)

## domain/entities.py

```python
from dataclasses import dataclass, field

from app.modules.shared.domain.entities import (
    BaseEntity,
    DomainErrors,
    PaginatedList,
    Pagination,
)
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN, UNSET
from app.modules.user.domain.entities import User
from app.modules.{module}.domain.enums import {Entity}SortField


@dataclass(kw_only=True, slots=True)
class {Entity}(BaseEntity):
    name: str = field(default=None, repr=True, compare=True)
    description: str | None = field(default=UNSET, repr=False, compare=False)

    created_by: User = field(default=None, repr=False, compare=False)
    updated_by: User = field(default=None, repr=False, compare=False)

    def __post_init__(self):
        errors: list[str] = []

        if self.name is not UNSET and self.name is not None:
            self.name = " ".join(self.name.strip().split())
            if self.name:
                self.name = self.name[0].upper() + self.name[1:]

            if len(self.name) < 3:
                errors.append("{Entity} name must be at least 3 characters long.")
            elif len(self.name) > 255:
                errors.append("{Entity} name must not exceed 255 characters.")
            elif not RESOURCE_NAME_PATTERN.match(self.name):
                errors.append(
                    "{Entity} name must contain only letters, numbers, spaces, hyphens, and underscores."
                )

        if errors:
            raise DomainErrors(errors)

    def deactivate(self, updated_by: User) -> None:  # noqa
        super().deactivate()
        self.updated_by = updated_by


@dataclass(kw_only=True, slots=True)
class {Entity}List(PaginatedList):
    items: list[{Entity}] = field(default_factory=list, repr=True, compare=False)


@dataclass(kw_only=True, slots=True)
class {Entity}Pagination(Pagination):
    sort_by: {Entity}SortField = field(
        default={Entity}SortField.CREATED_AT, repr=False, compare=False
    )
```

## domain/enums.py

```python
from enum import Enum


class {Entity}SortField(str, Enum):
    NAME = "name"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
```

Every member must be a real column name — the repository resolves it with `getattr`.

## domain/value_objects.py

Leave empty when the module reuses the shared value objects. See `/create-value-object` when it
needs its own.

## application/exceptions.py

```python
from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.application.exceptions import StandardException


# GENERIC EXCEPTIONS
class {Module}Exception(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the {module} module."
            },
        )


# SPECIFIC EXCEPTIONS
class {Entity}NotFoundException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"{Entity} with id '{id}' not found."},
        )
```

## application/interfaces.py

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

    # UPDATE
    async def update(self, entity: {Entity}) -> {Entity}: ...
```

## application/mappers.py

```python
import math

from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.domain.value_objects import UNSET
from app.modules.shared.presentation.schemas import PaginationMeta
from app.modules.user.domain.entities import User
from app.modules.{module}.domain.entities import {Entity}, {Entity}List, {Entity}Pagination
from app.modules.{module}.infrastructure.models import {Entity}Model
from app.modules.{module}.presentation.schemas import CreateRequest, GetResponse


# ENTITY / DTOS
def create_entity_mapper(payload: CreateRequest, authentication: Authentication) -> {Entity}:
    return mapper.to({Entity}).map(
        payload,
        fields_mapping={
            "name": payload.name,
            "description": payload.description,
            "created_by": authentication.user,
            "updated_by": authentication.user,
        },
    )


# ENTITY / MODELS
def model_entity_mapper(model: {Entity}Model) -> {Entity}:
    return mapper.to({Entity}).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "created_by": User(id=model.created_by),
            "updated_by": User(id=model.updated_by),
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def entity_model_mapper(entity: {Entity}) -> {Entity}Model:
    return mapper.to({Entity}Model).map(
        entity,
        fields_mapping={
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "created_by": entity.created_by.id,
            "updated_by": entity.updated_by.id,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        },
    )


def models_{entity}_list_mapper(rows: list) -> {Entity}List:
    return {Entity}List(
        items=[model_entity_mapper(row[0]) for row in rows],
        total=rows[0][1] if rows else 0,
    )
```

The inherited four are mandatory in both directions — automapper does not traverse parent `slots`.

## application/use_cases.py

```python
from loguru import logger

from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.{module}.application.exceptions import (
    {Module}Exception,
    {Entity}NotFoundException,
)
from app.modules.{module}.application.interfaces import I{Entity}Repository
from app.modules.{module}.domain.entities import {Entity}


class {Module}UseCases:
    def __init__(self, repository: I{Entity}Repository) -> None:
        self.repository = repository

    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        try:
            logger.debug(
                f"Initializing create {module} use case for '{entity.name}'. "
                f"Requested by user {entity.created_by.id}."
            )

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

## application/utils.py

Leave empty until the module needs a local helper.

## infrastructure/models.py

```python
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, Text, UUID as SQUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.settings import settings
from app.modules.shared.infrastructure.models import BaseModel

if TYPE_CHECKING:
    from app.modules.user.infrastructure.models import UserModel


class {Entity}Model(BaseModel):
    __tablename__ = f"{settings.APPLICATION_TABLE_PREFIX}_{plural_snake}"
    __table_args__ = (
        Index("ix_{plural_snake}_created_by", "created_by"),
        Index("ix_{plural_snake}_updated_by", "updated_by"),
    )

    name: Mapped[str] = mapped_column(
        String(255),
        name="name",
        comment="Human-readable name of the {entity}",
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        name="description",
        comment="Optional description of the {entity}",
        nullable=True,
        default=None,
    )

    created_by: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_users.id", ondelete="RESTRICT"),
        name="created_by",
        comment="Identifier of the user who created the {entity}",
        nullable=False,
    )

    updated_by: Mapped[UUID] = mapped_column(
        SQUID(as_uuid=True),
        ForeignKey(f"{settings.APPLICATION_TABLE_PREFIX}_users.id", ondelete="RESTRICT"),
        name="updated_by",
        comment="Identifier of the user who last updated the {entity}",
        nullable=False,
    )

    creator: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[created_by], lazy="noload"
    )

    updater: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[updated_by], lazy="noload"
    )
```

Leave the file empty when the module does not persist anything — `example`, `websocket`, and
`shared` all do.

Remember to register the model in `migrations/env.py`.

## infrastructure/repositories.py

```python
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.shared.application.exceptions import StandardException
from app.modules.{module}.application.exceptions import {Module}Exception
from app.modules.{module}.application.interfaces import I{Entity}Repository
from app.modules.{module}.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
)
from app.modules.{module}.domain.entities import {Entity}
from app.modules.{module}.infrastructure.models import {Entity}Model


class Postgres{Entity}Repository(I{Entity}Repository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, entity: {Entity}) -> {Entity}:
        try:
            logger.info(f"Creating {entity} '{entity.name}' in database.")

            db_model: {Entity}Model = entity_model_mapper(entity)

            self.session.add(db_model)
            await self.session.flush()

            logger.info(f"{Entity} '{entity.name}' created successfully in database.")
            return model_entity_mapper(db_model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create {entity} repository."
            )
            raise {Module}Exception()
```

## infrastructure/caches.py

Leave empty until the module caches. See `/create-cache`.

## infrastructure/services.py

Leave empty until the module wraps an external or stateful system. See `/create-service`.

## presentation/schemas.py

```python
from pydantic import BaseModel, ConfigDict, Field

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import (  # noqa: F401
    CreateResponse,
    DeleteResponse,
    UpdateResponse,
)


# REQUEST
class CreateRequest(BaseModel):
    name: str = Field(
        title="{Entity} Name (Required)",
        description="A human-readable name to identify the {entity}.",
        min_length=3,
        max_length=255,
        examples=["My {entity}"],
        json_schema_extra={"example": "My {entity}", "writeOnly": True},
    )

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Payload for creating a new {entity}.",
            "example": {"name": "My {entity}"},
        },
    )
```

## presentation/docs.py

Start with `router_docs` carrying the prefix, tag, and the standard error block — see
`/create-docs` for the full template.

```python
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse


# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/{module-kebab}",
    "tags": ["{Module}"],
    "responses": {
        # 400, 401, 403, 405, 422, 500, 502, 504
    },
}
```

## presentation/dependencies.py

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.modules.{module}.application.interfaces import I{Entity}Repository
from app.modules.{module}.application.use_cases import {Module}UseCases
from app.modules.{module}.infrastructure.repositories import Postgres{Entity}Repository


def get_{module}_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> I{Entity}Repository:
    return Postgres{Entity}Repository(session=session)


def get_{module}_use_cases(
    repository: Annotated[I{Entity}Repository, Depends(get_{module}_repository)],
) -> {Module}UseCases:
    return {Module}UseCases(repository=repository)
```

## presentation/routers.py

```python
from fastapi import APIRouter

from app.modules.{module}.presentation.docs import router_docs

router = APIRouter(**router_docs)
```

Handlers come from `/create-router` or `/create-endpoint`. A router with no routes is valid and
importable — just do not register it in `app/app.py` yet.
