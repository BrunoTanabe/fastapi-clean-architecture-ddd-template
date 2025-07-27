from fastapi import APIRouter
from loguru import logger
from fastapi.responses import RedirectResponse

from app.core.exceptions import StandardException
from app.modules.health.application.enums import HealthType
from app.modules.health.presentation.docs import (
    router_docs,
    health_check_docs,
    redirect_root_docs,
)
from app.modules.health.presentation.exceptions import HealthCheckStandardException
from app.modules.health.presentation.schemas import HealthCheckResponse

router = APIRouter(**router_docs)


@router.get("/healthz", **health_check_docs)
async def health_check() -> HealthCheckResponse:
    try:
        output = HealthCheckResponse(
            status=HealthType.OK,
        )

        return output
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the health_check endpoint.")
        raise HealthCheckStandardException()


@router.get("/", **redirect_root_docs)
async def redirect_root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
