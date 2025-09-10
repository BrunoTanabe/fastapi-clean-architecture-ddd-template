from loguru import logger

from app.core.exceptions import StandardException
from app.modules.health.application.enums import HealthType
from app.modules.health.presentation.exceptions import HealthUseCasesException


class HealthUseCases:
    async def check(self) -> HealthType:
        try:
            return HealthType.OK
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("An error occurred in the hello use case.")
            raise HealthUseCasesException()
