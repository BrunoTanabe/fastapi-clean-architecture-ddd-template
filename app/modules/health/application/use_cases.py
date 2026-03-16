from loguru import logger

from app.modules.health.application.interfaces import IHealthRepository
from app.modules.health.domain.entities import Health
from app.modules.health.presentation.exceptions import (
    HealthException,
    MigrationNotInitiatedException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.presentation.exceptions import (
    StandardException,
    DomainException,
)


class HealthUseCases:
    def __init__(
        self,
        repository: IHealthRepository,
    ) -> None:
        self.repository = repository

    @staticmethod
    async def health() -> Health:
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
                f"Starting get alembic version use case for the admin {health.user.email.__str__()}."
            )

            alembic_version: Health = await self.repository.get_alembic_version(health)
            health.alembic_version = alembic_version.alembic_version

            if not health:
                logger.info(
                    f"Alembic migration version not found in database for admin {health.user.email.__str__()}. Raising exception."
                )
                raise MigrationNotInitiatedException()

            logger.debug(
                f"Get alembic version use case completed successfully for the admin {health.user.email.__str__()}. Alembic version: {health.alembic_version}."
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
