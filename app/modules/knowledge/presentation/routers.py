from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.security import authenticate_manager
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.application.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.knowledge.application.use_cases import KnowledgeUseCases
from app.modules.authentication.domain.entities import Authentication
from app.modules.knowledge.application.mappers import (
    create_entity_mapper,
    entity_create_mapper,
    delete_entity_mapper,
    entity_delete_mapper,
    entities_get_all_mapper,
    get_all_entity_mapper,
    update_entity_mapper,
    entity_update_mapper,
)
from app.modules.knowledge.presentation.dependencies import get_knowledge_use_cases
from app.modules.knowledge.presentation.docs import (
    router_docs,
    create_docs,
    delete_docs,
    get_all_docs,
    update_docs,
)
from app.modules.knowledge.application.exceptions import KnowledgeException
from app.modules.knowledge.presentation.schemas import (
    CreateRequest,
    GetAllResponse,
    KnowledgePaginationParams,
    UpdateRequest,
)
from app.modules.shared.presentation.schemas import (
    CreateResponse,
    DeleteResponse,
    UpdateResponse,
)

router = APIRouter(**router_docs)


# CREATE
@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_manager)],
    use_case: Annotated[KnowledgeUseCases, Depends(get_knowledge_use_cases)],
) -> CreateResponse:
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
        logger.opt(exception=e).error(
            "An error occurred in the create knowledge endpoint."
        )
        raise KnowledgeException()


# READ
@router.get("/", **get_all_docs)
@router.get("", include_in_schema=False)
async def get_all(
    authentication: Annotated[Authentication, Depends(authenticate_manager)],
    use_case: Annotated[KnowledgeUseCases, Depends(get_knowledge_use_cases)],
    query_params: Annotated[KnowledgePaginationParams, Depends()],
) -> GetAllResponse:
    try:
        request_domain, pagination = get_all_entity_mapper(authentication, query_params)
        knowledge_list = await use_case.get_all(request_domain, pagination)
        output = entities_get_all_mapper(knowledge_list, pagination)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the get all knowledge bases endpoint."
        )
        raise KnowledgeException()


# UPDATE
@router.patch("/{id}/", **update_docs)
@router.patch("/{id}", include_in_schema=False)
async def update(
    id: UUID,
    payload: UpdateRequest,
    authentication: Annotated[Authentication, Depends(authenticate_manager)],
    use_case: Annotated[KnowledgeUseCases, Depends(get_knowledge_use_cases)],
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
        logger.opt(exception=e).error(
            "An error occurred in the update knowledge endpoint."
        )
        raise KnowledgeException()


# DELETE
@router.delete("/{id}/", **delete_docs)
@router.delete("/{id}", include_in_schema=False)
async def delete(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_manager)],
    use_case: Annotated[KnowledgeUseCases, Depends(get_knowledge_use_cases)],
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
        logger.opt(exception=e).error(
            "An error occurred in the delete knowledge endpoint."
        )
        raise KnowledgeException()
