from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.knowledge.domain.enums import KnowledgeSortField
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.domain.value_objects import RESOURCE_NAME_PATTERN
from app.modules.shared.presentation.schemas import (
    PaginationMeta,
    PaginationParams,
)


# REQUEST
class CreateRequest(BaseModel):
    name: str = Field(
        title="Name (Required)",
        description="The unique name of the knowledge base.",
        min_length=3,
        max_length=255,
        examples=["Machine Learning Fundamentals", "Python Best Practices"],
        json_schema_extra={
            "example": "Machine Learning Fundamentals",
            "writeOnly": True,
        },
    )

    description: str | None = Field(
        default=None,
        title="Description (Optional)",
        description="A detailed description of the knowledge base.",
        examples=[
            "A collection of resources on machine learning fundamentals.",
            None,
        ],
        json_schema_extra={
            "example": "A collection of resources on machine learning fundamentals.",
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

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    model_config = ConfigDict(
        title="CreateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Request model for creating a new knowledge base.",
            "example": {
                "name": "Machine Learning Fundamentals",
                "description": "A collection of resources on machine learning fundamentals.",
            },
            "examples": [
                {
                    "name": "Machine Learning Fundamentals",
                    "description": "A collection of resources on machine learning fundamentals.",
                },
                {
                    "name": "Python Best Practices",
                    "description": None,
                },
            ],
        },
    )


class UpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        title="Name (Optional)",
        description="The new unique name of the knowledge base.",
        min_length=3,
        max_length=255,
        examples=["Machine Learning Fundamentals", None],
        json_schema_extra={
            "example": "Machine Learning Fundamentals",
            "writeOnly": True,
        },
    )

    description: str | None = Field(
        default=None,
        title="Description (Optional)",
        description="The new description of the knowledge base. Pass null to clear it.",
        examples=["A collection of resources on machine learning fundamentals.", None],
        json_schema_extra={
            "example": "A collection of resources on machine learning fundamentals.",
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
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None and not RESOURCE_NAME_PATTERN.match(value):
            raise ValueError(
                "Name must contain only letters, numbers, spaces, hyphens, and underscores."
            )
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    model_config = ConfigDict(
        title="UpdateRequest",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Request model for updating an existing knowledge base.",
            "example": {
                "name": "Machine Learning Fundamentals",
                "description": "A collection of resources on machine learning fundamentals.",
            },
            "examples": [
                {
                    "name": "Machine Learning Fundamentals",
                    "description": "A collection of resources on machine learning fundamentals.",
                },
                {"name": "Machine Learning Fundamentals"},
                {"description": "Updated description."},
            ],
        },
    )


class KnowledgePaginationParams:
    def __init__(
        self,
        pagination: Annotated[PaginationParams, Depends()],
        sort_by: KnowledgeSortField = Query(default=KnowledgeSortField.UPDATED_AT),
    ):
        self.sort_order = pagination.sort_order.value
        self.page = pagination.page
        self.limit = pagination.limit
        self.offset = pagination.offset
        self.sort_by = sort_by


# RESPONSE
class KnowledgeListItem(BaseModel):
    id: UUID = Field(
        title="ID",
        description="The unique identifier of the knowledge base.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    name: str = Field(
        title="Name",
        description="The name of the knowledge base.",
        examples=["Machine Learning Fundamentals"],
    )

    description: str | None = Field(
        title="Description",
        description="A detailed description of the knowledge base.",
        examples=["A collection of resources on machine learning fundamentals.", None],
    )

    updated_at: datetime = Field(
        title="Updated At",
        description="The timestamp of the last update to the knowledge base.",
        examples=["2025-01-15T10:30:00Z"],
    )

    model_config = ConfigDict(
        title="KnowledgeListItem",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "A knowledge base list item.",
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Machine Learning Fundamentals",
                "description": "A collection of resources on machine learning fundamentals.",
                "updated_at": "2025-01-15T10:30:00Z",
            },
        },
    )


class GetAllResponse(BaseModel):
    message: str = ResponseMessages.RETRIEVED.value
    knowledge_bases: list[KnowledgeListItem]
    pagination: PaginationMeta

    model_config = ConfigDict(
        title="GetAllResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for retrieving all knowledge bases.",
            "example": {
                "knowledge_bases": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Machine Learning Fundamentals",
                        "description": "A collection of resources on machine learning fundamentals.",
                        "updated_at": "2025-01-15T10:30:00Z",
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
