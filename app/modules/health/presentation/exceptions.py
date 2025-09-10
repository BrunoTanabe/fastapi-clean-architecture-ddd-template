from http import HTTPStatus
from typing import Union, List

from app.core.exceptions import StandardException


# GENERIC EXCEPTIONS
class HealthException(StandardException):
    def __init__(
        self,
        message: str = "Internal processing error",
        errors: Union[
            str, List[str]
        ] = "An unexpected error occurred while processing the request at the health check.",
    ) -> None:
        error_list = [errors] if isinstance(errors, str) else errors

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": error_list},
        )


class HealthUseCasesException(StandardException):
    def __init__(
        self,
        message: str = "Use case processing error",
        errors: Union[
            str, List[str]
        ] = "An error occurred while processing the use case in the health check module.",
    ) -> None:
        error_list = [errors] if isinstance(errors, str) else errors

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": error_list},
        )


# SPECIFIC EXCEPTIONS
class RedirectException(StandardException):
    def __init__(
        self,
        message: str = "Redirection error",
        errors: Union[
            str, List[str]
        ] = "An error occurred while redirecting to the documentation page.",
    ) -> None:
        error_list = [errors] if isinstance(errors, str) else errors

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": error_list},
        )
