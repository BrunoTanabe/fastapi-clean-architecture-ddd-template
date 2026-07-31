# Schema Templates

## Contents

- [Create request](#create-request)
- [Partial-update request](#partial-update-request)
- [Shared CRUD responses](#shared-crud-responses)
- [One-time secret response](#one-time-secret-response)
- [Actor projection](#actor-projection)
- [Detail response](#detail-response)
- [Paginated list response](#paginated-list-response)
- [Pagination params](#pagination-params)
- [Enum query field](#enum-query-field)

## Create request

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateRequest(BaseModel):
    name: str = Field(
        title="{Entity} Name (Required)",
        description="A human-readable name to identify the {entity}.",
        min_length=3,
        max_length=255,
        examples=["CI pipeline", "Partner integration"],
        json_schema_extra={
            "example": "CI pipeline",
            "writeOnly": True,
        },
    )

    description: str | None = Field(
        default=None,
        title="{Entity} Description (Optional)",
        description="An optional description of what the {entity} is used for.",
        max_length=1000,
        examples=["Used by the CI pipeline to publish releases.", None],
        json_schema_extra={
            "example": "Used by the CI pipeline to publish releases.",
            "writeOnly": True,
        },
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not RESOURCE_NAME_PATTERN.match(value):
            raise ValueError(
                "Name must contain only letters, numbers, spaces, hyphens, and underscores."
            )
        return value

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Payload for creating a new {entity}.",
            "example": {
                "name": "CI pipeline",
                "description": "Used by the CI pipeline to publish releases.",
            },
        },
    )
```

## Partial-update request

Every field optional with `default=None`. The mapper distinguishes omitted from explicitly null
through `model_fields_set`, so the schema must not try to encode that difference.

```python
from pydantic import model_validator


class UpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        title="{Entity} Name (Optional)",
        description="A new name for the {entity}. Omit to leave it unchanged.",
        min_length=3,
        max_length=255,
        examples=["Renamed pipeline"],
        json_schema_extra={"example": "Renamed pipeline", "writeOnly": True},
    )

    description: str | None = Field(
        default=None,
        title="{Entity} Description (Optional)",
        description="A new description. Send null to clear it, or omit to leave it unchanged.",
        max_length=1000,
        examples=["Updated description", None],
        json_schema_extra={"example": "Updated description", "writeOnly": True},
    )

    @model_validator(mode="after")
    @classmethod
    def validate_at_least_one_field(cls, values):
        if not values.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return values

    model_config = ConfigDict(
        title="UpdateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Payload for partially updating a {entity}.",
            "example": {"name": "Renamed pipeline"},
        },
    )
```

Document the omit-versus-null distinction in the field `description` — it is the only place a
client learns how to clear a value.

## Shared CRUD responses

```python
from app.modules.shared.presentation.schemas import (
    CreateResponse,
    DeleteResponse,
    UpdateResponse,
)
```

Import them. A module only writes its own response class when it returns more than a message.

## One-time secret response

The raw secret is returned exactly once, on create and on rotate. Reference: `CreateKeyResponse`.

```python
class Create{Entity}Response(BaseModel):
    message: str = ResponseMessages.CREATED.value

    api_key: str = Field(
        title="API Key (Returned Once)",
        description=(
            "The generated secret. This is the only time it is returned — "
            "store it securely, it cannot be retrieved again."
        ),
        examples=["sk_live_9f2c…"],
        json_schema_extra={"example": "sk_live_9f2c…", "readOnly": True},
    )

    model_config = ConfigDict(
        title="Create{Entity}Response",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response returned after creating a {entity}, including the one-time secret.",
            "example": {"message": ResponseMessages.CREATED.value, "api_key": "sk_live_9f2c…"},
        },
    )
```

Say "returned once" in the description. Never add the secret to any other response, and never to a
list item.

## Actor projection

A compact view of a related user, instead of exposing the raw FK. Reference: `ActorResponse`.

```python
class ActorResponse(BaseModel):
    email: str = Field(
        title="Email",
        description="Email address of the user.",
        examples=["person@example.com"],
        json_schema_extra={"example": "person@example.com", "readOnly": True},
    )

    preferred_name: str = Field(
        title="Preferred Name",
        description="Preferred display name of the user.",
        examples=["Alex"],
        json_schema_extra={"example": "Alex", "readOnly": True},
    )

    model_config = ConfigDict(
        title="ActorResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Compact representation of the user who acted on the resource.",
            "example": {"email": "person@example.com", "preferred_name": "Alex"},
        },
    )
```

The repository must `joinedload` the relationship for this to be populated — see
`/create-repository-method`.

## Detail response

```python
from datetime import datetime
from uuid import UUID


class GetResponse(BaseModel):
    message: str = ResponseMessages.RETRIEVED.value

    id: UUID = Field(
        title="Identifier",
        description="Unique identifier of the {entity}.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
        json_schema_extra={
            "example": "550e8400-e29b-41d4-a716-446655440000",
            "readOnly": True,
        },
    )

    name: str = Field(
        title="Name",
        description="Human-readable name of the {entity}.",
        examples=["CI pipeline"],
        json_schema_extra={"example": "CI pipeline", "readOnly": True},
    )

    created_by: ActorResponse = Field(
        title="Created By",
        description="The user who created the {entity}.",
        json_schema_extra={"readOnly": True},
    )

    created_at: datetime = Field(
        title="Created At",
        description="Timestamp of when the {entity} was created.",
        examples=["2026-01-15T10:30:00Z"],
        json_schema_extra={"example": "2026-01-15T10:30:00Z", "readOnly": True},
    )

    model_config = ConfigDict(
        title="GetResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Full representation of a single {entity}.",
            "example": {
                "message": ResponseMessages.RETRIEVED.value,
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "CI pipeline",
                "created_by": {"email": "person@example.com", "preferred_name": "Alex"},
                "created_at": "2026-01-15T10:30:00Z",
            },
        },
    )
```

## Paginated list response

The list item is a compact projection — not the detail response. A list endpoint must not carry
every field of every row.

```python
from app.modules.shared.presentation.schemas import PaginationMeta


class {Entity}ListItem(BaseModel):
    id: UUID = Field(...)
    name: str = Field(...)
    created_at: datetime = Field(...)

    model_config = ConfigDict(
        title="{Entity}ListItem",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={"description": "Compact representation of a {entity} in a list."},
    )


class GetAllResponse(BaseModel):
    message: str = ResponseMessages.RETRIEVED.value
    items: list[{Entity}ListItem]
    pagination: PaginationMeta

    model_config = ConfigDict(
        title="GetAllResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Paginated list of {entity} records.",
            "example": {
                "message": ResponseMessages.RETRIEVED.value,
                "items": [],
                "pagination": {
                    "total": 0,
                    "page": 1,
                    "limit": 20,
                    "total_pages": 0,
                    "has_next": False,
                    "has_prev": False,
                },
            },
        },
    )
```

The collection field may be named for the resource (`api_keys` in `key`) rather than `items` —
match whatever the module's mapper produces.

## Pagination params

A callable class, not a `BaseModel`. It composes the shared `PaginationParams` and adds `sort_by`.

```python
from typing import Annotated

from fastapi import Depends, Query

from app.modules.shared.presentation.schemas import PaginationParams
from app.modules.{module}.domain.enums import {Entity}SortField


class {Entity}PaginationParams:
    def __init__(
        self,
        pagination: Annotated[PaginationParams, Depends()],
        sort_by: {Entity}SortField = Query(
            default={Entity}SortField.CREATED_AT,
            title="Sort Field",
            description=(
                "Field to sort the results by. Allowed values: "
                f"{', '.join([field.value for field in {Entity}SortField])}."
            ),
            examples=[{Entity}SortField.CREATED_AT.value],
        ),
    ):
        self.sort_order = pagination.sort_order
        self.page = pagination.page
        self.limit = pagination.limit
        self.offset = pagination.offset
        self.sort_by = sort_by
```

Copy all four shared attributes across — the mapper reads them by name.

## Enum query field

```python
expires_in: {Entity}Expiration = Field(
    title="Expiration (Required)",
    description=(
        "The validity period, chosen from a fixed set of presets. "
        f"Allowed values: {', '.join([choice.value for choice in {Entity}Expiration])}. "
        f"Use '{{Entity}Expiration.NEVER.value}' for one that never expires."
    ),
    examples=[{Entity}Expiration.THIRTY_DAYS.value, {Entity}Expiration.NEVER.value],
    json_schema_extra={
        "example": {Entity}Expiration.THIRTY_DAYS.value,
        "writeOnly": True,
    },
)
```

Build the allowed-values list from the enum so it can never drift from the code.
