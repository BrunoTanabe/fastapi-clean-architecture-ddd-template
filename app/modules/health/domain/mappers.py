from app.modules.health.application.enums import HealthType
from app.modules.health.presentation.schemas import HealthResponse


def domain_to_health_response(
    status: HealthType,
) -> HealthResponse:
    return HealthResponse(
        status=status,
    )
