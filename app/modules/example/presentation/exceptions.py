from http import HTTPStatus
from typing import Union, List

from app.core.exceptions import StandardException


class ExampleException(StandardException):
    def __init__(
        self,
        message: str = "Internal processing error",
        errors: Union[
            str, List[str]
        ] = "An unexpected error occurred while processing the request at the example module.",
    ) -> None:
        error_list = [errors] if isinstance(errors, str) else errors

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": error_list},
        )


class ExampleUseCasesException(StandardException):
    def __init__(
        self,
        message: str = "Use case processing error",
        errors: Union[
            str, List[str]
        ] = "An error occurred while processing the use case in the example module.",
    ) -> None:
        error_list = [errors] if isinstance(errors, str) else errors

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": error_list},
        )


class ExampleNameNotProvidedException(StandardException):
    def __init__(
        self,
        message: str = "Name not provided",
        errors: Union[
            str, List[str]
        ] = "The name field is required and cannot be empty.",
    ) -> None:
        error_list = [errors] if isinstance(errors, str) else errors

        super().__init__(
            status_code=HTTPStatus.BAD_REQUEST,
            message=message,
            data={"errors": error_list},
        )
