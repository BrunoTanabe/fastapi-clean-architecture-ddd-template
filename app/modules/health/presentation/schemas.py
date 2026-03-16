from pydantic import BaseModel, Field, ConfigDict

from app.modules.health.application.enums import HealthType


# RESPONSE
class HealthResponse(BaseModel):
    status: HealthType = Field(
        title="Health Status",
        description=f"Indicates the health status of the system. Possible values are: {', '.join(health_type.value for health_type in HealthType)}",
        examples=[HealthType.OK.value, HealthType.ERROR.value],
        json_schema_extra={
            "example": HealthType.OK,
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="HealthResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for health check endpoint.",
            "example": {
                "status": HealthType.OK,
            },
            "examples": [
                {
                    "status": HealthType.OK,
                },
                {
                    "status": HealthType.ERROR,
                },
            ],
        },
    )


class AlembicVersionResponse(BaseModel):
    version: str = Field(
        title="Alembic Version",
        description="The current Alembic migration version of the database.",
        examples=["ae1027a6acf"],
        json_schema_extra={
            "example": "ae1027a6acf",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="AlembicResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for Alembic version endpoint.",
            "example": {
                "version": "ae1027a6acf",
            },
            "examples": [
                {
                    "version": "ae1027a6acf",
                },
                {
                    "version": "b1c2d3e4f5g6",
                },
            ],
        },
    )
