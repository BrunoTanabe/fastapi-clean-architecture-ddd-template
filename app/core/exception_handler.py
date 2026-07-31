from http import HTTPStatus
from typing import cast

from fastapi import Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Receive, Scope, Send

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.application.utils import current_timestamp
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import (
    StandardDetailsResponse,
    StandardResponse,
)


class _WebSocketRejectionResponse(Response):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # type: ignore[override]
        await send(
            {
                "type": "websocket.http.response.start",
                "status": self.status_code,
                "headers": [],
            }
        )
        await send(
            {
                "type": "websocket.http.response.body",
                "body": b"",
                "more_body": False,
            }
        )


async def validation_exception_handler(
    request: Request | WebSocket, exc: Exception
) -> Response:
    if isinstance(request, WebSocket):
        return _WebSocketRejectionResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    err = cast(RequestValidationError, exc)
    errors = {e["loc"][-1]: e["msg"] for e in err.errors()}

    response_content = StandardResponse(
        code=HTTPStatus.UNPROCESSABLE_ENTITY,
        method=request.method,
        path=request.url.path,
        timestamp=current_timestamp(),
        details=StandardDetailsResponse(
            message=ResponseMessages.VALIDATION_ERROR.value,
            data=errors,
        ),
    )

    return Response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_content.model_dump_json(),
        media_type="application/json",
    )


async def http_exception_handler(
    request: Request | WebSocket, exc: Exception
) -> Response:
    if isinstance(request, WebSocket):
        err = cast(StarletteHTTPException, exc)
        return _WebSocketRejectionResponse(status_code=err.status_code)

    err = cast(StarletteHTTPException, exc)
    if isinstance(err, StandardException):
        message = err.message
        data = err.data
    else:
        if err.status_code == status.HTTP_400_BAD_REQUEST:
            message = ResponseMessages.BAD_REQUEST.value
        elif err.status_code == status.HTTP_401_UNAUTHORIZED:
            message = ResponseMessages.UNAUTHORIZED_ERROR.value
        elif err.status_code == status.HTTP_403_FORBIDDEN:
            message = ResponseMessages.AUTHORIZATION_ERROR.value
        elif err.status_code == status.HTTP_404_NOT_FOUND:
            message = ResponseMessages.RESOURCE_NOT_FOUND.value
        elif err.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            message = ResponseMessages.METHOD_ERROR.value
        elif err.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
            message = ResponseMessages.VALIDATION_ERROR.value
        elif err.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            message = ResponseMessages.RATE_LIMIT_EXCEEDED.value
        else:
            message = ResponseMessages.INTERNAL_ERROR.value
        data = {"error": str(err.detail)}

    response_content = StandardResponse(
        code=err.status_code,
        method=request.method,
        path=request.url.path,
        timestamp=current_timestamp(),
        details=StandardDetailsResponse(
            message=message,
            data=data,
        ),
    )

    return Response(
        status_code=err.status_code,
        content=response_content.model_dump_json(),
        media_type="application/json",
    )


async def internal_exception_handler(
    request: Request | WebSocket, exc: Exception
) -> Response:
    if isinstance(request, WebSocket):
        return _WebSocketRejectionResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    response_content = StandardResponse(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        method=request.method,
        path=request.url.path,
        timestamp=current_timestamp(),
        details=StandardDetailsResponse(
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={"error": "An unexpected error occurred."},
        ),
    )

    return Response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_content.model_dump_json(),
        media_type="application/json",
    )
