from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.health.application.exceptions import HealthException
from app.modules.health.application.interfaces import IHealthRepository
from app.modules.health.application.mappers import model_entity_mapper
from app.modules.health.domain.entities import Health
from app.modules.health.infrastructure.models import AlembicModel
from app.modules.shared.application.exceptions import StandardException


class PostgresHealthRepository(IHealthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_alembic_version(self, health: Health) -> Health | None:
        try:
            logger.info(
                f"Getting alembic migration version from database for admin {health.user.id}."
            )

            statement = select(AlembicModel)

            result = await self.session.execute(statement)
            alembic_model: AlembicModel | None = result.scalar_one_or_none()

            if alembic_model is None:
                logger.info(
                    f"No alembic migration version found in database for admin {health.user.id}."
                )
                return None

            health.alembic_version = model_entity_mapper(alembic_model).alembic_version

            logger.info(
                f"Alembic migration version {health.alembic_version} found in database for admin {health.user.id}."
            )
            return health
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get alembic version repository."
            )
            raise HealthException()
