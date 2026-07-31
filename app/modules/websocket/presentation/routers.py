from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from loguru import logger

from app.core.security import authenticate_websocket, no_authentication
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import DomainException, StandardException
from app.modules.shared.domain.entities import DomainError
from app.modules.websocket.application.exceptions import WebSocketException
from app.modules.websocket.application.mappers import connect_entity_mapper
from app.modules.websocket.application.use_cases import WebSocketUseCases
from app.modules.websocket.presentation.dependencies import get_websocket_use_cases
from app.modules.websocket.presentation.docs import connect_ws_docs, router_docs
from app.modules.websocket.presentation.schemas import WebSocketMessageResponse

router = APIRouter(**router_docs)


# READ
@router.get("/connect/", **connect_ws_docs)
@router.get("/connect", include_in_schema=False)
async def websocket_connect_reference(
    _: Annotated[None, Depends(no_authentication)],
) -> WebSocketMessageResponse:
    raise WebSocketException()


# WEBSOCKET
@router.websocket("/connect/")
@router.websocket("/connect")
async def websocket_connect(
    websocket: WebSocket,
    authentication: Annotated[Authentication, Depends(authenticate_websocket)],
    use_case: Annotated[WebSocketUseCases, Depends(get_websocket_use_cases)],
) -> None:
    try:
        connection = connect_entity_mapper(authentication)
        await use_case.connect(websocket, connection)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An unexpected error occurred in the websocket connect endpoint."
        )
        raise WebSocketException()
