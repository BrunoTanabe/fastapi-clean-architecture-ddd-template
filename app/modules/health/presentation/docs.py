from http import HTTPStatus
from fastapi.responses import RedirectResponse

from app.core.schemas import StandardResponse
from app.modules.health.presentation.schemas import HealthCheckResponse

router_docs = {
    "prefix": "",
    "tags": ["Health Check"],
    "responses": {
        401: {
            "model": StandardResponse,
            "description": "Authentication error",
            "content": {
                "application/json": {
                    "example": {
                        "code": 401,
                        "method": "GET",
                        "path": "/",
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
                        "path": "/",
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
                        "path": "/",
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

health_check_docs = {
    "summary": "Endpoint for checking the health of the application",
    "description": "This endpoint is used to verify that the application is running and healthy. It returns a simple status message.",
    "response_description": "Returns a status message indicating the health of the application.",
    "status_code": HTTPStatus.OK,
    "include_in_schema": False,
    "responses": {
        200: {
            "description": "Successful analysis of infractor eligibility",
            "model": StandardResponse[HealthCheckResponse],
            "content": {
                "application/json": {
                    "examples": {
                        "System Working": {
                            "summary": "System working correctly",
                            "code": 200,
                            "method": "GET",
                            "path": "/healthz",
                            "timestamp": "2025-01-15T10:30:00Z",
                            "details": {
                                "message": "Request processed successfully",
                                "data": {"status": "OK"},
                            },
                        },
                    }
                }
            },
        }
    },
}

redirect_root_docs = {
    "summary": "Redirects root path to FastAPI documentation",
    "description": "This endpoint redirects the root path to the FastAPI documentation page.",
    "response_description": "Redirects to the FastAPI documentation page.",
    "status_code": HTTPStatus.PERMANENT_REDIRECT,
    "response_class": RedirectResponse,
    "include_in_schema": False,
    "responses": {
        308: {
            "description": "Permanent redirect to FastAPI documentation",
            "content": {
                "application/json": {
                    "examples": {
                        "Redirect to Docs": {
                            "summary": "Redirects to FastAPI documentation",
                            "code": 308,
                            "method": "GET",
                            "path": "/",
                            "timestamp": "2025-01-15T10:30:00Z",
                            "details": {
                                "message": "Redirecting to FastAPI documentation",
                                "data": {"url": "/docs"},
                            },
                        },
                    }
                }
            },
        }
    },
}
