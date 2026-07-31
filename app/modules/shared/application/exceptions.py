from http import HTTPStatus
from typing import Any

from fastapi import HTTPException

from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.domain.entities import DomainError, DomainErrors


# GENERIC EXCEPTIONS
class StandardException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.data = data or {}
        super().__init__(status_code=status_code, detail=self.message)


class DomainException(StandardException):
    def __init__(self, domain_error: DomainError) -> None:
        errors = (
            domain_error.errors
            if isinstance(domain_error, DomainErrors)
            else [domain_error.message]
        )
        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ResponseMessages.VALIDATION_ERROR.value,
            data={"errors": errors},
        )


class CoreException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=ResponseMessages.INTERNAL_ERROR.value,
            data={
                "errors": ["An unexpected error occurred while processing the request."]
            },
        )


class OriginNotAllowedException(StandardException):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            message=ResponseMessages.AUTHORIZATION_ERROR.value,
            data={"errors": "Connection rejected: origin not allowed."},
        )
