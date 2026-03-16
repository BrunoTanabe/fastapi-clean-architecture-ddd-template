from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.health.application.interfaces import IHealthRepository
from app.modules.health.domain.entities import Health
from app.modules.health.domain.mappers import model_entity_mapper
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.health.presentation.exceptions import HealthException
from app.modules.shared.presentation.exceptions import StandardException


class PostgresHealthRepository(IHealthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_alembic_version(self, health: Health) -> Optional[Health]:
        try:
            logger.info(
                f"Getting alembic migration version from database for admin {health.user.email.__str__()}."
            )

            statement = select(AlembicModel)

            result = await self.session.execute(statement)
            alembic_model: Optional[AlembicModel] = result.scalar_one_or_none()

            if alembic_model is None:
                logger.info(
                    f"No alembic migration version found in database for admin {health.user.email.__str__()}."
                )
                return None

            health: Health = await model_entity_mapper(alembic_model)

            logger.info(
                f"Alembic migration version {health.alembic_version} retrieved successfully from database."
            )
            return health
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get alembic version repository."
            )
            raise HealthException()
