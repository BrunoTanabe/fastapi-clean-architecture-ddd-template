from app.modules.health.application.use_cases import HealthUseCases


def get_health_use_cases() -> HealthUseCases:
    return HealthUseCases()
