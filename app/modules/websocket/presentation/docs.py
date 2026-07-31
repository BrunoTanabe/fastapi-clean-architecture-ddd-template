from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse
from app.modules.websocket.domain.enums import WebSocketMessageType
from app.modules.websocket.presentation.schemas import WebSocketMessageResponse

# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/websocket",
    "tags": ["WebSocket"],
    "responses": {
        400: {
            "model": StandardResponse,
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "Bad Request": {
                            "summary": "The request could not be understood or was missing required parameters.",
                            "value": {
                                "code": 400,
                                "method": "GET",
                                "path": "/api/v1/websocket/connect",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.VALIDATION_ERROR.value,
                                    "data": {
                                        "error": "The request is missing required parameters."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        401: {
            "model": StandardResponse,
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "examples": {
                        "Unauthorized": {
                            "summary": "Authentication is required and has failed or has not yet been provided.",
                            "value": {
                                "code": 401,
                                "method": "GET",
                                "path": "/api/v1/websocket/connect",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.UNAUTHORIZED_ERROR.value,
                                    "data": {
                                        "error": "Authentication credentials were missing or incorrect."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        403: {
            "model": StandardResponse,
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "examples": {
                        "Forbidden": {
                            "summary": "The request was valid, but the server is refusing action.",
                            "value": {
                                "code": 403,
                                "method": "GET",
                                "path": "/api/v1/websocket/connect",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.AUTHORIZATION_ERROR.value,
                                    "data": {
                                        "error": "You do not have permission to access this resource."
                                    },
                                },
                            },
                        },
                    },
                }
            },
        },
        500: {
            "model": StandardResponse,
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "examples": {
                        "Internal Server Error": {
                            "summary": "An unexpected error occurred while processing the request.",
                            "value": {
                                "code": 500,
                                "method": "GET",
                                "path": "/api/v1/websocket/connect",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.INTERNAL_ERROR.value,
                                    "data": {"error": "An unexpected error occurred."},
                                },
                            },
                        },
                    },
                }
            },
        },
    },
}


# ENDPOINT DOCS
# CONNECT (WebSocket reference — GET is never executed, exists only for OpenAPI)
connect_ws_docs = {
    "summary": "WebSocket — Connect",
    "description": (
        "> ⚠️ **This is a documentation reference, not a callable HTTP endpoint.**\n\n"
        "Upgrade an HTTP connection to a persistent **WebSocket** channel for real-time "
        "server-push messages. Connect with `ws://` (dev) or `wss://` (prod) using a "
        "WebSocket client — browsers, `websocat`, or the test page at "
        "`/devtools/websocket_test.html`.\n\n"
        "---\n\n"
        "### Authentication\n"
        "Requires the `hub_session_id` cookie set by `POST /api/v1/auth/login`. "
        "No `Authorization` header — cookies are sent automatically on same-origin upgrades.\n\n"
        "### Origin validation\n"
        "The `Origin` header must match a value in `SECURITY_ALLOW_ORIGINS`. "
        "Connections from other origins are rejected with **403** before the handshake completes.\n\n"
        "### Server → client messages\n"
        "The server sends JSON frames. The `message_type` field discriminates the payload shape:\n\n"
        "| `message_type` | `body` shape |\n"
        "|---|---|\n"
        f"| `{WebSocketMessageType.NOTIFICATION.value}` | `NotificationResponse` |\n\n"
        "### Example frame\n"
        "```json\n"
        "{\n"
        f'  "message_type": "{WebSocketMessageType.NOTIFICATION.value}",\n'
        '  "body": {\n'
        '    "id": "550e8400-e29b-41d4-a716-446655440000",\n'
        '    "created_at": "2025-01-15T10:30:00Z",\n'
        '    "notification_type": "knowledge_created",\n'
        '    "title": "Knowledge base created",\n'
        '    "body": "The knowledge base \'ML Fundamentals\' was created successfully.",\n'
        '    "redirect_url": "https://app.example.com/knowledge/550e8400"\n'
        "  }\n"
        "}\n"
        "```\n\n"
        "### Full AsyncAPI spec\n"
        "Available at [`/devtools/asyncapi.html`](http://localhost:8000/devtools/asyncapi.html) "
        "in development."
    ),
    "response_description": (
        "JSON frame pushed by the server. `message_type` identifies the payload shape."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": WebSocketMessageResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "WebSocket frame — server-push message.",
            "model": WebSocketMessageResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Notification — knowledge_created": {
                            "summary": "Notification: knowledge base created",
                            "value": {
                                "message_type": WebSocketMessageType.NOTIFICATION.value,
                                "body": {
                                    "id": "550e8400-e29b-41d4-a716-446655440000",
                                    "created_at": "2025-01-15T10:30:00Z",
                                    "notification_type": "knowledge_created",
                                    "title": "Knowledge base created",
                                    "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                                    "redirect_url": "https://app.example.com/knowledge/550e8400",
                                },
                            },
                        },
                        "Notification — system_alert": {
                            "summary": "Notification: system alert",
                            "value": {
                                "message_type": WebSocketMessageType.NOTIFICATION.value,
                                "body": {
                                    "id": "661f9511-f3ac-52e5-b827-557766551111",
                                    "created_at": "2025-01-16T08:00:00Z",
                                    "notification_type": "system_alert",
                                    "title": "System alert",
                                    "body": "Scheduled maintenance on 2025-02-01 at 02:00 UTC.",
                                    "redirect_url": None,
                                },
                            },
                        },
                    }
                }
            },
        },
    },
}
