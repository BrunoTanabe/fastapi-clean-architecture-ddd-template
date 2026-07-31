from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import (
    CreateResponse,
    DeleteResponse,
    StandardResponse,
    UpdateResponse,
)
from app.modules.knowledge.presentation.schemas import GetAllResponse

# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/knowledge",
    "tags": ["Knowledge"],
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
                                "path": "/api/v1/knowledge",
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
                                "path": "/api/v1/knowledge",
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
                                "method": "POST",
                                "path": "/api/v1/knowledge",
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
                                "path": "/api/v1/knowledge",
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
        409: {
            "model": StandardResponse,
            "description": "Conflict",
            "content": {
                "application/json": {
                    "examples": {
                        "Conflict": {
                            "summary": "A knowledge base with the provided name already exists.",
                            "value": {
                                "code": 409,
                                "method": "POST",
                                "path": "/api/v1/knowledge",
                                "timestamp": "2025-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.CONFLICT.value,
                                    "data": {
                                        "error": "Knowledge with name 'Machine Learning Fundamentals' already exists."
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
                                "path": "/api/v1/knowledge",
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
                                "method": "POST",
                                "path": "/api/v1/knowledge",
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
                            "summary": "The server received an invalid response from the upstream server while acting as a gateway or proxy.",
                            "value": {
                                "code": 502,
                                "method": "POST",
                                "path": "/api/v1/knowledge",
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
                                "path": "/api/v1/knowledge",
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
# CREATE
create_docs = {
    "summary": "Endpoint to create a new knowledge base.",
    "description": "Create a new knowledge base in the system with the provided name and description.",
    "response_description": "The response contains only results metadata without knowledge base details.",
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
                        "Knowledge Base Created Successfully": {
                            "summary": "Knowledge Base Created Successfully",
                            "value": {
                                "code": 201,
                                "method": "POST",
                                "path": "/api/v1/knowledge",
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

# READ
get_all_docs = {
    "summary": "Endpoint to retrieve all knowledge bases.",
    "description": "Retrieve all active knowledge bases in the system.",
    "response_description": "The response contains a list of knowledge bases with their identifiers, names, and last update timestamps.",
    "status_code": HTTPStatus.OK,
    "response_model": GetAllResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": GetAllResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Knowledge Bases Retrieved Successfully": {
                            "summary": "Knowledge Bases Retrieved Successfully",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/api/v1/knowledge",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RETRIEVED.value,
                                    "data": {
                                        "knowledge_bases": [
                                            {
                                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                                "name": "Machine Learning Fundamentals",
                                                "updated_at": "2025-01-15T10:30:00Z",
                                            },
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

# UPDATE
update_docs = {
    "summary": "Endpoint to update an existing knowledge base.",
    "description": "Update the name and/or description of an existing active knowledge base.",
    "response_description": "The response contains only results metadata without knowledge base details.",
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
                        "Knowledge Base Updated Successfully": {
                            "summary": "Knowledge Base Updated Successfully",
                            "value": {
                                "code": 200,
                                "method": "PATCH",
                                "path": "/api/v1/knowledge/550e8400-e29b-41d4-a716-446655440000",
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
        400: {
            "model": StandardResponse,
            "description": "No Changes",
            "content": {
                "application/json": {
                    "examples": {
                        "No Changes": {
                            "summary": "The submitted values are identical to the stored ones.",
                            "value": {
                                "code": 400,
                                "method": "PATCH",
                                "path": "/api/v1/knowledge/550e8400-e29b-41d4-a716-446655440000",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.BAD_REQUEST.value,
                                    "data": {
                                        "error": "No changes were provided; the knowledge base with id '550e8400-e29b-41d4-a716-446655440000' already has the submitted values."
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
        404: {
            "model": StandardResponse,
            "description": "Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "Not Found": {
                            "summary": "The requested knowledge base was not found.",
                            "value": {
                                "code": 404,
                                "method": "PATCH",
                                "path": "/api/v1/knowledge/550e8400-e29b-41d4-a716-446655440000",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "Knowledge with id '550e8400-e29b-41d4-a716-446655440000' not found."
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

# DELETE
delete_docs = {
    "summary": "Endpoint to delete a knowledge base.",
    "description": "Deactivate an existing knowledge base by its identifier.",
    "response_description": "The response contains only results metadata without knowledge base details.",
    "status_code": HTTPStatus.OK,
    "response_model": DeleteResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": DeleteResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Knowledge Base Deleted Successfully": {
                            "summary": "Knowledge Base Deleted Successfully",
                            "value": {
                                "code": 200,
                                "method": "DELETE",
                                "path": "/api/v1/knowledge/550e8400-e29b-41d4-a716-446655440000",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.DELETED.value,
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
            "description": "Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "Not Found": {
                            "summary": "The requested knowledge base was not found.",
                            "value": {
                                "code": 404,
                                "method": "DELETE",
                                "path": "/api/v1/knowledge/550e8400-e29b-41d4-a716-446655440000",
                                "timestamp": "2025-01-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "Knowledge with id '550e8400-e29b-41d4-a716-446655440000' not found."
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
