from http import HTTPStatus

from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.presentation.exceptions import StandardException


# GENERIC EXCEPTIONS
class UserException(StandardException):
    def __init__(self) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An unexpected error occurred while processing the request at the user module."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )


# SPECIFIC EXCEPTIONS
class UserEmailAlreadyExistsException(StandardException):
    def __init__(
        self,
        email: str,
    ) -> None:
        message = ResponseMessages.CONFLICT.value
        errors = f"User email '{email}' already exists."

        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=message,
            data={"errors": errors},
        )


class UserEmailNotFoundException(StandardException):
    def __init__(
        self,
        email: str,
    ) -> None:
        message = ResponseMessages.RESOURCE_NOT_FOUND.value
        errors = f"User email '{email}' not found."

        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=message,
            data={"errors": errors},
        )


class CookieManagementException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An unexpected error occurred while managing the user cookie."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )
