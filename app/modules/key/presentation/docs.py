from http import HTTPStatus

from app.modules.key.presentation.schemas import (
    CreateKeyResponse,
    GetAllResponse,
    GetResponse,
    RotateKeyResponse,
)
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import (
    DeleteResponse,
    StandardResponse,
    UpdateResponse,
)

# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/key",
    "tags": ["Key"],
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T12:34:56Z",
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
    "summary": "Endpoint to create a new API key (admin only).",
    "description": (
        "Create a new API key owned by the authenticated administrator. The raw secret is "
        "returned in the response exactly once and is never stored or shown again — only its "
        "HMAC-SHA256 hash is persisted. Requires an authenticated session with the admin role: "
        "unauthenticated clients receive 401 and non-admin users receive 403."
    ),
    "response_description": "The response contains the created key's metadata and the raw secret, returned only once.",
    "status_code": HTTPStatus.CREATED,
    "response_model": CreateKeyResponse,
    "include_in_schema": True,
    "responses": {
        201: {
            "description": "Successful Response",
            "model": CreateKeyResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "API Key Created Successfully": {
                            "summary": "API Key Created Successfully",
                            "value": {
                                "code": 201,
                                "method": "POST",
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.CREATED.value,
                                    "data": {
                                        "api_key": "tk_live_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5aB3d",
                                    },
                                },
                            },
                        },
                    }
                }
            },
        },
        403: {
            "description": "Forbidden",
            "model": StandardResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "Insufficient Role": {
                            "summary": "Authenticated user does not have the admin role.",
                            "value": {
                                "code": 403,
                                "method": "POST",
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.AUTHORIZATION_ERROR.value,
                                    "data": {
                                        "error": "Only administrators can create API keys."
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

# READ
get_all_docs = {
    "summary": "Endpoint to retrieve all API keys (admin only).",
    "description": (
        "Retrieve all active API keys registered in the system, paginated. Requires an "
        "authenticated session with the admin role: unauthenticated clients receive 401 and "
        "non-admin users receive 403."
    ),
    "response_description": "The response contains a paginated list of API keys with their names, descriptions, and creation timestamps.",
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
                        "API Keys Retrieved Successfully": {
                            "summary": "API Keys Retrieved Successfully",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/api/v1/key",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RETRIEVED.value,
                                    "data": {
                                        "api_keys": [
                                            {
                                                "id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                                "name": "CI pipeline",
                                                "description": "Used by the CI pipeline to publish releases.",
                                                "created_at": "2026-07-15T10:30:00Z",
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

# READ
get_docs = {
    "summary": "Endpoint to retrieve a single API key by its identifier (admin only).",
    "description": (
        "Retrieve all stored data of a single API key by its identifier. The secret hash is "
        "never exposed. Requires an authenticated session with the admin role: unauthenticated "
        "clients receive 401 and non-admin users receive 403."
    ),
    "response_description": "The response contains all stored data of the API key, except the secret hash.",
    "status_code": HTTPStatus.OK,
    "response_model": GetResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": GetResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "API Key Retrieved Successfully": {
                            "summary": "API Key Retrieved Successfully",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RETRIEVED.value,
                                    "data": {
                                        "id": "3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                        "name": "CI pipeline",
                                        "description": "Used by the CI pipeline to publish releases.",
                                        "prefix": "iap_",
                                        "last_four": "aB3d",
                                        "expires_at": "2027-01-01T00:00:00Z",
                                        "last_used_at": None,
                                        "created_by": "b16f55f1-e862-4e33-8acf-860506ef4c53",
                                        "updated_by": "b16f55f1-e862-4e33-8acf-860506ef4c53",
                                        "is_active": True,
                                        "created_at": "2026-07-15T10:30:00Z",
                                        "updated_at": "2026-07-15T10:30:00Z",
                                    },
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
                            "summary": "The requested API key was not found.",
                            "value": {
                                "code": 404,
                                "method": "GET",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "API key with id '3f2504e0-4f89-11d3-9a0c-0305e82c3301' not found."
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

# UPDATE
update_docs = {
    "summary": "Endpoint to update an existing API key (admin only).",
    "description": (
        "Update the name and/or description of an existing active API key. Requires an "
        "authenticated session with the admin role: unauthenticated clients receive 401 and "
        "non-admin users receive 403."
    ),
    "response_description": "The response contains only results metadata without API key details.",
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
                        "API Key Updated Successfully": {
                            "summary": "API Key Updated Successfully",
                            "value": {
                                "code": 200,
                                "method": "PATCH",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
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
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.BAD_REQUEST.value,
                                    "data": {
                                        "error": "No changes were provided; the API key with id '3f2504e0-4f89-11d3-9a0c-0305e82c3301' already has the submitted values."
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
                            "summary": "The requested API key was not found.",
                            "value": {
                                "code": 404,
                                "method": "PATCH",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "API key with id '3f2504e0-4f89-11d3-9a0c-0305e82c3301' not found."
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

rotate_docs = {
    "summary": "Endpoint to rotate an existing API key secret (admin only).",
    "description": (
        "Generate a new secret for an existing active API key, revoking the previous one "
        "immediately and without a grace period. Any client still presenting the old secret "
        "starts receiving 401 as soon as this call completes, so coordinate the rollout before "
        "rotating. The new secret is returned exactly once and cannot be recovered afterwards. "
        "Requires an authenticated session with the admin role: unauthenticated clients receive "
        "401 and non-admin users receive 403."
    ),
    "response_description": "The response contains the new raw API key exactly once.",
    "status_code": HTTPStatus.OK,
    "response_model": RotateKeyResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "description": "Successful Response",
            "model": RotateKeyResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "API Key Rotated Successfully": {
                            "summary": "API Key Rotated Successfully",
                            "value": {
                                "code": 200,
                                "method": "PATCH",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301/rotate/",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.UPDATED.value,
                                    "data": {
                                        "api_key": "tk_live_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5K4j"
                                    },
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
                            "summary": "The requested API key was not found.",
                            "value": {
                                "code": 404,
                                "method": "PATCH",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301/rotate/",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "API key with id '3f2504e0-4f89-11d3-9a0c-0305e82c3301' not found."
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
    "summary": "Endpoint to delete an API key (admin only).",
    "description": (
        "Soft-delete (deactivate) an existing active API key by its identifier. The key is marked "
        "inactive and can no longer be used to authenticate. Requires an authenticated session "
        "with the admin role: unauthenticated clients receive 401 and non-admin users receive 403."
    ),
    "response_description": "The response contains only results metadata without API key details.",
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
                        "API Key Deleted Successfully": {
                            "summary": "API Key Deleted Successfully",
                            "value": {
                                "code": 200,
                                "method": "DELETE",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
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
                            "summary": "The requested API key was not found.",
                            "value": {
                                "code": 404,
                                "method": "DELETE",
                                "path": "/api/v1/key/3f2504e0-4f89-11d3-9a0c-0305e82c3301",
                                "timestamp": "2026-07-15T10:30:00Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "API key with id '3f2504e0-4f89-11d3-9a0c-0305e82c3301' not found."
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
