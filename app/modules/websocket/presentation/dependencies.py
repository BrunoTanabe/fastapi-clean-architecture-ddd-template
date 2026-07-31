from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection

from app.modules.websocket.application.interfaces import IConnectionManagerService
from app.modules.websocket.application.use_cases import WebSocketUseCases


def get_connection_manager(conn: HTTPConnection) -> IConnectionManagerService:
    return conn.app.state.connection_manager


def get_websocket_use_cases(
    service: Annotated[IConnectionManagerService, Depends(get_connection_manager)],
) -> WebSocketUseCases:
    return WebSocketUseCases(service=service)
