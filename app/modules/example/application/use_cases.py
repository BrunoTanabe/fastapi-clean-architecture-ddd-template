from loguru import logger

from app.modules.example.domain.entities import Example
from app.modules.example.presentation.exceptions import (
    ExampleException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.presentation.exceptions import (
    StandardException,
    DomainException,
)


class ExampleUseCases:
    @staticmethod
    async def hello(example: Example) -> Example:
        try:
            logger.debug("Starting hello use case.")

            logger.debug("Hello use case completed successfully.")
            return example
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("An error occurred in the hello use case.")
            raise ExampleException()
