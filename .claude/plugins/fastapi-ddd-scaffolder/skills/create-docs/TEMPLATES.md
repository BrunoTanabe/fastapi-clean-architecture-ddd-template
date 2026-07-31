# OpenAPI Documentation Templates

Mirrors `app/modules/key/presentation/docs.py`. Copy the shape verbatim and change only the module
name, prefix, paths, schemas, and examples.

## Contents

- [File header](#file-header)
- [router_docs](#router_docs)
- [Error entry shape](#error-entry-shape)
- [Create endpoint](#create-endpoint)
- [Paginated list endpoint](#paginated-list-endpoint)
- [Get by id endpoint](#get-by-id-endpoint)
- [Update endpoint](#update-endpoint)
- [Delete endpoint](#delete-endpoint)
- [Standard error codes](#standard-error-codes)

## File header

```python
from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import (
    DeleteResponse,
    StandardResponse,
    UpdateResponse,
)
from app.modules.{module}.presentation.schemas import (
    Create{Entity}Response,
    GetAllResponse,
    GetResponse,
)
```

## router_docs

```python
# MODULE DOCS
router_docs = {
    "prefix": "/api/v1/{module-kebab}",
    "tags": ["{Module}"],
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
                                "path": "/api/v1/{module-kebab}",
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
        # 401, 403, 405, 422, 500, 502, 504 follow the same shape
    },
}
```

The `tags` value must match the name registered in `custom_openapi()` in `app/app.py`.

## Error entry shape

Every entry follows this template. Only `code`, `method`, `path`, the `ResponseMessages` member,
and the error text change.

```python
        {status}: {
            "model": StandardResponse,
            "description": "{Reason Phrase}",
            "content": {
                "application/json": {
                    "examples": {
                        "{Reason Phrase}": {
                            "summary": "{One sentence describing when this happens.}",
                            "value": {
                                "code": {status},
                                "method": "{METHOD}",
                                "path": "/api/v1/{module-kebab}",
                                "timestamp": "2026-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.{MEMBER}.value,
                                    "data": {"error": "{User-facing explanation.}"},
                                },
                            },
                        },
                    },
                },
            },
        },
```

The `value` is the full `StandardResponse` envelope that
`ResponseFormattingMiddleware` produces — an example without it teaches clients the wrong shape.

## Create endpoint

```python
# ENDPOINT DOCS
create_docs = {
    "summary": "Create a new {entity}",
    "description": (
        "Creates a new {entity} and returns the generated secret. "
        "The secret is returned only once and cannot be retrieved again."
    ),
    "response_description": "The {entity} was created successfully.",
    "status_code": HTTPStatus.CREATED,
    "response_model": Create{Entity}Response,
    "include_in_schema": True,
    "responses": {
        201: {
            "model": Create{Entity}Response,
            "description": "Created",
            "content": {
                "application/json": {
                    "examples": {
                        "Created": {
                            "summary": "The {entity} was created successfully.",
                            "value": {
                                "code": 201,
                                "method": "POST",
                                "path": "/api/v1/{module-kebab}",
                                "timestamp": "2026-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.CREATED.value,
                                    "data": {"api_key": "sk_live_9f2c…"},
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
                            "summary": "A {entity} with the same name already exists.",
                            "value": {
                                "code": 409,
                                "method": "POST",
                                "path": "/api/v1/{module-kebab}",
                                "timestamp": "2026-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.CONFLICT.value,
                                    "data": {"error": "{Entity} with name 'CI pipeline' already exists."},
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}
```

Use obviously fake secrets in examples. `status_code` uses `HTTPStatus.CREATED`, never `201`.

## Paginated list endpoint

```python
get_all_docs = {
    "summary": "List {entity_plural}",
    "description": (
        "Returns a paginated list of active {entity_plural}. "
        "Supports page, limit, sort_by, and sort_order query parameters."
    ),
    "response_description": "The {entity_plural} were retrieved successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": GetAllResponse,
    "include_in_schema": True,
    "responses": {
        200: {
            "model": GetAllResponse,
            "description": "OK",
            "content": {
                "application/json": {
                    "examples": {
                        "OK": {
                            "summary": "The {entity_plural} were retrieved successfully.",
                            "value": {
                                "code": 200,
                                "method": "GET",
                                "path": "/api/v1/{module-kebab}",
                                "timestamp": "2026-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.RETRIEVED.value,
                                    "data": {
                                        "items": [],
                                        "pagination": {
                                            "total": 0,
                                            "page": 1,
                                            "limit": 20,
                                            "total_pages": 0,
                                            "has_next": False,
                                            "has_prev": False,
                                        },
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
```

A list endpoint has no 404 — an empty page is a success.

## Get by id endpoint

```python
get_docs = {
    "summary": "Get a {entity} by identifier",
    "description": "Returns the full representation of a single active {entity}.",
    "response_description": "The {entity} was retrieved successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": GetResponse,
    "include_in_schema": True,
    "responses": {
        200: { ... },
        404: {
            "model": StandardResponse,
            "description": "Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "Not Found": {
                            "summary": "No active {entity} exists with the given identifier.",
                            "value": {
                                "code": 404,
                                "method": "GET",
                                "path": "/api/v1/{module-kebab}/{id}",
                                "timestamp": "2026-07-15T12:34:56Z",
                                "details": {
                                    "message": ResponseMessages.RESOURCE_NOT_FOUND.value,
                                    "data": {
                                        "error": "{Entity} with id '550e8400-e29b-41d4-a716-446655440000' not found."
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
```

The 404 example text should match what the exception class actually produces.

## Update endpoint

```python
update_docs = {
    "summary": "Update a {entity}",
    "description": (
        "Partially updates a {entity}. Omitted fields are left unchanged; "
        "send null to clear a nullable field."
    ),
    "response_description": "The {entity} was updated successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": UpdateResponse,
    "include_in_schema": True,
    "responses": {
        200: { ... },
        400: {
            # {Entity}NotModifiedException — no effective change was submitted
        },
        404: { ... },
    },
}
```

Documenting the omit-versus-null distinction is what makes the `UNSET` protocol usable by clients.

## Delete endpoint

```python
delete_docs = {
    "summary": "Revoke a {entity}",
    "description": (
        "Soft-deletes the {entity}. It stops being usable immediately and no longer "
        "appears in listings, but the record is retained for auditing."
    ),
    "response_description": "The {entity} was deleted successfully.",
    "status_code": HTTPStatus.OK,
    "response_model": DeleteResponse,
    "include_in_schema": True,
    "responses": {
        200: { ... },
        404: { ... },
    },
}
```

Say that the delete is soft — a client that expects a hard delete will otherwise be surprised by
the audit trail.

## Standard error codes

| Code | `ResponseMessages` member | When |
|------|---------------------------|------|
| 400 | `VALIDATION_ERROR` | Malformed request or a failed domain rule |
| 401 | `UNAUTHORIZED_ERROR` | Missing, invalid, revoked, or expired credential |
| 403 | `AUTHORIZATION_ERROR` | Authenticated but not permitted, or path not in the tier |
| 405 | `METHOD_NOT_ALLOWED` | Method not supported on the path |
| 409 | `CONFLICT` | Natural-key conflict |
| 422 | `VALIDATION_ERROR` | Pydantic schema validation failure |
| 500 | `INTERNAL_ERROR` | Unexpected failure |
| 502 | `BAD_GATEWAY` | Upstream dependency failed |
| 504 | `GATEWAY_TIMEOUT` | Upstream dependency timed out |

400 and 422 are distinct: 422 is FastAPI rejecting the payload before the handler runs; 400 is a
`DomainException` or a business-rule failure from inside it.
