from dataclasses import dataclass, field
from uuid import UUID

from app.modules.notification.domain.entities import Notification
from app.modules.shared.domain.entities import DomainErrors
from app.modules.shared.domain.enums import Role
from app.modules.websocket.domain.enums import WebSocketMessageType


@dataclass(kw_only=True, slots=True)
class WebSocketMessage:
    session_id: UUID = field(default=None, repr=True, compare=True)
    user_id: UUID = field(default=None, repr=True, compare=False)
    role: Role = field(default=None, repr=True, compare=False)
    origin: str = field(default="", repr=True, compare=False)

    body: Notification | None = field(default=None, repr=False, compare=False)
    message_type: WebSocketMessageType = field(
        default=None, init=False, repr=True, compare=False
    )

    def __post_init__(self) -> None:
        errors: list[str] = []
        is_outbound = self.body is not None

        if not is_outbound:
            if not self.session_id:
                errors.append("WebSocketMessage must have a session_id.")
            if not self.user_id:
                errors.append("WebSocketMessage must have a user_id.")
            if not self.role:
                errors.append("WebSocketMessage must have a role.")

        if self.body is not None:
            if isinstance(self.body, Notification):
                self.message_type = WebSocketMessageType.NOTIFICATION
            else:
                errors.append(f"Unsupported body type: {type(self.body).__name__}.")

        if errors:
            raise DomainErrors(errors)
