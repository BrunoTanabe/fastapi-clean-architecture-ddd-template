from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.health.domain.entities import Health
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.health.presentation.schemas import (
    AlembicVersionResponse,
    HealthResponse,
)


# ENTITY / DTOS
def entity_health_mapper(health: Health) -> HealthResponse:
    return mapper.to(HealthResponse).map(health)


def alembic_entity_mapper(authentication: Authentication) -> Health:
    return Health(user=authentication.user)


def entity_alembic_mapper(health: Health) -> AlembicVersionResponse:
    return AlembicVersionResponse(version=health.alembic_version)


# ENTITY / MODELS
def model_entity_mapper(model: AlembicModel) -> Health:
    return Health(alembic_version=model.version_num)
