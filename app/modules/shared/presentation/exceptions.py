from http import HTTPStatus
from typing import Any, Dict, Optional

from fastapi import HTTPException

from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.domain.entities import DomainError


# GENERIC EXCEPTIONS
class StandardException(HTTPException):
    def __init__(
        self,
        status_code: int,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.data = data or {}
        super().__init__(status_code=status_code, detail=self.message)


class DomainException(StandardException):
    def __init__(self, domain_error: DomainError) -> None:
        message = ResponseMessages.VALIDATION_ERROR
        errors = [domain_error.message]

        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=message.value,
            data={"errors": errors},
        )


class CoreException(StandardException):
    def __init__(self) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = ["An unexpected error occurred while processing the request."]

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )
