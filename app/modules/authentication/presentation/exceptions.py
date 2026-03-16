from http import HTTPStatus

from app.modules.shared.application.enums import ResponseMessages
from app.modules.shared.presentation.exceptions import StandardException


# GENERIC EXCEPTIONS
class AuthenticationException(StandardException):
    def __init__(self) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An unexpected error occurred while processing the request at the authentication module."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )


class AuthenticationTokenException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An error occurred while processing the authentication token. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )


class HashingException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An error occurred while hashing the password. Please try again."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.INTERNAL_ERROR.value
        errors = "An error occurred while processing the refresh token. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            message=message,
            data={"errors": errors},
        )


# SPECIFIC EXCEPTIONS
class SessionInvalidCredentialsException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Invalid credentials for login."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class AuthenticationTokenExpiredException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Token has expired. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class AuthenticationTokenNotYetValidException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Token is not yet valid. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class AuthenticationTokenMalformedError(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = (
            "Malformed authentication token. Please login again or contact support."
        )

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class AuthenticationCookiesNotProvidedException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Authentication cookies doest not exist. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class UserHasNotPermissionException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "User does not have permission to perform this action."

        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            message=message,
            data={"errors": errors},
        )


class AuthenticationTokenInvalidException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Invalid authentication token. the provided token is not valid or has been revoked. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class ModifiedTokenException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "The authentication token has been modified. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenNotProvidedException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Refresh token not provided. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenExpiredException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Refresh token has expired. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenNotYetValidException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = (
            "Refresh token is not yet valid. Please login again or contact support."
        )

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenMalformedError(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Malformed refresh token. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenInvalidEndpoint(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = (
            "Invalid endpoint for refresh token. Please login again or contact support."
        )

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenInvalidException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Invalid refresh token. the provided token is not valid or has been revoked. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class RefreshTokenInvalidDeviceException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Invalid refresh token data. the provided token is not valid or has been revoked. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class AuthenticationInvalidDeviceException(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Invalid authentication data. the provided token is not valid or has been revoked. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )


class LogoutInvalidEndpoint(StandardException):
    def __init__(
        self,
    ) -> None:
        message = ResponseMessages.UNAUTHORIZED_ERROR.value
        errors = "Invalid endpoint for logout. Please login again or contact support."

        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=message,
            data={"errors": errors},
        )
