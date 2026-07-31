from app.modules.authentication.domain.entities import Authentication
from app.modules.notification.application.mappers import entity_notification_mapper
from app.modules.notification.domain.entities import Notification
from app.modules.websocket.domain.entities import WebSocketMessage
from app.modules.websocket.presentation.schemas import WebSocketMessageResponse


# ENTITY / DTOS
def connect_entity_mapper(authentication: Authentication) -> WebSocketMessage:
    return WebSocketMessage(
        session_id=authentication.id,
        user_id=authentication.user.id,
        role=authentication.user.role,
        origin=authentication.origin or "",
    )


def entity_schema_mapper(message: WebSocketMessage) -> WebSocketMessageResponse:
    if isinstance(message.body, Notification):
        body_dict = entity_notification_mapper(message.body).model_dump(mode="json")
    # elif isinstance(message.body, ChatMessage):
    #     body_dict = entity_chat_message_mapper(message.body).model_dump(mode="json")
    else:
        body_dict = {}

    return WebSocketMessageResponse(
        message_type=message.message_type,
        body=body_dict,
    )
