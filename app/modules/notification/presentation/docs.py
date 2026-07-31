from http import HTTPStatus

from app.modules.notification.domain.enums import NotificationType
from app.modules.notification.presentation.schemas import GetAllNotificationsResponse
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse, UpdateResponse

# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/notification",
    "tags": ["Notification"],
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
                                "path": "/api/v1/notification",
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
                                "path": "/api/v1/notification",
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
                                "path": "/api/v1/notification",
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
        405: {
            "model": StandardResponse,
            "description": "Method Not Allowed",
            "content": {
                "application/json": {
                    "examples": {
                        "Method Not Allowed": {
                            "summary": "The method is not allowed for the requested URL.",
                            "value": {
                                "code": 405,
                                "method": "PUT",
                                "path": "/api/v1/notification",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.METHOD_NOT_ALLOWED.value,
                                    "data": {
                                        "error": "The method is not allowed for the requested URL."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        422: {
            "model": StandardResponse,
            "description": "Form Validation Error",
            "content": {
                "application/json": {
                    "examples": {
                        "Form Validation Error": {
                            "summary": "The request was well-formed but was unable to be followed due to semantic errors.",
                            "value": {
                                "code": 422,
                                "method": "GET",
                                "path": "/api/v1/notification",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.VALIDATION_ERROR.value,
                                    "data": {
                                        "error": "The request contains semantic errors and cannot be processed."
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
                                "path": "/api/v1/notification",
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
        502: {
            "model": StandardResponse,
            "description": "Bad Gateway",
            "content": {
                "application/json": {
                    "examples": {
                        "Bad Gateway": {
                            "summary": "The server received an invalid response from the upstream server.",
                            "value": {
                                "code": 502,
                                "method": "GET",
                                "path": "/api/v1/notification",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.BAD_GATEWAY.value,
                                    "data": {
                                        "error": "The server received an invalid response from the upstream server."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        504: {
            "model": StandardResponse,
            "description": "Gateway Timeout",
            "content": {
                "application/json": {
                    "examples": {
                        "Gateway Timeout": {
                            "summary": "The server did not receive a timely response from the upstream server.",
                            "value": {
                                "code": 504,
                                "method": "GET",
                                "path": "/api/v1/notification",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.GATEWAY_TIMEOUT.value,
                                    "data": {
                                        "error": "The server did not receive a timely response from the upstream server."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}

# ENDPOINT DOCS
# UPDATE
mark_as_read_docs = {
    "summary": "Endpoint to mark a notification as read.",
    "description": "Mark a specific notification as read for the authenticated user. Verifies existence and ownership before updating the read status and timestamp.",
    "response_description": "Confirmation that the notification was marked as read successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": UpdateResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": UpdateResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Notification Marked as Read": {
                            "summary": "Notification Marked as Read",
                            "value": {
                                "code": 200,
                                "method": "PATCH",
                                "path": "/api/v1/notification/550e8400-e29b-41d4-a716-446655440000",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.UPDATED.value,
                                    "data": {},
                                },
                            },
                        },
                    }
                }
            },
        },
        404: {
            "model": StandardResponse,
            "description": "Notification Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "Notification Not Found": {
                            "summary": "No active notification with the given ID was found for the authenticated user.",
                            "value": {
                                "code": 404,
                                "method": "PATCH",
                                "path": "/api/v1/notification/550e8400-e29b-41d4-a716-446655440000",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "errors": "Notification with id '550e8400-e29b-41d4-a716-446655440000' not found."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}

# READ
get_all_docs = {
    "summary": "Endpoint to retrieve all notifications for the authenticated user.",
    "description": "Retrieve all active notifications belonging to the authenticated user, sorted and paginated.",
    "response_description": "A paginated list of notifications with their type, title, body, read status, and optional redirect URL.",
    "status_code": HTTPStatus.OK,
    "response_model": GetAllNotificationsResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": GetAllNotificationsResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Notifications Retrieved Successfully": {
                            "summary": "Notifications Retrieved Successfully",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/api/v1/notification",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RETRIEVED.value,
                                    "data": {
                                        "Notification": [
                                            {
                                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                                "notification_type": NotificationType.KNOWLEDGE_CREATED.value,
                                                "title": "Knowledge base created",
                                                "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                                                "redirect_url": "https://app.example.com/knowledge/550e8400",
                                                "is_read": False,
                                                "created_at": "2025-01-15T10:30:00Z",
                                            }
                                        ],
                                        "pagination": {
                                            "total": 1,
                                            "page": 1,
                                            "limit": 20,
                                            "total_pages": 1,
                                            "has_next": False,
                                            "has_prev": False,
                                        },
                                    },
                                },
                            },
                        },
                    }
                }
            },
        },
    },
}
