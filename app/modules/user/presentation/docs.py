from http import HTTPStatus

from fastapi import Security

from app.core.security import authenticate_user, no_authentication
from app.modules.shared.application.enums import ResponseMessages, Role
from app.modules.shared.presentation.schemas import StandardResponse
from app.modules.user.application.enums import Gender
from app.modules.user.presentation.schemas import CreateResponse, MeResponse

# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/user",
    "tags": ["User"],
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
                                "path": "/api/v1/user",
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
create_docs = {
    "summary": "Endpoint to create a new user.",
    "description": "Create a new user in the system with the provided details.",
    "dependencies": [Security(no_authentication)],
    "response_description": "The response contains only results metadata without user details.",
    "status_code": HTTPStatus.CREATED,
    "response_model": CreateResponse,
    "include_in_schema": True,
    "responses": {
        201: {
            "description": "Successful Response",
            "model": CreateResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "User Created Successfully": {
                            "summary": "User Created Successfully",
                            "value": {
                                "code": 201,
                                "method": "POST",
                                "path": "/api/v1/user",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.CREATED.value,
                                    "data": {},
                                },
                            },
                        },
                    }
                }
            },
        },
    },
}


me_docs = {
    "summary": "Endpoint to get the details of the authenticated user.",
    "description": "Get the details of the authenticated user.",
    "dependencies": [Security(authenticate_user)],
    "response_description": "The response contains the details of the authenticated user.",
    "status_code": HTTPStatus.OK,
    "response_model": MeResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": MeResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "User Details Retrieved Successfully": {
                            "summary": "User Details Retrieved Successfully",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/api/v1/user/me",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.SUCCESS.value,
                                    "data": {
                                        "first_name": "John",
                                        "last_name": "Doe",
                                        "preferred_name": "Joe",
                                        "gender": Gender.MALE.value,
                                        "birthdate": "1995-01-01",
                                        "email": "johndoe@domain.com",
                                        "phone": "+555472664275",
                                        "role": Role.ADMIN.value,
                                        "created_at": "2024-05-01T12:00:00Z",
                                    },
                                },
                            },
                        }
                    }
                }
            },
        }
    },
}
