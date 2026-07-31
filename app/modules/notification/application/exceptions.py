from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.application.exceptions import StandardException


# GENERIC EXCEPTIONS
class NotificationException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the notification module."
            },
        )


# SPECIFIC EXCEPTIONS
class NotificationNotFoundException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"Notification with id '{id}' not found."},
        )
