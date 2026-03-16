from http import HTTPStatus

from fastapi import Security

from app.core.security import (
    no_authentication,
    authenticate_refresh,
    authenticate_logout,
)
from app.modules.authentication.presentation.schemas import (
    LoginResponse,
    LogoutResponse,
)
from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.presentation.schemas import StandardResponse

# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/authentication",
    "tags": ["Authentication"],
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
                                "method": "POST",
                                "path": "/api/v1/authentication",
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
                                "method": "POST",
                                "path": "/api/v1/authentication",
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
                                "method": "DELETE",
                                "path": "/api/v1/authentication",
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
                                "path": "/api/v1/authentication",
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
                                "method": "POST",
                                "path": "/api/v1/authentication",
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
                                "method": "DELETE",
                                "path": "/api/v1/authentication",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.VALIDATION_ERROR.value,
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
                            "summary": "The server received an invalid response from the upstream server while acting as a gateway or proxy.",
                            "value": {
                                "code": 502,
                                "method": "POST",
                                "path": "/api/v1/authentication",
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
                            "summary": "The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server.",
                            "value": {
                                "code": 504,
                                "method": "POST",
                                "path": "/api/v1/authentication",
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
login_docs = {
    "summary": "Endpoint to login a user.",
    "description": (
        "Authenticate a user and initiate a login session. "
        "Authentication tokens are returned via HttpOnly cookies."
    ),
    "dependencies": [Security(no_authentication)],
    "response_description": (
        "Successful authentication. Access/refresh tokens are set in cookies and "
        "the JSON body returns a minimal confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LoginResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful login response (cookies + minimal JSON body)",
            "model": LoginResponse,
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Returned multiple times to set `token_type`, `access_token`, "
                        "and `refresh_token` cookies."
                    ),
                    "schema": {"type": "string"},
                    "example": "access_token=<token>; HttpOnly; Path=/; SameSite=lax",
                }
            },
            "content": {
                "application/json": {
                    "examples": {
                        "Login Success": {
                            "summary": "Minimal login response body",
                            "value": {"message": ResponseMessages.LOGIN_SUCCESS.value},
                        }
                    }
                }
            },
        },
    },
}


refresh_docs = {
    "summary": "Endpoint to refresh authentication tokens.",
    "description": (
        "Validates the `refresh_token` from HttpOnly cookies using `refresh_tokens` "
        "security dependency, then rotates and sets new `token_type`, `access_token`, "
        "and `refresh_token` cookies."
    ),
    "dependencies": [Security(authenticate_refresh)],
    "response_description": (
        "Successful token refresh. New access/refresh tokens and token type are set "
        "in cookies, and the JSON body returns a refresh confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LoginResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful refresh response (cookies + minimal JSON body)",
            "model": StandardResponse[LoginResponse],
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Returned multiple times to set `token_type`, `access_token`, "
                        "and `refresh_token` cookies."
                    ),
                    "schema": {"type": "string"},
                    "example": "access_token=<token>; HttpOnly; Path=/; SameSite=lax",
                }
            },
            "content": {
                "application/json": {
                    "examples": {
                        "Refresh Success": {
                            "summary": "Refresh token generated successfully",
                            "value": {
                                "code": 200,
                                "method": "PATCH",
                                "path": "/api/v1/authentication/refresh/",
                                "timestamp": "2026-03-15T23:14:46.555200Z",
                                "details": {
                                    "message": ResponseMessages.SUCCESS.value,
                                    "data": {
                                        "message": ResponseMessages.REFRESH_SUCCESS.value
                                    },
                                },
                            },
                        }
                    }
                }
            },
        },
    },
}

logout_docs = {
    "summary": "Endpoint to logout a user.",
    "description": (
        "Invalidates the authenticated session and removes authentication cookies. "
        "The endpoint requires a valid authenticated user."
    ),
    "dependencies": [Security(authenticate_logout)],
    "response_description": (
        "Successful logout. Authentication cookies are removed and the JSON body "
        "returns a logout confirmation message."
    ),
    "status_code": HTTPStatus.OK,
    "response_model": LogoutResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful logout response (cookies removed + minimal JSON body)",
            "model": StandardResponse[LogoutResponse],
            "headers": {
                "Set-Cookie": {
                    "description": (
                        "Returned multiple times to clear `token_type`, `access_token`, "
                        "and `refresh_token` cookies."
                    ),
                    "schema": {"type": "string"},
                    "example": 'access_token=""; Max-Age=0; Path=/; HttpOnly; SameSite=lax',
                }
            },
            "content": {
                "application/json": {
                    "examples": {
                        "Logout Success": {
                            "summary": "User logged out successfully",
                            "value": {
                                "code": 200,
                                "method": "PATCH",
                                "path": "/api/v1/authentication/logout/",
                                "timestamp": "2026-03-15T23:14:46.555200Z",
                                "details": {
                                    "message": ResponseMessages.SUCCESS.value,
                                    "data": {
                                        "message": ResponseMessages.LOGOUT_SUCCESS.value
                                    },
                                },
                            },
                        }
                    }
                }
            },
        },
    },
}
