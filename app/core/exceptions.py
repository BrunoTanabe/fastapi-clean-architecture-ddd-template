from http import HTTPStatus
from typing import Any, Dict, Optional, Union, List

from fastapi import HTTPException

from app.core.enums import ResponseMessages


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


class CoreException(StandardException):
    def __init__(self) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = ["An unexpected error occurred while processing the request."]

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )
