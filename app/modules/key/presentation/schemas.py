from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.modules.key.domain.enums import KeyExpiration, KeySortField
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN
from app.modules.shared.presentation.schemas import (
    PaginationMeta,
    PaginationParams,
)


# REQUEST
class CreateRequest(BaseModel):
    name: str = Field(
        title="Key Name (Required)",
        description="A human-readable name to identify the API key.",
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
        title="Key Description (Optional)",
        description="An optional description of what the API key is used for.",
        max_length=1000,
        examples=["Used by the CI pipeline to publish releases.", None],
        json_schema_extra={
            "example": "Used by the CI pipeline to publish releases.",
            "writeOnly": True,
        },
    )

    expires_in: KeyExpiration = Field(
        title="Expiration (Required)",
        description=(
            "The validity period of the API key, chosen from a fixed set of presets. "
            f"Allowed values: {', '.join([choice.value for choice in KeyExpiration])}. "
            f"Use '{KeyExpiration.NEVER.value}' for a key that never expires."
        ),
        examples=[KeyExpiration.THIRTY_DAYS.value, KeyExpiration.NEVER.value],
        json_schema_extra={
            "example": KeyExpiration.THIRTY_DAYS.value,
            "writeOnly": True,
        },
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, request: str) -> str:
        if not RESOURCE_NAME_PATTERN.match(request):
            raise ValueError(
                "Key name must contain only letters, numbers, spaces, hyphens, and underscores."
            )
        return request

    @field_validator("description")
    @classmethod
    def validate_description(cls, request: str | None) -> str | None:
        if isinstance(request, str) and request.strip() == "":
            return None
        return request

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Request model for creating a new API key.",
            "example": {
                "name": "CI pipeline",
                "description": "Used by the CI pipeline to publish releases.",
                "expires_in": KeyExpiration.THIRTY_DAYS.value,
            },
            "examples": [
                {
                    "name": "CI pipeline",
                    "description": "Used by the CI pipeline to publish releases.",
                    "expires_in": KeyExpiration.THIRTY_DAYS.value,
                },
                {
                    "name": "Partner integration",
                    "description": None,
                    "expires_in": KeyExpiration.NEVER.value,
                },
            ],
        },
    )


class UpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        title="Key Name (Optional)",
        description="The new human-readable name of the API key.",
        min_length=3,
        max_length=255,
        examples=["CI pipeline", None],
        json_schema_extra={
            "example": "CI pipeline",
            "writeOnly": True,
        },
    )

    description: str | None = Field(
        default=None,
        title="Key Description (Optional)",
        description="The new description of the API key. Pass null to clear it.",
        max_length=1000,
        examples=["Used by the CI pipeline to publish releases.", None],
        json_schema_extra={
            "example": "Used by the CI pipeline to publish releases.",
            "writeOnly": True,
        },
    )

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> UpdateRequest:
        has_name = "name" in self.model_fields_set and self.name is not None
        has_description = "description" in self.model_fields_set
        if not has_name and not has_description:
            raise ValueError(
                "At least one field must be provided. "
                "Pass a non-null name, or pass description (null to clear it)."
            )
        return self

    @field_validator("name")
    @classmethod
    def validate_name(cls, request: str | None) -> str | None:
        if request is not None and not RESOURCE_NAME_PATTERN.match(request):
            raise ValueError(
                "Key name must contain only letters, numbers, spaces, hyphens, and underscores."
            )
        return request

    @field_validator("description")
    @classmethod
    def validate_description(cls, request: str | None) -> str | None:
        if isinstance(request, str) and request.strip() == "":
            return None
        return request

    model_config = ConfigDict(
        title="UpdateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Request model for updating an existing API key.",
            "example": {
                "name": "CI pipeline",
                "description": "Used by the CI pipeline to publish releases.",
            },
            "examples": [
                {
                    "name": "CI pipeline",
                    "description": "Used by the CI pipeline to publish releases.",
                },
                {"name": "CI pipeline"},
                {"description": "Updated description."},
            ],
        },
    )


# RESPONSE
class CreateKeyResponse(BaseModel):
    api_key: str = Field(
        title="API Key Secret (Required)",
        description="The full raw API key. This is the only time it is ever returned — store it securely.",
        examples=["tk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5aB3d"],
        json_schema_extra={
            "example": "tk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5aB3d",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="CreateKeyResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for a successful API key creation. Carries the raw secret exactly once.",
            "example": {
                "api_key": "tk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5aB3d",
            },
            "examples": [
                {
                    "api_key": "tk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5aB3d",
                },
                {
                    "api_key": "tk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5K4j",
                },
            ],
        },
    )


class RotateKeyResponse(BaseModel):
    api_key: str = Field(
        title="Rotated API Key Secret (Required)",
        description="The newly generated raw API key. The previous secret stops working immediately and this value is never returned again — store it securely.",
        examples=["tk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5K4j"],
        json_schema_extra={
            "example": "tk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5K4j",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="RotateKeyResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for a successful API key rotation. Carries the new raw secret exactly once; the previous one is revoked.",
            "example": {
                "api_key": "tk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5K4j",
            },
            "examples": [
                {
                    "api_key": "tk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5K4j",
                },
                {
                    "api_key": "tk_live_q4w5e6r7t8y9u0i1o2p3a4s5d6f7g8H9j",
                },
            ],
        },
    )


# PAGINATION
class KeyPaginationParams:
    def __init__(
        self,
        pagination: Annotated[PaginationParams, Depends()],
        sort_by: KeySortField = Query(default=KeySortField.CREATED_AT),
    ):
        self.sort_order = pagination.sort_order.value
        self.page = pagination.page
        self.limit = pagination.limit
        self.offset = pagination.offset
        self.sort_by = sort_by


# RESPONSE
class KeyListItem(BaseModel):
    id: UUID = Field(
        title="Key Identifier (Required)",
        description="The unique identifier of the API key.",
        examples=["3f2504e0-4f89-11d3-9a0c-0305e82c3301"],
        json_schema_extra={
            "example": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
            "readOnly": True,
        },
    )

    name: str = Field(
        title="Key Name (Required)",
        description="The human-readable name of the API key.",
        examples=["CI pipeline", "Partner integration"],
        json_schema_extra={
            "example": "CI pipeline",
            "readOnly": True,
        },
    )

    description: str | None = Field(
        title="Key Description (Optional)",
        description="The description of what the API key is used for.",
        examples=["Used by the CI pipeline to publish releases.", None],
        json_schema_extra={
            "example": "Used by the CI pipeline to publish releases.",
            "readOnly": True,
        },
    )

    created_at: datetime = Field(
        title="Created At (Required)",
        description="The date and time when the API key was created.",
        examples=["2026-07-15T10:30:00Z"],
        json_schema_extra={
            "example": "2026-07-15T10:30:00Z",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="KeyListItem",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "An API key list item.",
            "example": {
                "id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                "name": "CI pipeline",
                "description": "Used by the CI pipeline to publish releases.",
                "created_at": "2026-07-15T10:30:00Z",
            },
        },
    )


class ActorResponse(BaseModel):
    email: str = Field(
        title="Actor Email (Required)",
        description="The email address of the user.",
        examples=["johndoe@email.com"],
        json_schema_extra={
            "example": "johndoe@email.com",
            "readOnly": True,
        },
    )

    preferred_name: str = Field(
        title="Actor Preferred Name (Required)",
        description="The preferred name of the user.",
        examples=["John"],
        json_schema_extra={
            "example": "John",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="ActorResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "The identity of a user who acted on the resource.",
            "example": {
                "email": "johndoe@email.com",
                "preferred_name": "John",
            },
        },
    )


