from http import HTTPStatus
from fastapi.responses import RedirectResponse

from app.core.enums import ResponseMessages
from app.core.schemas import StandardResponse
from app.modules.health.presentation.schemas import HealthResponse

# MODULE DOCS
router_docs = {
    "prefix": "",
    "tags": ["Health"],
    "responses": {
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
                                "path": "/",
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
                                "path": "/",
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
                                "path": "/",
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
    },
}

# ENDPOINT DOCS
health_docs = {
    "summary": "Endpoint for checking the health of the application",
    "description": "This endpoint is used to verify that the application is running and healthy. It returns a simple status message.",
    "response_description": "Returns a status message indicating the health of the application.",
    "status_code": HTTPStatus.OK,
    "response_model": HealthResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful analysis of infractor eligibility",
            "model": StandardResponse[HealthResponse],
            "content": {
                "application/json": {
                    "examples": {
                        "System Working": {
                            "summary": "System working correctly",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/health",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.SUCCESS.value,
                                    "data": {"status": "OK"},
                                },
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
    "response_model": None,
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
                            "value": {
                                "code": 308,
                                "method": "GET",
                                "path": "/",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.REDIRECT.value,
                                    "data": {"url": "/docs"},
                                },
                            },
                        },
                    }
                }
            },
        }
    },
}
