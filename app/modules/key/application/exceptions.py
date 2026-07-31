from http import HTTPStatus

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import ResponseMessages


# GENERIC EXCEPTIONS
class KeyException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the key module."
            },
        )


# SPECIFIC EXCEPTIONS
class KeyNotFoundException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"API key with id '{id}' not found."},
        )


class KeyNotModifiedException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.BAD_REQUEST.value,
            data={
                "errors": f"No changes were provided; the API key with id '{id}' already has the submitted values."
            },
        )


class ApiKeyNotProvidedException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "API key was not provided. Please provide a valid API key in the request header."
            },
        )


class ApiKeyInvalidException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "Invalid API key. The provided key is not valid or does not exist."
            },
        )


class ApiKeyRevokedException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "The provided API key has been revoked and can no longer be used."
            },
        )


class ApiKeyExpiredException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ResponseMessages.UNAUTHORIZED_ERROR.value,
            data={
                "errors": "The provided API key has expired. Please generate a new API key."
            },
        )
