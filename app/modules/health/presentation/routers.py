from fastapi import APIRouter, Depends
from loguru import logger
from fastapi.responses import RedirectResponse

from app.core.exceptions import StandardException
from app.modules.health.application.use_cases import HealthUseCases
from app.modules.health.domain.mappers import domain_to_health_response
from app.modules.health.presentation.dependencies import get_health_use_cases
from app.modules.health.presentation.docs import (
    router_docs,
    check_docs,
    redirect_root_docs,
)
from app.modules.health.presentation.exceptions import HealthException
from app.modules.health.presentation.schemas import HealthCheckResponse

router = APIRouter(**router_docs)


@router.get("/health", **check_docs)
async def check(
    use_case: HealthUseCases = Depends(get_health_use_cases),
) -> HealthCheckResponse:
    try:
        response_domain = await use_case.check()
        output = domain_to_health_response(response_domain)

        return output
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the health_check endpoint.")
        raise HealthException()


@router.get("/", **redirect_root_docs)
async def redirect_root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
