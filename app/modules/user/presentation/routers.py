from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.security import authenticate_user, no_authentication
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.application.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.user.application.use_cases import UserUseCases
from app.modules.user.application.mappers import (
    create_entity_mapper,
    entity_create_mapper,
    me_entity_mapper,
    entity_me_mapper,
)
from app.modules.user.presentation.dependencies import get_user_use_cases
from app.modules.user.presentation.docs import router_docs, create_docs, me_docs
from app.modules.user.application.exceptions import UserException
from app.modules.user.presentation.schemas import (
    CreateRequest,
    CreateResponse,
    MeResponse,
)

router = APIRouter(**router_docs)


# CREATE
@router.post("/", **create_docs)
@router.post("", include_in_schema=False)
async def create(
    payload: CreateRequest,
    _: Annotated[None, Depends(no_authentication)],
    use_case: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> CreateResponse:
    try:
        request_domain = create_entity_mapper(payload)
        response_domain = await use_case.create(request_domain)
        output = entity_create_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the create user endpoint.")
        raise UserException()


# READ
@router.get("/me/", **me_docs)
@router.get("/me", include_in_schema=False)
async def me(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    use_case: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> MeResponse:
    try:
        request_domain = me_entity_mapper(authentication)
        response_domain = await use_case.me(request_domain)
        output = entity_me_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the me endpoint.")
        raise UserException()
