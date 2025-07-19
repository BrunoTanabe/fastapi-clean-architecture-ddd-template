import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExampleRequest(BaseModel):
    name: str = Field(
        title="Individual's name (Required)",
        description="Name to receive 'Hello' in the response. Must be a valid name.",
        min_length=3,
        examples=["Bruno Tanabe", "João da Silva"],
        json_schema_extra={
            "example": "Bruno Tanabe",
            "writeOnly": True,
        },
    )

    @field_validator("name")
    def validate_name(cls, request: str) -> str:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+$", request):
            raise ValueError(
                "Name must contain only letters, spaces, apostrophes, and hyphens."
            )
        return request.strip()

    model_config = ConfigDict(
        title="ExampleRequest",
        str_strip_whitespace=True,
        str_to_lower=True,
        str_min_length=3,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Example schema for the request to analyze infractions.",
            "example": {
                "name": "Bruno Tanabe",
            },
            "examples": [
                {
                    "name": "Bruno Tanabe",
                },
                {
                    "name": "João da Silva",
                },
                {
                    "name": "Maria Oliveira",
                },
            ],
        },
    )


class ExampleResponse(BaseModel):
    message: str = Field(
        title="Response message (Required)",
        description="Message to be returned in the response, greeting the individual.",
        min_length=3,
        pattern=r"^Hello\s[A-Za-zÀ-ÖØ-öø-ÿ\s'-]+!$",
        examples=["Hello Bruno Tanabe!", "Hello João da Silva!"],
        json_schema_extra={
            "example": "Hello Bruno Tanabe!",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="ExampleResponse",
        str_strip_whitespace=True,
        str_to_lower=True,
        str_min_length=3,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Example schema for the response of analyzing infractions.",
            "example": {
                "message": "Hello Bruno Tanabe!",
            },
            "examples": [
                {
                    "message": "Hello Bruno Tanabe!",
                },
                {
                    "message": "Hello João da Silva!",
                },
                {
                    "message": "Hello Maria Oliveira!",
                },
            ],
        },
    )
