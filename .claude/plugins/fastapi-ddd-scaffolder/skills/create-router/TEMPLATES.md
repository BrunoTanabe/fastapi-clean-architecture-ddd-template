# Router Templates

Every block mirrors `app/modules/key/presentation/routers.py`.

## Contents

- [File header](#file-header)
- [Create](#create)
- [Paginated list](#paginated-list)
- [Get by id](#get-by-id)
- [Partial update](#partial-update)
- [Sub-path action](#sub-path-action)
- [Delete](#delete)
- [Public endpoint](#public-endpoint)
- [WebSocket route](#websocket-route)
- [Allowlist rules](#allowlist-rules)

## File header

```python
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.security import authenticate_admin
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.application.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.{module}.application.exceptions import {Module}Exception
from app.modules.{module}.application.mappers import (
    create_entity_mapper,
    entity_create_mapper,
    entities_get_all_mapper,
    entity_get_mapper,
    entity_update_mapper,
    entity_delete_mapper,
    get_all_entity_mapper,
    get_entity_mapper,
    update_entity_mapper,
    delete_entity_mapper,
)
from app.modules.{module}.application.use_cases import {Module}UseCases
from app.modules.{module}.presentation.dependencies import get_{module}_use_cases
from app.modules.{module}.presentation.docs import (
    router_docs,
    create_docs,
    get_all_docs,
    get_docs,
    update_docs,
    delete_docs,
)
from app.modules.{module}.presentation.schemas import (
    CreateRequest,
    Create{Entity}Response,
    GetAllResponse,
    GetResponse,
    {Entity}PaginationParams,
    UpdateRequest,
)
from app.modules.shared.presentation.schemas import DeleteResponse, UpdateResponse

router = APIRouter(**router_docs)
```

## Create

```python
# CREATE
@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
) -> Create{Entity}Response:
    try:
        request_domain = create_entity_mapper(payload, authentication)
        response_domain = await use_case.create(request_domain)
        output = entity_create_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the create {module} endpoint.")
        raise {Module}Exception()
```

Parameter order is fixed: `payload`, then `authentication`, then `use_case`, then optional
`query_params`. Path parameters come first of all.

## Paginated list

```python
# READ
@router.get("/", **get_all_docs)
@router.get("", include_in_schema=False)
async def get_all(
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
    query_params: Annotated[{Entity}PaginationParams, Depends()],
) -> GetAllResponse:
    try:
        request_domain, pagination = get_all_entity_mapper(authentication, query_params)
        entity_list = await use_case.get_all(request_domain, pagination)
        output = entities_get_all_mapper(entity_list, pagination)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the get all {entity_plural} endpoint.")
        raise {Module}Exception()
```

The request mapper returns a tuple, so the handler unpacks it and passes both parts through.

## Get by id

```python
@router.get("/{id}/", **get_docs)
@router.get("/{id}", include_in_schema=False)
async def get_by_id(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
) -> GetResponse:
    try:
        request_domain = get_entity_mapper(id, authentication)
        response_domain = await use_case.get_by_id(request_domain)
        output = entity_get_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the get {module} by id endpoint.")
        raise {Module}Exception()
```

`id: UUID` makes FastAPI reject a malformed identifier with a 422 before the handler body runs.

## Partial update

```python
# UPDATE
@router.patch("/{id}/", **update_docs)
@router.patch("/{id}", include_in_schema=False)
async def update(
    id: UUID,
    payload: UpdateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
) -> UpdateResponse:
    try:
        request_domain = update_entity_mapper(id, payload, authentication)
        response_domain = await use_case.update(request_domain)
        output = entity_update_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the update {module} endpoint.")
        raise {Module}Exception()
```

Partial updates are `PATCH`, never `PUT` — the `UNSET` protocol depends on omitted fields being
meaningful.

## Sub-path action

An operation that is neither plain CRUD nor a separate resource. Both slash forms still apply.

```python
@router.patch("/{id}/rotate/", **rotate_docs)
@router.patch("/{id}/rotate", include_in_schema=False)
async def rotate(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
) -> Rotate{Entity}Response:
    try:
        request_domain = rotate_entity_mapper(id, authentication)
        response_domain = await use_case.rotate(request_domain)
        output = entity_rotate_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the rotate {module} endpoint.")
        raise {Module}Exception()
```

## Delete

```python
# DELETE
@router.delete("/{id}/", **delete_docs)
@router.delete("/{id}", include_in_schema=False)
async def delete(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
) -> DeleteResponse:
    try:
        request_domain = delete_entity_mapper(id, authentication)
        response_domain = await use_case.delete(request_domain)
        output = entity_delete_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the delete {module} endpoint.")
        raise {Module}Exception()
```

Deletion is a soft delete; the response is still 200 with a `DeleteResponse`, not 204.

## Public endpoint

```python
@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    _: Annotated[None, Depends(no_authentication)],
    use_case: Annotated[{Module}UseCases, Depends(get_{module}_use_cases)],
) -> CreateResponse:
    ...
```

`no_authentication` is not a no-op — it checks the path against `SECURITY_NO_AUTH_PATHS`. A public
endpoint missing from that tier is rejected.

## WebSocket route

The `GET` decoy documents the channel in OpenAPI and raises immediately; the real handlers are the
two `@router.websocket` decorators. Reference: `websocket/presentation/routers.py`.

```python
@router.get("/connect/", **connect_docs)
async def connect_docs_only() -> None:
    raise WebSocketDocumentationOnlyException()


@router.websocket("/connect/")
@router.websocket("/connect")
async def connect(
    websocket: WebSocket,
    authentication: Annotated[Authentication, Depends(authenticate_websocket)],
    use_case: Annotated[WebSocketUseCases, Depends(get_websocket_use_cases)],
) -> None: ...
```

## Allowlist rules

In `app/core/settings.py`, grouped under an uppercase module comment, both forms per rule:

```python
# {MODULE}
(_path_rule("/api/v1/{module}/", "POST"),)
(_path_rule("/api/v1/{module}", "POST"),)
(_path_rule("/api/v1/{module}/", "GET"),)
(_path_rule("/api/v1/{module}", "GET"),)
(_path_rule("/api/v1/{module}/{id}/", "GET"),)
(_path_rule("/api/v1/{module}/{id}", "GET"),)
(_path_rule("/api/v1/{module}/{id}/", "PATCH"),)
(_path_rule("/api/v1/{module}/{id}", "PATCH"),)
(_path_rule("/api/v1/{module}/{id}/rotate/", "PATCH"),)
(_path_rule("/api/v1/{module}/{id}/rotate", "PATCH"),)
(_path_rule("/api/v1/{module}/{id}/", "DELETE"),)
(_path_rule("/api/v1/{module}/{id}", "DELETE"),)
```

`{id}` is matched as `(?P<id>[^/]+)`, so a parameter can never span a `/`. Methods are uppercase
and compared exactly.
