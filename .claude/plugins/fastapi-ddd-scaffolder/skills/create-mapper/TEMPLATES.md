# Mapper Templates

## Contents

- [File header](#file-header)
- [Request to entity](#request-to-entity)
- [Partial-update request to entity](#partial-update-request-to-entity)
- [Entity to response](#entity-to-response)
- [Actor projection helpers](#actor-projection-helpers)
- [Paginated list mappers](#paginated-list-mappers)
- [Model to entity](#model-to-entity)
- [Model to entity with actors](#model-to-entity-with-actors)
- [Entity to model](#entity-to-model)
- [Reserved metadata bridge](#reserved-metadata-bridge)
- [Value objects](#value-objects)
- [Cache serializers](#cache-serializers)

## File header

```python
import json
import math
from datetime import datetime
from uuid import UUID

from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.{module}.domain.entities import {Entity}, {Entity}List, {Entity}Pagination
from app.modules.{module}.infrastructure.models import {Entity}Model
from app.modules.{module}.presentation.schemas import (
    ActorResponse,
    CreateRequest,
    Create{Entity}Response,
    GetAllResponse,
    GetResponse,
    {Entity}ListItem,
    {Entity}PaginationParams,
    UpdateRequest,
)
from app.modules.shared.domain.enums import SortOrder
from app.modules.shared.domain.value_objects import Name, UNSET
from app.modules.shared.presentation.schemas import (
    DeleteResponse,
    PaginationMeta,
    UpdateResponse,
)
from app.modules.user.domain.entities import User


# ENTITY / DTOS
...

# ENTITY / MODELS
...

# ENTITY / CACHE
...
```

## Request to entity

```python
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
```

On creation `created_by` and `updated_by` are both the acting user. Derived values are computed by
a helper from `application/utils.py`, not inline — reference:
`"expires_at": resolve_expires_at(payload.expires_in)`.

## Partial-update request to entity

Built by hand, not through automapper, because every field needs the `model_fields_set` check.

```python
def update_entity_mapper(
    id: UUID, payload: UpdateRequest, authentication: Authentication
) -> {Entity}:
    return {Entity}(
        id=id,
        name=payload.name if "name" in payload.model_fields_set else UNSET,
        description=payload.description
        if "description" in payload.model_fields_set
        else UNSET,
        updated_by=authentication.user,
    )
```

`created_by` is deliberately absent — the use case restores it from the stored record so an update
can never rewrite authorship.

Delete and rotate mappers are the minimal version of the same idea:

```python
def delete_entity_mapper(id: UUID, authentication: Authentication) -> {Entity}:
    return {Entity}(id=id, updated_by=authentication.user)
```

## Entity to response

```python
def entity_create_mapper(entity: {Entity}) -> Create{Entity}Response:
    return mapper.to(Create{Entity}Response).map(
        entity,
        fields_mapping={"api_key": entity.plain_key},
    )


def entity_update_mapper(entity: {Entity}) -> UpdateResponse:
    return UpdateResponse()


def entity_delete_mapper(entity: {Entity}) -> DeleteResponse:
    return DeleteResponse()


def entity_get_mapper(entity: {Entity}) -> GetResponse:
    return mapper.to(GetResponse).map(
        entity,
        fields_mapping={
            "id": entity.id,
            "name": entity.name,
            "description": entity.description if entity.description is not UNSET else None,
            "created_by": _actor_response(entity.created_by),
            "updated_by": _actor_response(entity.updated_by),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        },
    )
```

Update and delete mappers still take the entity even though they ignore it — the router calls every
mapper the same way, so the uniform signature is what keeps handlers identical.

Always normalize `UNSET` to `None` on the way out. A response schema has no idea what `UNSET` is.

## Actor projection helpers

Private helpers, prefixed with `_`, placed next to the mappers that use them.

```python
def _actor_response(user: User) -> ActorResponse:
    return ActorResponse(
        email=str(user.email),
        preferred_name=user.name.preferred_name,
    )
```

This only works when the repository loaded the relationship — see
`model_entity_with_actors_mapper` below.

## Paginated list mappers

```python
def get_all_entity_mapper(
    authentication: Authentication, query_params: {Entity}PaginationParams
) -> tuple[{Entity}, {Entity}Pagination]:
    entity = {Entity}(
        created_by=authentication.user,
        updated_by=authentication.user,
    )
    pagination = {Entity}Pagination(
        page=query_params.page,
        per_page=query_params.limit,
        sort_order=SortOrder(query_params.sort_order),
        sort_by=query_params.sort_by,
    )

    return entity, pagination


def entities_get_all_mapper(
    entity_list: {Entity}List, pagination: {Entity}Pagination
) -> GetAllResponse:
    total = entity_list.total
    total_pages = math.ceil(total / pagination.per_page) if pagination.per_page else 0

    return GetAllResponse(
        items=[
            {Entity}ListItem(
                id=entity.id,
                name=entity.name,
                description=entity.description if entity.description is not UNSET else None,
                created_at=entity.created_at,
            )
            for entity in entity_list.items
        ],
        pagination=PaginationMeta(
            total=total,
            page=pagination.page,
            limit=pagination.per_page,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1,
        ),
    )
```

Note the vocabulary shift: the HTTP layer says `limit`, the domain says `per_page`. The request
mapper translates one way and the response mapper the other.

The entity returned by `get_all_entity_mapper` carries the actor so the repository and use case can
log and authorize; it is not a filter.

## Model to entity

```python
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
```

The inherited four are mandatory. FKs become minimal `User(id=...)` stubs — enough for a caller to
read the id, without a second query.

## Model to entity with actors

Used when the repository issued `joinedload(Model.creator)` / `joinedload(Model.updater)` and the
response needs the actor's name and email.

```python
def _model_user_mapper(model) -> User:
    return User(
        id=model.id,
        name=Name(
            first_name=model.first_name,
            last_name=model.last_name,
            preferred_name=model.preferred_name,
        ),
        email=str(model.email),
    )


def model_entity_with_actors_mapper(model: {Entity}Model) -> {Entity}:
    return mapper.to({Entity}).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "created_by": _model_user_mapper(model.creator),
            "updated_by": _model_user_mapper(model.updater),
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )
```

Keep both variants. Using the `_with_actors` mapper on a row that was not eager-loaded raises a
lazy-load error under async SQLAlchemy.

## Rows to entity list

```python
def models_{entity}_list_mapper(rows: list) -> {Entity}List:
    """Convert window-function rows [(Model, total), ...] into a {Entity}List."""
    return {Entity}List(
        items=[model_entity_mapper(row[0]) for row in rows],
        total=rows[0][1] if rows else 0,
    )
```

The `if rows else 0` guard matters: an empty page must yield `total=0`, not an `IndexError`.

## Entity to model

```python
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
```

Nested entities flatten back to their ids. A transient secret must never appear here.

## Reserved metadata bridge

The model renames the attribute; the entity keeps `metadata`. Reference: `notification`.

```python
# Model → Entity
"metadata": model.{module}_metadata,

# Entity → Model
"{module}_metadata": entity.metadata,
```

## Value objects

`Email` and `Phone` flatten to strings; the structured `Name` flattens to its parts.

```python
# Entity → Model
"first_name": entity.name.first_name,
"last_name": entity.name.last_name,
"preferred_name": entity.name.preferred_name,
"email": str(entity.email),
"phone": str(entity.phone) if entity.phone else None,

# Model → Entity
"name": Name(
    first_name=model.first_name,
    last_name=model.last_name,
    preferred_name=model.preferred_name,
),
"email": str(model.email),   # the entity's __post_init__ converts str → Email
"phone": str(model.phone) if model.phone else None,
```

Handing the raw string to the entity is preferred for single-value objects — it re-validates on
every load, so a row that predates a rule change fails loudly instead of silently.

## Cache serializers

The `# ENTITY / CACHE` section. Plain `json.dumps` / `json.loads`, not automapper.

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

`is_active` is `init=False` on `BaseEntity`, so it is assigned after construction. Round-trip every
field the consumer reads, and bump `REDIS_CACHE_VERSION` whenever this payload changes.
