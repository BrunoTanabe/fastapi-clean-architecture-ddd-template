from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from loguru import logger

from app.modules.shared.application.exceptions import DomainException, StandardException
from app.modules.shared.domain.entities import DomainError
from app.modules.websocket.application.exceptions import WebSocketException
from app.modules.websocket.application.interfaces import IConnectionManagerService
from app.modules.websocket.domain.entities import WebSocketMessage


class WebSocketUseCases:
    def __init__(self, service: IConnectionManagerService) -> None:
        self.service = service

    # CONNECT
    async def connect(self, websocket: WebSocket, message: WebSocketMessage) -> None:
        try:
            logger.debug(
                f"Initializing connect use case for user '{message.user_id}' "
                f"session '{message.session_id}'."
            )

            await self.service.connect(websocket, message)

            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            await self.service.disconnect(websocket)
            logger.debug(
                f"Connect use case completed: client disconnected for user '{message.user_id}'."
            )
        except StandardException:
            await self.service.disconnect(websocket)
            raise
        except DomainError as e:
            await self.service.disconnect(websocket)
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                f"An unexpected error occurred during the connect use case for user '{message.user_id}'."
            )
            await self.service.disconnect(websocket)
            raise WebSocketException()
