from http import HTTPStatus

from fastapi import Security

from app.core.schemas import StandardResponse
from app.core.security import api_key_auth
from app.modules.example.presentation.schemas import ExampleResponse


example_docs = {
    "prefix": "/api/v1/example",
    "tags": ["example"],
    "dependencies": [Security(api_key_auth)],
    "responses": {
        401: {
            "model": StandardResponse,
            "description": "Authentication error",
            "content": {
                "application/json": {
                    "example": {
                        "code": 401,
                        "method": "GET",
                        "path": "/api/v1/example",
                        "timestamp": "2025-07-15T12:34:56Z",
                        "details": {
                            "message": "Authentication error",
                            "data": {"error": "Invalid or missing API key."},
                        },
                    }
                }
            },
        },
        422: {
            "model": StandardResponse,
            "description": "Form validation error",
            "content": {
                "application/json": {
                    "example": {
                        "code": 422,
                        "method": "POST",
                        "path": "/api/v1/example",
                        "timestamp": "2025-07-15T12:34:56Z",
                        "details": {
                            "message": "Form validation error",
                            "data": {"field": "Error message for the field."},
                        },
                    }
                }
            },
        },
        500: {
            "model": StandardResponse,
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "code": 500,
                        "method": "DELETE",
                        "path": "/api/v1/example",
                        "timestamp": "2025-07-15T12:34:56Z",
                        "details": {
                            "message": "Internal Server Error",
                            "data": {"error": "An unexpected error occurred."},
                        },
                    }
                }
            },
        },
    },
}

example_request_docs = {
    "summary": "Endpoint Example",
    "description": "This endpoint returns a greeting message.",
    "response_description": "Returns a greeting message.",
    "status_code": HTTPStatus.OK,
    "responses": {
        200: {
            "description": "Successful response",
            "model": StandardResponse[ExampleResponse],
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "method": "POST",
                        "path": "/api/v1/example/",
                        "timestamp": "2025-01-15T10:30:00Z",
                        "details": {
                            "message": "Request processed successfully.",
                            "data": {
                                "message": "Hello Bruno Tanabe!",
                            },
                        },
                    }
                }
            },
        }
    },
}
