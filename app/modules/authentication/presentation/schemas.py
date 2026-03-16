from pydantic import BaseModel, ConfigDict

from app.modules.shared.application.enums import ResponseMessages


# RESPONSE
class LoginResponse(BaseModel):
    message: str = ResponseMessages.LOGIN_SUCCESS.value

    model_config = ConfigDict(
        title="LoginResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for successful user login.",
            "example": {"message": ResponseMessages.LOGIN_SUCCESS.value},
        },
    )
