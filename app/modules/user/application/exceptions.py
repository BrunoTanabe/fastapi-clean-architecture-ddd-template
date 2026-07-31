from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.application.exceptions import StandardException


# GENERIC EXCEPTIONS
class UserException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the user module."
            },
        )


# SPECIFIC EXCEPTIONS
class UserEmailAlreadyExistsException(StandardException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={"errors": f"User email '{email}' already exists."},
        )


class UserEmailNotFoundException(StandardException):
    def __init__(self, email: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"User email '{email}' not found."},
        )


class UserIdNotFoundException(StandardException):
    def __init__(self, user_id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"User with identifier '{user_id}' not found."},
        )


class CookieManagementException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while managing the user cookie."
            },
        )
