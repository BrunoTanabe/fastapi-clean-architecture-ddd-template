from uuid import UUID

from fastapi import WebSocket
from loguru import logger

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import Role
from app.modules.websocket.application.exceptions import WebSocketException
from app.modules.websocket.application.interfaces import IConnectionManagerService
from app.modules.websocket.application.mappers import entity_schema_mapper
from app.modules.websocket.domain.entities import WebSocketMessage


class ConnectionManager(IConnectionManagerService):
    def __init__(self) -> None:
        self.active_connections: dict[WebSocket, WebSocketMessage] = {}

    async def connect(self, websocket: WebSocket, message: WebSocketMessage) -> None:
        try:
            logger.debug(f"Connecting WebSocket for user '{message.user_id}'.")
            await websocket.accept()
            self.active_connections[websocket] = message
            logger.debug(
                f"WebSocket connected for user '{message.user_id}' session '{message.session_id}'. "
                f"Active connections: {len(self.active_connections)}."
            )
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                f"An error occurred in the connect connection manager for user '{message.user_id}'."
            )
            raise WebSocketException()

    async def disconnect(self, websocket: WebSocket) -> None:
        try:
            self.active_connections.pop(websocket, None)
            logger.debug(
                f"WebSocket disconnected. Active connections: {len(self.active_connections)}."
            )
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the disconnect connection manager."
            )
            raise WebSocketException()

    async def disconnect_user(self, user_id: UUID) -> None:
        try:
            to_close = [
                ws
                for ws, info in self.active_connections.items()
                if info.user_id == user_id
            ]
            for ws in to_close:
                try:
                    await ws.close(code=1000)
                except Exception as e:
                    logger.opt(exception=e).warning(
                        f"Failed to close WebSocket for user '{user_id}'. Already closed?"
                    )
                self.active_connections.pop(ws, None)
            if to_close:
                logger.debug(
                    f"Disconnected {len(to_close)} WebSocket(s) for user '{user_id}'. "
                    f"Active connections: {len(self.active_connections)}."
                )
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                f"An error occurred in the disconnect_user connection manager for user '{user_id}'."
            )
            raise WebSocketException()

    async def disconnect_session(self, session_id: UUID) -> None:
        try:
            to_close = [
                ws
                for ws, info in self.active_connections.items()
                if info.session_id == session_id
            ]
            for ws in to_close:
                try:
                    await ws.close(code=1000)
                except Exception as e:
                    logger.opt(exception=e).warning(
                        f"Failed to close WebSocket for session '{session_id}'. Already closed?"
                    )
                self.active_connections.pop(ws, None)
            if to_close:
                logger.debug(
                    f"Disconnected WebSocket for session '{session_id}'. "
                    f"Active connections: {len(self.active_connections)}."
                )
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                f"An error occurred in the disconnect_session connection manager for session '{session_id}'."
            )
            raise WebSocketException()

    async def send(self, message: WebSocketMessage, websocket: WebSocket) -> None:
        try:
            payload = entity_schema_mapper(message).model_dump(mode="json")
            await websocket.send_json(payload)
            logger.debug(f"WebSocket message sent to {websocket.client}.")
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                f"Failed to send WebSocket message to {websocket.client}. Disconnecting."
            )
            await self.disconnect(websocket)

    async def send_to_user(self, message: WebSocketMessage) -> None:
        try:
            target = [
                ws
                for ws, info in self.active_connections.items()
                if info.user_id == message.user_id
            ]
            if not target:
                logger.debug(
                    f"No active WebSocket connections for user '{message.user_id}'. Skipping."
                )
                return
            payload = entity_schema_mapper(message).model_dump(mode="json")
            for ws in target:
                try:
                    await ws.send_json(payload)
                except Exception as e:
                    logger.opt(exception=e).error(
                        f"Failed to send WebSocket message to {ws.client} "
                        f"for user '{message.user_id}'. Disconnecting."
                    )
                    await self.disconnect(ws)
            logger.debug(
                f"WebSocket message sent to {len(target)} connection(s) "
                f"for user '{message.user_id}'."
            )
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                f"An error occurred in the send_to_user connection manager for user '{message.user_id}'."
            )
            raise WebSocketException()

    async def broadcast_to(self, message: WebSocketMessage, minimum_role: Role) -> None:
        try:
            payload = entity_schema_mapper(message).model_dump(mode="json")
            sent_count = 0
            for ws, info in list(self.active_connections.items()):
                should_send = (
                    minimum_role == Role.USER
                    or (
                        minimum_role == Role.MANAGER
                        and info.role in (Role.MANAGER, Role.ADMIN)
                    )
                    or (minimum_role == Role.ADMIN and info.role == Role.ADMIN)
                )
                if not should_send:
                    continue
                try:
                    await ws.send_json(payload)
                    sent_count += 1
                except Exception as e:
                    logger.opt(exception=e).error(
                        f"Failed to broadcast WebSocket message to {ws.client}. Disconnecting."
                    )
                    await self.disconnect(ws)
            logger.debug(
                f"WebSocket broadcast_to(minimum_role={minimum_role.value}) "
                f"sent to {sent_count} connection(s)."
            )
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the broadcast_to connection manager."
            )
            raise WebSocketException()
