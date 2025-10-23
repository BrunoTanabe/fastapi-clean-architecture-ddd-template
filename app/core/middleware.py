from collections.abc import Callable
from http import HTTPStatus
from secrets import token_urlsafe
from time import time

import orjson
from fastapi import Request, Response
from fastapi.responses import ORJSONResponse
from hypercorn.logging import AccessLogAtoms
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.responses import StreamingResponse

from app.core.enums import ResponseMessages
from app.core.exceptions import CoreException
from app.core.settings import settings
from app.core.utils import _current_timestamp


async def log_request_middleware(request: Request, call_next: Callable) -> Response:
    start_time = time()
    request_id: str = token_urlsafe(settings.LOGS_REQUEST_ID_LENGTH)
    exception = None

    with logger.contextualize(request_id=request_id):
        try:
            logger.info(
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
            core_exc = CoreException()
            response = ORJSONResponse(
                status_code=core_exc.status_code,
                content={
                    "code": core_exc.status_code,
                    "method": request.method,
                    "path": request.url.path,
                    "timestamp": _current_timestamp(),
                    "details": {
                        "message": ResponseMessages.INTERNAL_ERROR.value,
                        "data": core_exc.data,
                    },
                },
            )
        final_time = time()
        elapsed = final_time - start_time
        response_dict = {
            "status": response.status_code,
            "headers": response.headers.raw if hasattr(response, "headers") else {},
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
    @staticmethod
    def _is_docs_request(request: Request) -> bool:
        referer = (request.headers.get("referer") or "").lower()
        user_agent = (request.headers.get("user-agent") or "").lower()
        return "/docs" in referer or "/redoc" in referer or "swagger" in user_agent

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        if request.url.path in ["/openapi.json", "/docs", "/redoc"]:
            logger.debug(
                "Skipping response formatting for OpenAPI documentation endpoints."
            )
            return response

        content_type = (response.headers.get("content-type") or "").lower()
        if (
            isinstance(response, StreamingResponse)
            or "text/event-stream" in content_type
        ):
            for h in ("content-length", "content-encoding", "transfer-encoding"):
                if h in response.headers:
                    response.headers.pop(h, None)
            return response

        if isinstance(response, RedirectResponse):
            if self._is_docs_request(request):
                url = (
                    response.headers.get("location")
                    or response.headers.get("Location")
                    or response.headers.get("X-Redirect-URL")
                )
                if url:
                    formatted = {
                        "code": HTTPStatus.OK,
                        "method": request.method,
                        "path": request.url.path,
                        "timestamp": _current_timestamp(),
                        "details": {
                            "message": ResponseMessages.REDIRECT_AUTHENTICATION_NOTICE.value,
                            "data": {"url": url, "new_tab": False},
                        },
                    }
                    logger.debug("Converted redirect to JSON for Swagger UI", url=url)
                    return ORJSONResponse(
                        status_code=HTTPStatus.OK,
                        content=formatted,
                    )
            logger.debug("Skipping response formatting for redirect response.")
            return response

        if isinstance(response, HTMLResponse):
            if self._is_docs_request(request):
                url = response.headers.get("X-Redirect-URL")
                formatted = {
                    "code": HTTPStatus.OK,
                    "method": request.method,
                    "path": request.url.path,
                    "timestamp": _current_timestamp(),
                    "details": {
                        "message": ResponseMessages.REDIRECT_AUTHENTICATION_NOTICE.value,
                        "data": {"url": url, "new_tab": True},
                    },
                }
                logger.debug("Converted HTML to JSON for Swagger UI", url=url)
                return ORJSONResponse(
                    status_code=HTTPStatus.OK,
                    content=formatted,
                )
            logger.debug("Skipping response formatting for HTML response.")
            return response

        raw_body = b""
        async for chunk in response.body_iterator:
            raw_body += chunk

        content_type = response.headers.get("content-type", "")
        if (
            "text/html" in content_type
            or raw_body.startswith(b"<!DOCTYPE")
            or raw_body.startswith(b"<html")
        ):
            logger.debug("Skipping response formatting for HTML content")
            return Response(
                content=raw_body,
                status_code=response.status_code,
                headers=response.headers,
                media_type="text/html",
            )

        try:
            original_data = orjson.loads(raw_body)

            if 200 <= response.status_code < 300:
                message = ResponseMessages.SUCCESS.value
            elif response.status_code == 400:
                message = ResponseMessages.VALIDATION_ERROR.value
            elif response.status_code == 401:
                message = ResponseMessages.UNAUTHORIZED_ERROR.value
            elif response.status_code == 403:
                message = ResponseMessages.AUTHORIZATION_ERROR.value
            elif response.status_code == 404:
                message = ResponseMessages.RESOURCE_NOT_FOUND.value
            elif response.status_code == 405:
                message = ResponseMessages.METHOD_ERROR.value
            elif response.status_code == 422:
                message = ResponseMessages.VALIDATION_ERROR.value
            elif response.status_code >= 500:
                message = ResponseMessages.INTERNAL_ERROR.value
            else:
                message = "Request processed."

            if (
                isinstance(original_data, dict)
                and "code" in original_data
                and "method" in original_data
                and "path" in original_data
                and "timestamp" in original_data
                and "details" in original_data
            ):
                logger.debug("Response already formatted, returning as-is")
                safe_headers = {}
                for key, value in response.headers.items():
                    if key.lower() not in [
                        "content-length",
                        "content-encoding",
                        "transfer-encoding",
                    ]:
                        safe_headers[key] = value

                return ORJSONResponse(
                    status_code=response.status_code,
                    content=original_data,
                    headers=safe_headers,
                )

            formatted = {
                "code": response.status_code,
                "method": request.method,
                "path": request.url.path,
                "timestamp": _current_timestamp(),
                "details": {
                    "message": message,
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
