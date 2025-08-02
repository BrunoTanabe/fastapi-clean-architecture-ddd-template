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
            if not example.name:
                logger.info("Example name not provided, raising exception.")

                raise ExampleNameNotProvidedException(
                    message="Example name must be provided.",
                    errors="The 'name' field is required for processing the example.",
                )

            example.message = f"Hello {example.name}!"
            return example

        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error("fAn error occurred in the hello use case.")
            raise ExampleUseCasesException()
