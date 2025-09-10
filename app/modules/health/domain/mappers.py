from app.modules.health.application.enums import HealthType
from app.modules.health.presentation.schemas import HealthCheckResponse


def domain_to_health_response(
    status: HealthType,
) -> HealthCheckResponse:
    return HealthCheckResponse(
        status=status,
    )
