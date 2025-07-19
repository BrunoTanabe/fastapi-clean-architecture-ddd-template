from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field, ConfigDict


T = TypeVar("T")


class StandardDetailsResponse(BaseModel, Generic[T]):
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

    data: Optional[T] = Field(
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
        str_to_lower=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Standard details response schema for API endpoints, including a message and optional data.",
            "example": {
                "message": "Process completed successfully.",
                "data": {"key": "value"},
            },
            "examples": [
                {
                    "message": "Unable to process the request.",
                    "data": {"field": "Error message for the field."},
                },
                {
                    "message": "Process completed successfully.",
                    "data": {"key": "value", "another_key": 123},
                },
            ],
        },
    )


class StandardResponse(BaseModel, Generic[T]):
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
                "message": "Request processed successfully.",
                "data": {"key": "value"},
            },
            {
                "message": "Unable to process the request.",
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
        str_to_lower=True,
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
                    "message": "Request processed successfully.",
                    "data": {"key": "value"},
                },
            },
        },
    )
