from http import HTTPStatus
from secrets import token_urlsafe
from time import time
from uuid import uuid4

import orjson
from loguru import logger
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.settings import settings
from app.modules.shared.application.exceptions import CoreException
from app.modules.shared.application.utils import current_timestamp, resolve_client_ip
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import (
    StandardDetailsResponse,
    StandardResponse,
)

_SKIP_FORMATTING_PATHS: frozenset[str] = frozenset({"/openapi.json", "/docs", "/redoc"})

_STATUS_MESSAGES: dict[int, str] = {
    400: ResponseMessages.VALIDATION_ERROR.value,
    401: ResponseMessages.UNAUTHORIZED_ERROR.value,
    403: ResponseMessages.AUTHORIZATION_ERROR.value,
    404: ResponseMessages.RESOURCE_NOT_FOUND.value,
    405: ResponseMessages.METHOD_ERROR.value,
    422: ResponseMessages.VALIDATION_ERROR.value,
    429: ResponseMessages.RATE_LIMIT_EXCEEDED.value,
}

_REDIRECT_STATUSES: frozenset[int] = frozenset({301, 302, 307, 308})

_REFORMAT_STRIP_HEADERS: frozenset[bytes] = frozenset(
    {b"content-length", b"content-encoding", b"transfer-encoding", b"content-type"}
)


def _message_for_status(status_code: int) -> str:
    if 200 <= status_code < 300:
        return ResponseMessages.SUCCESS.value
    if status_code >= 500:
        return ResponseMessages.INTERNAL_ERROR.value
    return _STATUS_MESSAGES.get(status_code, ResponseMessages.SUCCESS.value)


def _get_header(headers: list[tuple[bytes, bytes]], name: bytes) -> str:
    for k, v in headers:
        if k.lower() == name:
            return v.decode("latin-1")
    return ""


