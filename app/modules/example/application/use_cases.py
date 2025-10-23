from loguru import logger

from app.core.exceptions import StandardException

from app.modules.example.domain.entities import Example
from app.modules.example.presentation.exceptions import (
    ExampleNameNotProvidedException,
    ExampleUseCasesException,
)


class ExampleUseCases:
    async def hello(self, example: Example) -> Example:
        try:
            logger.info("Starting hello use case.")

            if not example.name:
                logger.warning("Example name not provided, raising exception.")

                raise ExampleNameNotProvidedException(
                    message="Example name must be provided.",
                    errors="The 'name' field is required for processing the example.",
                )

            example.message = f"Hello {example.name}!"

            logger.info("Hello use case completed successfully.")
            return example
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(f"An error occurred in the hello use case.")
            raise ExampleUseCasesException()
