from http import HTTPStatus

from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.presentation.exceptions import StandardException


# GENERIC EXCEPTIONS
class ExampleException(StandardException):
    def __init__(self) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An unexpected error occurred while processing the request at the example module."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )
