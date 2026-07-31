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
from app.modules.key.application.exceptions import KeyException
from app.modules.key.application.mappers import (
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
    rotate_entity_mapper,
    entity_rotate_mapper,
)
from app.modules.key.application.use_cases import KeyUseCases
from app.modules.key.presentation.dependencies import get_key_use_cases
from app.modules.key.presentation.docs import (
    router_docs,
    create_docs,
    get_all_docs,
    get_docs,
    update_docs,
    delete_docs,
    rotate_docs,
)
from app.modules.key.presentation.schemas import (
    CreateRequest,
    CreateKeyResponse,
    GetAllResponse,
    GetResponse,
    KeyPaginationParams,
    RotateKeyResponse,
    UpdateRequest,
)
from app.modules.shared.presentation.schemas import DeleteResponse, UpdateResponse

router = APIRouter(**router_docs)


# CREATE
@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[KeyUseCases, Depends(get_key_use_cases)],
) -> CreateKeyResponse:
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
        logger.opt(exception=e).error("An error occurred in the create key endpoint.")
        raise KeyException()


# READ
@router.get("/", **get_all_docs)
@router.get("", include_in_schema=False)
async def get_all(
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[KeyUseCases, Depends(get_key_use_cases)],
    query_params: Annotated[KeyPaginationParams, Depends()],
) -> GetAllResponse:
    try:
        request_domain, pagination = get_all_entity_mapper(authentication, query_params)
        key_list = await use_case.get_all(request_domain, pagination)
        output = entities_get_all_mapper(key_list, pagination)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the get all keys endpoint.")
        raise KeyException()


@router.get("/{id}/", **get_docs)
@router.get("/{id}", include_in_schema=False)
async def get_by_id(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[KeyUseCases, Depends(get_key_use_cases)],
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
        logger.opt(exception=e).error(
            "An error occurred in the get key by id endpoint."
        )
        raise KeyException()


# UPDATE
@router.patch("/{id}/", **update_docs)
@router.patch("/{id}", include_in_schema=False)
async def update(
    id: UUID,
    payload: UpdateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[KeyUseCases, Depends(get_key_use_cases)],
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
        logger.opt(exception=e).error("An error occurred in the update key endpoint.")
        raise KeyException()


@router.patch("/{id}/rotate/", **rotate_docs)
@router.patch("/{id}/rotate", include_in_schema=False)
async def rotate(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[KeyUseCases, Depends(get_key_use_cases)],
) -> RotateKeyResponse:
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
        logger.opt(exception=e).error("An error occurred in the rotate key endpoint.")
        raise KeyException()


# DELETE
@router.delete("/{id}/", **delete_docs)
@router.delete("/{id}", include_in_schema=False)
async def delete(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[KeyUseCases, Depends(get_key_use_cases)],
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
        logger.opt(exception=e).error("An error occurred in the delete key endpoint.")
        raise KeyException()