class GetResponse(BaseModel):
    id: UUID = Field(
        title="Key Identifier (Required)",
        description="The unique identifier of the API key.",
        examples=["3f2504e0-4f89-11d3-9a0c-0305e82c3301"],
        json_schema_extra={
            "example": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
            "readOnly": True,
        },
    )

    name: str = Field(
        title="Key Name (Required)",
        description="The human-readable name of the API key.",
        examples=["CI pipeline", "Partner integration"],
        json_schema_extra={
            "example": "CI pipeline",
            "readOnly": True,
        },
    )

    description: str | None = Field(
        title="Key Description (Optional)",
        description="The description of what the API key is used for.",
        examples=["Used by the CI pipeline to publish releases.", None],
        json_schema_extra={
            "example": "Used by the CI pipeline to publish releases.",
            "readOnly": True,
        },
    )

    prefix: str = Field(
        title="Key Prefix (Required)",
        description="The public, non-secret prefix used to identify the key.",
        examples=["iap_"],
        json_schema_extra={
            "example": "iap_",
            "readOnly": True,
        },
    )

    last_four: str = Field(
        title="Last Four (Required)",
        description="The last four characters of the raw key, for masked display.",
        examples=["aB3d"],
        json_schema_extra={
            "example": "aB3d",
            "readOnly": True,
        },
    )

    expires_at: datetime | None = Field(
        title="Expiration (Optional)",
        description="The expiration timestamp of the key, or null if it never expires.",
        examples=["2027-01-01T00:00:00Z", None],
        json_schema_extra={
            "example": "2027-01-01T00:00:00Z",
            "readOnly": True,
        },
    )

    last_used_at: datetime | None = Field(
        title="Last Used At (Optional)",
        description="The timestamp of the last time the key was used to authenticate, or null if never used.",
        examples=["2026-07-15T10:30:00Z", None],
        json_schema_extra={
            "example": None,
            "readOnly": True,
        },
    )

    created_by: ActorResponse = Field(
        title="Created By (Required)",
        description="The email and preferred name of the user who created the key.",
        examples=[{"email": "johndoe@email.com", "preferred_name": "John"}],
    )

    updated_by: ActorResponse = Field(
        title="Updated By (Required)",
        description="The email and preferred name of the user who last updated the key.",
        examples=[{"email": "johndoe@email.com", "preferred_name": "John"}],
    )

    created_at: datetime = Field(
        title="Created At (Required)",
        description="The date and time when the API key was created.",
        examples=["2026-07-15T10:30:00Z"],
        json_schema_extra={
            "example": "2026-07-15T10:30:00Z",
            "readOnly": True,
        },
    )

    updated_at: datetime = Field(
        title="Updated At (Required)",
        description="The date and time when the API key was last updated.",
        examples=["2026-07-15T10:30:00Z"],
        json_schema_extra={
            "example": "2026-07-15T10:30:00Z",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="GetResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model with the stored data of a single active API key (the secret hash is never exposed).",
            "example": {
                "id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                "name": "CI pipeline",
                "description": "Used by the CI pipeline to publish releases.",
                "prefix": "iap_",
                "last_four": "aB3d",
                "expires_at": "2027-01-01T00:00:00Z",
                "last_used_at": None,
                "created_by": {
                    "email": "johndoe@email.com",
                    "preferred_name": "John",
                },
                "updated_by": {
                    "email": "johndoe@email.com",
                    "preferred_name": "John",
                },
                "created_at": "2026-07-15T10:30:00Z",
                "updated_at": "2026-07-15T10:30:00Z",
            },
        },
    )


class GetAllResponse(BaseModel):
    message: str = ResponseMessages.RETRIEVED.value
    api_keys: list[KeyListItem]
    pagination: PaginationMeta

    model_config = ConfigDict(
        title="GetAllResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for retrieving all API keys.",
            "example": {
                "api_keys": [
                    {
                        "id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                        "name": "CI pipeline",
                        "description": "Used by the CI pipeline to publish releases.",
                        "created_at": "2026-07-15T10:30:00Z",
                    }
                ],
                "pagination": {
                    "total": 1,
                    "page": 1,
                    "limit": 20,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False,
                },
            },
        },
    )
