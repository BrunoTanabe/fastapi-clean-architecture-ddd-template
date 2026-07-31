from typing import Protocol
from uuid import UUID

from fastapi import WebSocket

from app.modules.shared.domain.enums import Role
from app.modules.websocket.domain.entities import WebSocketMessage


class IConnectionManagerService(Protocol):
    async def connect(
        self, websocket: WebSocket, message: WebSocketMessage
    ) -> None: ...

    async def disconnect(self, websocket: WebSocket) -> None: ...

    async def disconnect_user(self, user_id: UUID) -> None: ...

    async def disconnect_session(self, session_id: UUID) -> None: ...

    async def send(self, message: WebSocketMessage, websocket: WebSocket) -> None: ...

    async def send_to_user(self, message: WebSocketMessage) -> None: ...

    async def broadcast_to(
        self, message: WebSocketMessage, minimum_role: Role
    ) -> None: ...
