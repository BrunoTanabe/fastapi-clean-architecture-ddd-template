from loguru import logger

from app.modules.health.application.exceptions import (
    HealthException,
    MigrationNotInitiatedException,
)
from app.modules.health.application.interfaces import IHealthRepository
from app.modules.health.domain.entities import Health
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError


class HealthUseCases:
    def __init__(
        self,
        repository: IHealthRepository,
    ) -> None:
        self.repository = repository

    @staticmethod
    def health() -> Health:
        try:
            logger.debug("Starting health check use case.")

            health: Health = Health()

            logger.debug("Health check use case completed successfully.")
            return health
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the health check use case."
            )
            raise HealthException()

    async def alembic_version(self, health: Health) -> Health:
        try:
            logger.debug(
                f"Starting get alembic version use case for the admin {health.user.id}."
            )

            alembic_db: Health | None = await self.repository.get_alembic_version(
                health
            )

            if not health or not alembic_db or not alembic_db.alembic_version:
                logger.info(
                    f"Alembic migration version not found in database for admin {health.user.id}. Alembic migration might not have been initiated."
                )
                raise MigrationNotInitiatedException()

            health.alembic_version = alembic_db.alembic_version

            logger.debug(
                f"Get alembic version use case completed successfully for the admin {health.user.id}. Alembic migration version: {health.alembic_version}."
            )
            return health
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the alembic_version use case."
            )
            raise HealthException()
