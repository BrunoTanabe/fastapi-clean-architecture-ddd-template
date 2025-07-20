from collections.abc import Callable
from http.client import HTTPException
from secrets import token_urlsafe
from time import time

import orjson
from fastapi import Request, Response
from fastapi.responses import ORJSONResponse
from hypercorn.logging import AccessLogAtoms
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import CoreException
from app.core.settings import settings
from app.core.utils import _current_timestamp


async def log_request_middleware(request: Request, call_next: Callable) -> Response:
    start_time = time()
    request_id: str = token_urlsafe(settings.LOGS_REQUEST_ID_LENGTH)
    exception = None

    with logger.contextualize(request_id=request_id):
        try:
            logger.debug(
                "Received request",
                method=request.method,
                path=request.url.path,
                query=request.url.query,
                content_type=request.headers.get("content-type"),
                user_agent=request.headers.get("user-agent"),
                host=request.headers.get("host"),
                content_length=request.headers.get("content-length"),
                client_ip=request.client.host,
            )

            response = await call_next(request)
        except Exception as exc:
            exception = exc
            response = HTTPException(CoreException())
        final_time = time()
        elapsed = final_time - start_time
        response_dict = {
            "status": response.status_code,
            "headers": response.headers.raw,
        }

        atoms = AccessLogAtoms(request, response_dict, final_time)  # type: ignore

        data = {
            "remote_ip": request.headers.get("x-forwarded-for") or atoms["h"],
            "schema": request.headers.get("x-forwarded-proto") or atoms["S"],
            "protocol": atoms["H"],
            "method": atoms["m"],
            "path_with_query": atoms["Uq"],
            "status_code": response.status_code,
            "response_length": atoms["B"],
            "elapsed": elapsed,
            "referer": atoms["f"],
            "user_agent": atoms["a"],
        }

        if not exception:
            logger.success("Request processed successfully", **data)
        else:
            logger.opt(exception=exception).error(
                "Unhandled exception occurred", **data
            )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Processed-Time"] = str(elapsed)

    return response


class ResponseFormattingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
            logger.debug(
                "Skipping response formatting for OpenAPI documentation endpoints."
            )
            return response

        if 200 <= response.status_code < 300:
            raw_body = b""
            async for chunk in response.body_iterator:
                raw_body += chunk

            try:
                original_data = orjson.loads(raw_body)

                formatted = {
                    "code": response.status_code,
                    "method": request.method,
                    "path": request.url.path,
                    "timestamp": _current_timestamp(),
                    "details": {
                        "message": "Request processed successfully.",
                        "data": original_data,
                    },
                }

                safe_headers = {}
                for key, value in response.headers.items():
                    if key.lower() not in [
                        "content-length",
                        "content-encoding",
                        "transfer-encoding",
                    ]:
                        safe_headers[key] = value

                logger.debug("Returning formatted response")

                return ORJSONResponse(
                    status_code=response.status_code,
                    content=formatted,
                    headers=safe_headers,
                )
            except orjson.JSONDecodeError:
                safe_headers = {}
                for key, value in response.headers.items():
                    if key.lower() not in [
                        "content-length",
                        "content-encoding",
                        "transfer-encoding",
                    ]:
                        safe_headers[key] = value

                logger.debug(
                    "Returning raw response due to JSON decode error", raw_body=raw_body
                )

                return Response(
                    content=raw_body,
                    status_code=response.status_code,
                    headers=safe_headers,
                    media_type=response.media_type,
                )

        logger.debug("Returning response without formatting")

        return response
