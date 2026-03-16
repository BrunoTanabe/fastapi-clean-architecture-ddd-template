from typing import Union

from automapper import mapper

from app.modules.health.domain.entities import Health
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.health.presentation.schemas import (
    HealthResponse,
    AlembicVersionResponse,
)
from app.modules.user.domain.entities import User


# ENTITY / DTOS
async def health_mapper(
    health: Health,
) -> HealthResponse:
    return mapper.to(HealthResponse).map(health)


async def alembic_entity_mapper(
    health: Union[User, Health],
) -> Union[Health, AlembicVersionResponse]:
    if isinstance(health, User):
        return Health(user=health)
    elif isinstance(health, Health):
        return AlembicVersionResponse(version=health.alembic_version)
    else:
        raise ValueError("Health must be either a User or a Health.")


# ENTITY / MODELS
async def model_entity_mapper(
    health: AlembicModel,
) -> Health:
    return Health(alembic_version=health.version_num)
