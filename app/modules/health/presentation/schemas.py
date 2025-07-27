from pydantic import BaseModel, Field, ConfigDict

from app.modules.health.application.enums import HealthType


class HealthCheckResponse(BaseModel):
    status: HealthType = Field(
        title="Health Status",
        description=f"Indicates the health status of the system. Possible values are: {', '.join(HealthType.choices())}.",
        examples=[HealthType.choices()],
        json_schema_extra={
            "example": HealthType.OK,
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="HealthCheckResponse",
        str_strip_whitespace=True,
        str_to_lower=True,
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
