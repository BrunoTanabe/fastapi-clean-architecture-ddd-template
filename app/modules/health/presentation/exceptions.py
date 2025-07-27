from http import HTTPStatus
from typing import Union, List

from app.core.exceptions import StandardException


class HealthCheckStandardException(StandardException):
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
