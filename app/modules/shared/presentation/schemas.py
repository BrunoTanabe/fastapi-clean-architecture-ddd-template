from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

from app.modules.shared.domain.enums import ResponseMessages, SortOrder


class StandardDetailsResponse[T](BaseModel):
    message: str = Field(
        title="Response message",
        description="A brief, human-readable summary of the response.",
        examples=["Process completed successfully.", "Unable to process the request."],
        min_length=1,
        json_schema_extra={
            "example": "Unable to process the request.",
            "writeOnly": True,
        },
    )

    data: T | None = Field(
        title="Additional data (optional)",
        description="A JSON object containing additional context or details about the response.",
        examples=[{"field": "value"}, {}, {"key": "value", "another_key": 123}],
        json_schema_extra={
            "example": {"field": "value"},
            "writeOnly": True,
        },
    )

    model_config = ConfigDict(
        title="StandardDetailsResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Standard details response schema for API endpoints, including a message and optional data.",
            "example": {
                "message": ResponseMessages.SUCCESS.value,
                "data": {"key": "value"},
            },
            "examples": [
                {
                    "message": ResponseMessages.VALIDATION_ERROR.value,
                    "data": {"field": "Error message for the field."},
                },
                {
                    "message": ResponseMessages.SUCCESS.value,
                    "data": {"key": "value", "another_key": 123},
                },
            ],
        },
    )


class StandardResponse[T](BaseModel):
    code: int = Field(
        title="HTTP status code (required)",
        description="Numeric HTTP status code indicating the response type.",
        ge=100,
        le=599,
        examples=[200, 400, 404, 500],
        json_schema_extra={
            "example": 200,
            "writeOnly": True,
        },
    )

    method: str = Field(
        title="HTTP method (required)",
        description="The HTTP method used in the request.",
        pattern="^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)$",
        examples=["DELETE", "GET", "POST", "PUT"],
        json_schema_extra={
            "example": "GET",
            "writeOnly": True,
        },
    )

    path: str = Field(
        title="Request path (required)",
        description="The URI path of the endpoint.",
        min_length=1,
        pattern="^/.*$",
        examples=["/api/v1/resource", "/api/v2/example"],
        json_schema_extra={
            "example": "/api/v1/resource",
            "writeOnly": True,
        },
    )

    timestamp: str = Field(
        title="Timestamp (required)",
        description="ISO 8601 formatted date-time string when the response was generated.",
        examples=["2024-05-01T12:00:00Z", "2024-05-01T15:30:00+00:00"],
        json_schema_extra={
            "example": "2024-05-01T12:00:00Z",
            "writeOnly": True,
        },
    )

    details: StandardDetailsResponse[T] = Field(
        title="Response details (optional)",
        description="Detailed information payload for success or error responses.",
        default_factory=lambda: StandardDetailsResponse[T](
            message="Request processed successfully.",
            data={},
        ),
        examples=[
            {
                "message": ResponseMessages.SUCCESS.value,
                "data": {"key": "value"},
            },
            {
                "message": ResponseMessages.VALIDATION_ERROR.value,
                "data": {"field": "Error message for the field."},
            },
        ],
        json_schema_extra={
            "example": {
                "message": "Request processed successfully.",
                "data": {"key": "value"},
            },
            "writeOnly": True,
        },
    )

    model_config = ConfigDict(
        title="StandardResponse",
        str_strip_whitespace=True,
        str_min_length=1,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Standard response schema for API endpoints, including HTTP status code, method, path, timestamp, and details.",
            "example": {
                "code": 200,
                "method": "GET",
                "path": "/api/v1/resource",
                "timestamp": "2024-05-01T12:00:00Z",
                "details": {
                    "message": ResponseMessages.SUCCESS.value,
                    "data": {"key": "value"},
                },
            },
        },
    )


# PAGINATION
# Built from the enum so the documented values can never drift from the code.
_SORT_ORDER_VALUES = ", ".join([order.value for order in SortOrder])


class PaginationParams:
    def __init__(
        self,
        sort_order: SortOrder = Query(
            title="Sort Order",
            description=f"The order in which to sort the results. Allowed values are: {_SORT_ORDER_VALUES}.",
            examples=[SortOrder.ASC.value, SortOrder.DESC.value],
            default=SortOrder.DESC,
        ),
        page: int = Query(
            default=1,
            ge=1,
            title="Page Number",
            description="The page number to retrieve (1-indexed).",
            examples=[1, 2, 5],
        ),
        limit: int = Query(
            default=20,
            ge=1,
            le=100,
            title="Page Size",
            description="Number of items to return per page. Maximum is 100.",
            examples=[10, 20, 50],
        ),
    ):
        self.sort_order = sort_order
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit


class PaginationMeta(BaseModel):
    total: int = Field(
        title="Total Items",
        description="Total number of items matching the query.",
        ge=0,
        examples=[100, 0, 87],
        json_schema_extra={"example": 100},
    )

    page: int = Field(
        title="Current Page",
        description="The current page number (1-indexed).",
        ge=1,
        examples=[1, 2, 5],
        json_schema_extra={"example": 1},
    )

    limit: int = Field(
        title="Page Size",
        description="Number of items per page.",
        ge=1,
        examples=[10, 20, 50],
        json_schema_extra={"example": 20},
    )

    total_pages: int = Field(
        title="Total Pages",
        description="Total number of pages available for the current query.",
        ge=0,
        examples=[1, 5, 10],
        json_schema_extra={"example": 5},
    )

    has_next: bool = Field(
        title="Has Next Page",
        description="Indicates whether a next page is available.",
        examples=[True, False],
        json_schema_extra={"example": True},
    )

    has_prev: bool = Field(
        title="Has Previous Page",
        description="Indicates whether a previous page is available.",
        examples=[False, True],
        json_schema_extra={"example": False},
    )

    model_config = ConfigDict(
        title="PaginationMeta",
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Pagination metadata returned alongside list responses.",
            "example": {
                "total": 87,
                "page": 2,
                "limit": 20,
                "total_pages": 5,
                "has_next": True,
                "has_prev": True,
            },
        },
    )


# CRUD RESPONSES
class CreateResponse(BaseModel):
    message: str = ResponseMessages.CREATED.value

    model_config = ConfigDict(
        title="CreateResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for a successful resource creation.",
            "example": {"message": ResponseMessages.CREATED.value},
        },
    )


class UpdateResponse(BaseModel):
    message: str = ResponseMessages.UPDATED.value

    model_config = ConfigDict(
        title="UpdateResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for a successful resource update.",
            "example": {"message": ResponseMessages.UPDATED.value},
        },
    )


class DeleteResponse(BaseModel):
    message: str = ResponseMessages.DELETED.value

    model_config = ConfigDict(
        title="DeleteResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for a successful resource deletion.",
            "example": {"message": ResponseMessages.DELETED.value},
        },
    )
