from pydantic import BaseModel, ConfigDict, Field

from app.modules.websocket.domain.enums import WebSocketMessageType


class WebSocketMessageResponse(BaseModel):
    message_type: WebSocketMessageType = Field(
        title="Message Type",
        description="Type of message sent through the WebSocket channel.",
        examples=[WebSocketMessageType.NOTIFICATION.value],
        json_schema_extra={
            "example": WebSocketMessageType.NOTIFICATION.value,
            "readOnly": True,
        },
    )
    body: dict = Field(
        title="Body",
        description="Serialized message payload. Structure depends on message_type.",
        json_schema_extra={
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="WebSocketMessageResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
    )
