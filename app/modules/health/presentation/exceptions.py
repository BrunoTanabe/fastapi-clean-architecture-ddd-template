from http import HTTPStatus

from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.presentation.exceptions import StandardException


# GENERIC EXCEPTIONS
class HealthException(StandardException):
    def __init__(self) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An unexpected error occurred while processing the request at the health module."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )


# SPECIFIC EXCEPTIONS
class MigrationNotInitiatedException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.RESOURCE_NOT_FOUND.value
        errors = "Alembic migration version not found. It seems that the database migrations have not been initiated."

        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=message,
            data={"errors": errors},
        )
