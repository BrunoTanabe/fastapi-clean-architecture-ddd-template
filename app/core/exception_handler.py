from typing import cast

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette import status

from app.core.utils import _current_timestamp


async def validation_exception_handler(
    request: Request, exc: Exception
) -> ORJSONResponse:
    err = cast(RequestValidationError, exc)
    errors = {e["loc"][-1]: e["msg"] for e in err.errors()}
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "method": request.method,
            "path": request.url.path,
            "timestamp": _current_timestamp(),
            "details": {"message": "Form validation error", "data": errors},
        },
    )


async def http_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    err = cast(StarletteHTTPException, exc)
    if hasattr(err, "message") and hasattr(err, "data"):
        message = getattr(err, "message")
        data = getattr(err, "data")
    else:
        if err.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Authentication error"
        elif err.status_code == status.HTTP_403_FORBIDDEN:
            message = "Authorization error"
        elif err.status_code == status.HTTP_404_NOT_FOUND:
            message = "Resource not found"
        elif err.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            message = "Method error"
        elif err.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            message = "Form validation error"
        else:
            message = "Internal processing error"
        data = {"error": str(err.detail)}

    return ORJSONResponse(
        status_code=err.status_code,
        content={
            "code": err.status_code,
            "method": request.method,
            "path": request.url.path,
            "timestamp": _current_timestamp(),
            "details": {
                "message": message,
                "data": data,
            },
        },
    )


async def internal_exception_handler(
    request: Request, exc: Exception
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "method": request.method,
            "path": request.url.path,
            "timestamp": _current_timestamp(),
            "details": {
                "message": "Internal Server Error",
                "data": {"error": "An unexpected error occurred."},
            },
        },
    )
