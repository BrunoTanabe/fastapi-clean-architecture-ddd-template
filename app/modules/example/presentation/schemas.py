import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


# REQUEST
class ExampleRequest(BaseModel):
    first_name: str = Field(
        title="Individual's first name (Required)",
        description="First name to receive 'Hello' in the response. Must be a valid name.",
        min_length=3,
        examples=["John", "Jane"],
        json_schema_extra={
            "example": "John",
            "writeOnly": True,
        },
    )

    last_name: str = Field(
        title="Individual's last name (Required)",
        description="Last name to receive 'Hello' in the response. Must be a valid name.",
        min_length=3,
        examples=["Doe", "Smith"],
        json_schema_extra={
            "example": "Doe",
            "writeOnly": True,
        },
    )

    @field_validator("first_name")
    def validate_first_name(cls, request: str) -> str:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", request):
            raise ValueError(
                "First name must contain only letters, spaces, apostrophes, and hyphens."
            )
        return request.strip()

    @field_validator("last_name")
    def validate_last_name(cls, request: str) -> str:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", request):
            raise ValueError(
                "Last name must contain only letters, spaces, apostrophes, and hyphens."
            )
        return request.strip()

    model_config = ConfigDict(
        title="ExampleRequest",
        str_strip_whitespace=True,
        str_min_length=3,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Example schema for the request to analyze infractions.",
            "example": {
                "first_name": "John",
                "last_name": "Doe",
            },
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                },
                {
                    "first_name": "Jane",
                    "last_name": "Smith",
                },
            ],
        },
    )


# RESPONSE
class ExampleResponse(BaseModel):
    message: str = Field(
        title="Response message (Required)",
        description="Message to be returned in the response, greeting the individual.",
        min_length=3,
        examples=["Hello, John Doe!", "Hello, Jane Smith!"],
        json_schema_extra={
            "example": "Hello John Doe!",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="ExampleResponse",
        str_strip_whitespace=True,
        str_min_length=3,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Example schema for the response of analyzing infractions.",
            "example": {
                "message": "Hello, John Doe!",
            },
            "examples": [
                {
                    "message": "Hello, John Doe!",
                },
                {
                    "message": "Hello, Jane Smith!",
                },
            ],
        },
    )
