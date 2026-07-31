from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from loguru import logger

from app.core.security import authenticate_admin, no_authentication
from app.modules.authentication.domain.entities import Authentication
from app.modules.health.application.exceptions import (
    HealthException,
)
from app.modules.health.application.mappers import (
    alembic_entity_mapper,
    entity_alembic_mapper,
    entity_health_mapper,
)
from app.modules.health.application.use_cases import HealthUseCases
from app.modules.health.presentation.dependencies import get_health_use_cases
from app.modules.health.presentation.docs import (
    alembic_version_docs,
    health_docs,
    redirect_docs,
    router_docs,
)
from app.modules.health.presentation.schemas import (
    AlembicVersionResponse,
    HealthResponse,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError

router = APIRouter(**router_docs)


@router.get("/health/", **health_docs)
@router.get("/health", include_in_schema=False)
async def health(
    _: Annotated[None, Depends(no_authentication)],
    use_case: Annotated[HealthUseCases, Depends(get_health_use_cases)],
) -> HealthResponse:
    try:
        response_domain = use_case.health()
        output = entity_health_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the health router.")
        raise HealthException()


@router.get("/", **redirect_docs)
async def redirect(
    _: Annotated[None, Depends(no_authentication)],
) -> RedirectResponse:
    try:
        return RedirectResponse(url="/docs")
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the redirect_root router.")
        raise HealthException()


@router.get("/api/v1/alembic-version/", **alembic_version_docs)
@router.get("/api/v1/alembic-version", include_in_schema=False)
async def alembic_version(
    authentication: Annotated[Authentication, Depends(authenticate_admin)],
    use_case: Annotated[HealthUseCases, Depends(get_health_use_cases)],
) -> AlembicVersionResponse:
    try:
        request_domain = alembic_entity_mapper(authentication)
        response_domain = await use_case.alembic_version(request_domain)
        output = entity_alembic_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the get alembic version endpoint."
        )
        raise HealthException()
