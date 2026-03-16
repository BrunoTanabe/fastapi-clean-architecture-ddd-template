from collections.abc import Callable
from http import HTTPStatus
from secrets import token_urlsafe
from time import time
from uuid import uuid4

import orjson
from fastapi import Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from hypercorn.logging import AccessLogAtoms
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.settings import settings
from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.application.utils import current_timestamp
from app.modules.shared.presentation.exceptions import CoreException
from app.modules.shared.presentation.schemas import (
    StandardResponse,
    StandardDetailsResponse,
)


async def log_request_middleware(request: Request, call_next: Callable) -> Response:
    start_time = time()
    request_id: str = token_urlsafe(settings.LOGS_REQUEST_ID_LENGTH)
    exception = None

    skip_logging = request.url.path == "/health"

    with logger.contextualize(request_id=request_id):
        try:
            if not skip_logging:
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
            response_content = StandardResponse(
                code=core_exc.status_code,
                method=request.method,
                path=request.url.path,
                timestamp=current_timestamp(),
                details=StandardDetailsResponse(
                    message=ResponseMessages.INTERNAL_ERROR.value, data=core_exc.data
                ),
            )
            response = Response(
                status_code=core_exc.status_code,
                content=response_content.model_dump_json(),
                media_type="application/json",
            )
        final_time = time()
        elapsed = final_time - start_time
        if not skip_logging:
            response_dict = {
                "status": response.status_code,
                "headers": response.headers.raw if hasattr(response, "headers") else {},
            }

            atoms = AccessLogAtoms(request, response_dict, final_time)  # noqa

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
    _EXCLUDED_HEADERS = {"content-length", "content-encoding", "transfer-encoding"}

    @staticmethod
    def _is_docs_request(request: Request) -> bool:
        referer = (request.headers.get("referer") or "").lower()
        user_agent = (request.headers.get("user-agent") or "").lower()
        return (
            "/docs" in referer
            or "/redoc" in referer
            or "/openapi.json" in referer
            or "swagger" in user_agent
        )

    @classmethod
    def _safe_headers(cls, response: Response) -> dict[str, str]:
        return {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in cls._EXCLUDED_HEADERS and key.lower() != "set-cookie"
        }

    @staticmethod
    def _set_cookie_headers(response: Response) -> list[tuple[bytes, bytes]]:
        return [
            (key, value)
            for key, value in response.raw_headers
            if key.lower() == b"set-cookie"
        ]

    @classmethod
    def _build_response(
        cls,
        original_response: Response,
        *,
        status_code: int,
        content: str | bytes,
        media_type: str | None,
    ) -> Response:
        rebuilt_response = Response(
            status_code=status_code,
            content=content,
            headers=cls._safe_headers(original_response),
            media_type=media_type,
        )

        # Preserve every Set-Cookie header because login sets multiple cookies.
        for key, value in cls._set_cookie_headers(original_response):
            rebuilt_response.raw_headers.append((key, value))

        return rebuilt_response

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
            logger.debug("Skipping response formatting for SSE streaming")
            return response

        if isinstance(response, RedirectResponse):
            if self._is_docs_request(request):
                url = (
                    response.headers.get("location")
                    or response.headers.get("Location")
                    or response.headers.get("X-Redirect-URL")
                )
                if url:
                    response_content = StandardResponse(
                        code=HTTPStatus.PERMANENT_REDIRECT,
                        method=request.method,
                        path=request.url.path,
                        timestamp=current_timestamp(),
                        details=StandardDetailsResponse(
                            message=ResponseMessages.REDIRECT_AUTHENTICATION_NOTICE.value,
                            data={"url": url, "new_tab": False},
                        ),
                    )
                    logger.debug("Converted redirect to JSON for Swagger UI", url=url)
                    return self._build_response(
                        response,
                        status_code=HTTPStatus.PERMANENT_REDIRECT,
                        content=response_content.model_dump_json(),
                        media_type="application/json",
                    )
            logger.debug("Skipping response formatting for redirect response.")
            return response

        if isinstance(response, HTMLResponse):
            if self._is_docs_request(request):
                url = response.headers.get("X-Redirect-URL")
                response_content = StandardResponse(
                    code=HTTPStatus.OK,
                    method=request.method,
                    path=request.url.path,
                    timestamp=current_timestamp(),
                    details=StandardDetailsResponse(
                        message=ResponseMessages.REDIRECT_AUTHENTICATION_NOTICE.value,
                        data={"url": url, "new_tab": True},
                    ),
                )
                logger.debug("Converted HTML to JSON for Swagger UI", url=url)
                return self._build_response(
                    response,
                    status_code=HTTPStatus.OK,
                    content=response_content.model_dump_json(),
                    media_type="application/json",
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
            return self._build_response(
                response,
                content=raw_body,
                status_code=response.status_code,
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
            elif response.status_code == 429:
                message = ResponseMessages.RATE_LIMIT_EXCEEDED.value
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
                return self._build_response(
                    response,
                    status_code=response.status_code,
                    content=orjson.dumps(original_data),
                    media_type="application/json",
                )

            response_content = StandardResponse(
                code=response.status_code,
                method=request.method,
                path=request.url.path,
                timestamp=current_timestamp(),
                details=StandardDetailsResponse(message=message, data=original_data),
            )

            if request.url.path != "/health":
                logger.debug("Returning formatted response")

            return self._build_response(
                response,
                status_code=response.status_code,
                content=response_content.model_dump_json(),
                media_type="application/json",
            )
        except orjson.JSONDecodeError:
            logger.debug(
                "Returning raw response due to JSON decode error",
                raw_body=raw_body,
            )

            return self._build_response(
                response,
                content=raw_body,
                status_code=response.status_code,
                media_type=response.media_type,
            )


class DeviceIdMiddleware(BaseHTTPMiddleware):
    COOKIE_NAME = "device_id"

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        device_id = request.cookies.get(self.COOKIE_NAME)

        if not device_id:
            device_id = uuid4().hex
            request.state.new_device_id = device_id

        request.state.device_id = device_id

        response: Response = await call_next(request)

        if getattr(request.state, "new_device_id", None):
            response.set_cookie(
                key=settings.COOKIES_DEVICE_KEY,
                value=device_id,
                max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
                path=settings.COOKIES_REFRESH_TOKEN_PATH,
                domain=settings.COOKIES_DOMAIN,
                secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
                httponly=True,
                samesite="strict",
            )

        return response
