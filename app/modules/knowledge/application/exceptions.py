from http import HTTPStatus

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.application.exceptions import StandardException


# GENERIC EXCEPTIONS
class KnowledgeException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": "An unexpected error occurred while processing the request at the knowledge module."
            },
        )


# SPECIFIC EXCEPTIONS
class KnowledgeNotFoundException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            message=ResponseMessages.RESOURCE_NOT_FOUND.value,
            data={"errors": f"Knowledge with id '{id}' not found."},
        )


class KnowledgeNameAlreadyExistsException(StandardException):
    def __init__(self, name: str) -> None:
        super().__init__(
            status_code=HTTPStatus.CONFLICT,
            message=ResponseMessages.CONFLICT.value,
            data={"errors": f"Knowledge with name '{name}' already exists."},
        )


class KnowledgeNotModifiedException(StandardException):
    def __init__(self, id: str) -> None:
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.BAD_REQUEST.value,
            data={
                "errors": f"No changes were provided; the knowledge base with id '{id}' already has the submitted values."
            },
        )