def _parse_cookies(cookie_header: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for part in cookie_header.split(";"):
        part = part.strip()
        if "=" in part:
            key, _, value = part.partition("=")
            cookies[key.strip()] = value.strip()
    return cookies


def _build_set_cookie(
    key: str,
    value: str,
    *,
    max_age: int,
    path: str,
    domain: str | None,
    secure: bool,
    httponly: bool,
    samesite: str,
) -> str:
    parts = [f"{key}={value}", f"Max-Age={max_age}", f"Path={path}"]
    if domain:
        parts.append(f"Domain={domain}")
    if secure:
        parts.append("Secure")
    if httponly:
        parts.append("HttpOnly")
    if samesite:
        parts.append(f"SameSite={samesite}")
    return "; ".join(parts)


class DeviceIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope.get("method") == "OPTIONS":
            await self.app(scope, receive, send)
            return

        req_headers: list[tuple[bytes, bytes]] = list(scope.get("headers", []))
        cookies = _parse_cookies(_get_header(req_headers, b"cookie"))
        device_id = cookies.get(settings.COOKIES_DEVICE_KEY)

        new_device_id: str | None = None
        if not device_id:
            device_id = uuid4().hex
            new_device_id = device_id

        scope.setdefault("state", {})
        scope["state"]["device_id"] = device_id
        if new_device_id:
            scope["state"]["new_device_id"] = new_device_id

        if not new_device_id:
            await self.app(scope, receive, send)
            return

        cookie_bytes = _build_set_cookie(
            settings.COOKIES_DEVICE_KEY,
            device_id,
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        ).encode("latin-1")

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                new_headers = list(message.get("headers", []))
                new_headers.append((b"set-cookie", cookie_bytes))
                message = {**message, "headers": new_headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)


class LogRequestMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time()
        request_id = token_urlsafe(settings.LOGS_REQUEST_ID_LENGTH)
        path: str = scope.get("path", "")
        skip_logging = path == "/health"
        method: str = scope.get("method", "")
        query_string = scope.get("query_string", b"").decode("latin-1")
        path_with_query = f"{path}?{query_string}" if query_string else path
        scheme: str = scope.get("scheme", "http")
        http_version: str = scope.get("http_version", "1.1")
        client = scope.get("client")
        client_host = client[0] if client else "unknown"

        req_headers: list[tuple[bytes, bytes]] = list(scope.get("headers", []))
        x_forwarded_proto = _get_header(req_headers, b"x-forwarded-proto")
        remote_ip = resolve_client_ip(
            x_forwarded_for=_get_header(req_headers, b"x-forwarded-for") or None,
            x_real_ip=_get_header(req_headers, b"x-real-ip") or None,
            peer_host=client_host,
        )

        exception: Exception | None = None
        response_started = False

        with logger.contextualize(request_id=request_id):
            if not skip_logging:
                logger.info(
                    "Received request",
                    method=method,
                    path=path,
                    query=query_string,
                    content_type=_get_header(req_headers, b"content-type"),
                    user_agent=_get_header(req_headers, b"user-agent"),
                    host=_get_header(req_headers, b"host"),
                    content_length=_get_header(req_headers, b"content-length"),
                    client_ip=client_host,
                )

            async def send_wrapper(message: Message) -> None:
                nonlocal response_started

                if message["type"] == "http.response.start":
                    response_started = True
                    request_elapsed = time() - start_time
                    status_code: int = message["status"]
                    resp_headers: list[tuple[bytes, bytes]] = list(
                        message.get("headers", [])
                    )

                    if not skip_logging:
                        log_data = {
                            "remote_ip": remote_ip,
                            "schema": x_forwarded_proto or scheme,
                            "protocol": f"HTTP/{http_version}",
                            "method": method,
                            "path_with_query": path_with_query,
                            "status_code": status_code,
                            "response_length": _get_header(
                                resp_headers, b"content-length"
                            ),
                            "elapsed": request_elapsed,
                            "referer": _get_header(req_headers, b"referer"),
                            "user_agent": _get_header(req_headers, b"user-agent"),
                        }
                        if not exception:
                            logger.success("Request processed successfully", **log_data)
                        else:
                            logger.opt(exception=exception).error(
                                "Unhandled exception occurred", **log_data
                            )

                    resp_headers.append((b"x-request-id", request_id.encode()))
                    resp_headers.append(
                        (b"x-processed-time", str(request_elapsed).encode())
                    )
                    message = {**message, "headers": resp_headers}

                await send(message)

            try:
                await self.app(scope, receive, send_wrapper)
            except Exception as exc:
                exception = exc
                if not response_started:
                    core_exc = CoreException()
                    body = (
                        StandardResponse(
                            code=core_exc.status_code,
                            method=method,
                            path=path,
                            timestamp=current_timestamp(),
                            details=StandardDetailsResponse(
                                message=ResponseMessages.INTERNAL_ERROR.value,
                                data=core_exc.data,
                            ),
                        )
                        .model_dump_json()
                        .encode()
                    )
                    elapsed = time() - start_time

                    if not skip_logging:
                        logger.opt(exception=exc).error(
                            "Unhandled exception occurred",
                            remote_ip=remote_ip,
                            schema=x_forwarded_proto or scheme,
                            protocol=f"HTTP/{http_version}",
                            method=method,
                            path_with_query=path_with_query,
                            status_code=core_exc.status_code,
                            response_length=len(body),
                            elapsed=elapsed,
                            referer=_get_header(req_headers, b"referer"),
                            user_agent=_get_header(req_headers, b"user-agent"),
                        )

                    await send(
                        {
                            "type": "http.response.start",
                            "status": core_exc.status_code,
                            "headers": [
                                (b"content-type", b"application/json"),
                                (b"content-length", str(len(body)).encode()),
                                (b"x-request-id", request_id.encode()),
                                (b"x-processed-time", str(elapsed).encode()),
                            ],
                        }
                    )
                    await send(
                        {"type": "http.response.body", "body": body, "more_body": False}
                    )
                else:
                    raise


class ResponseFormattingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    @staticmethod
    def _is_docs_request(headers: list[tuple[bytes, bytes]]) -> bool:
        referer = _get_header(headers, b"referer").lower()
        user_agent = _get_header(headers, b"user-agent").lower()
        return (
            "/docs" in referer
            or "/redoc" in referer
            or "/openapi.json" in referer
            or "swagger" in user_agent
        )

    @staticmethod
    def _is_already_formatted(data: object) -> bool:
        return (
            isinstance(data, dict)
            and "code" in data
            and "method" in data
            and "path" in data
            and "timestamp" in data
            and "details" in data
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope["path"]
        if path in _SKIP_FORMATTING_PATHS:
            await self.app(scope, receive, send)
            return

        method: str = scope.get("method", "")
        req_headers: list[tuple[bytes, bytes]] = list(scope.get("headers", []))
        is_docs = self._is_docs_request(req_headers)

        start_message: dict | None = None
        is_passthrough = False
        is_done = False
        body_chunks: list[bytes] = []

        async def send_wrapper(message: Message) -> None:
            nonlocal start_message, is_passthrough, is_done

            if is_passthrough:
                await send(message)
                return

            if is_done:
                return

            if message["type"] == "http.response.start":
                status: int = message["status"]
                resp_headers: list[tuple[bytes, bytes]] = list(
                    message.get("headers", [])
                )
                content_type = _get_header(resp_headers, b"content-type").lower()

                if "text/event-stream" in content_type:
                    is_passthrough = True
                    await send(message)
                    return

                if status in _REDIRECT_STATUSES:
                    if is_docs:
                        location = _get_header(
                            resp_headers, b"location"
                        ) or _get_header(resp_headers, b"x-redirect-url")
                        if location:
                            body = (
                                StandardResponse(
                                    code=HTTPStatus.PERMANENT_REDIRECT,
                                    method=method,
                                    path=path,
                                    timestamp=current_timestamp(),
                                    details=StandardDetailsResponse(
                                        message=ResponseMessages.REDIRECT_AUTHENTICATION_NOTICE.value,
                                        data={"url": location, "new_tab": False},
                                    ),
                                )
                                .model_dump_json()
                                .encode()
                            )
                            logger.debug(
                                "Converted redirect to JSON for Swagger UI",
                                url=location,
                            )
                            new_headers: list[tuple[bytes, bytes]] = [
                                (b"content-type", b"application/json"),
                                (b"content-length", str(len(body)).encode()),
                            ]
                            new_headers += [
                                (k, v)
                                for k, v in resp_headers
                                if k.lower() == b"set-cookie"
                            ]
                            await send(
                                {
                                    "type": "http.response.start",
                                    "status": HTTPStatus.PERMANENT_REDIRECT,
                                    "headers": new_headers,
                                }
                            )
                            await send(
                                {
                                    "type": "http.response.body",
                                    "body": body,
                                    "more_body": False,
                                }
                            )
                            is_done = True
                            return
                    is_passthrough = True
                    await send(message)
                    return

                if "text/html" in content_type:
                    if is_docs:
                        redirect_url = _get_header(resp_headers, b"x-redirect-url")
                        if redirect_url:
                            body = (
                                StandardResponse(
                                    code=HTTPStatus.OK,
                                    method=method,
                                    path=path,
                                    timestamp=current_timestamp(),
                                    details=StandardDetailsResponse(
                                        message=ResponseMessages.REDIRECT_AUTHENTICATION_NOTICE.value,
                                        data={"url": redirect_url, "new_tab": True},
                                    ),
                                )
                                .model_dump_json()
                                .encode()
                            )
                            logger.debug(
                                "Converted HTML to JSON for Swagger UI",
                                url=redirect_url,
                            )
                            new_headers = [
                                (b"content-type", b"application/json"),
                                (b"content-length", str(len(body)).encode()),
                            ]
                            new_headers += [
                                (k, v)
                                for k, v in resp_headers
                                if k.lower() == b"set-cookie"
                            ]
                            await send(
                                {
                                    "type": "http.response.start",
                                    "status": HTTPStatus.OK,
                                    "headers": new_headers,
                                }
                            )
                            await send(
                                {
                                    "type": "http.response.body",
                                    "body": body,
                                    "more_body": False,
                                }
                            )
                            is_done = True
                            return
                    is_passthrough = True
                    await send(message)
                    return

                start_message = message

            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))

                if not message.get("more_body", False):
                    raw_body = b"".join(body_chunks)

                    if start_message is None:
                        return

                    if raw_body.startswith((b"<!DOCTYPE", b"<html")):
                        await send(start_message)
                        await send(
                            {
                                "type": "http.response.body",
                                "body": raw_body,
                                "more_body": False,
                            }
                        )
                        is_done = True
                        return

                    status = start_message["status"]
                    resp_headers = list(start_message.get("headers", []))

                    try:
                        original_data = orjson.loads(raw_body)

                        if self._is_already_formatted(original_data):
                            new_body = raw_body
                        else:
                            if (
                                isinstance(original_data, dict)
                                and "message" in original_data
                            ):
                                msg = original_data["message"]
                                data = {
                                    k: v
                                    for k, v in original_data.items()
                                    if k != "message"
                                }
                            else:
                                msg = _message_for_status(status)
                                data = original_data

                            new_body = (
                                StandardResponse(
                                    code=status,
                                    method=method,
                                    path=path,
                                    timestamp=current_timestamp(),
                                    details=StandardDetailsResponse(
                                        message=msg, data=data
                                    ),
                                )
                                .model_dump_json()
                                .encode()
                            )

                        new_headers = [
                            (k, v)
                            for k, v in resp_headers
                            if k.lower() not in _REFORMAT_STRIP_HEADERS
                        ]
                        new_headers.append((b"content-type", b"application/json"))
                        new_headers.append(
                            (b"content-length", str(len(new_body)).encode())
                        )

                        await send(
                            {
                                "type": "http.response.start",
                                "status": status,
                                "headers": new_headers,
                            }
                        )
                        await send(
                            {
                                "type": "http.response.body",
                                "body": new_body,
                                "more_body": False,
                            }
                        )

                    except orjson.JSONDecodeError:
                        await send(start_message)
                        await send(
                            {
                                "type": "http.response.body",
                                "body": raw_body,
                                "more_body": False,
                            }
                        )

                    is_done = True

        await self.app(scope, receive, send_wrapper)
