from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestFormStrict
from loguru import logger

from app.core.security import (
    authenticate_logout,
    authenticate_refresh,
    no_authentication,
)
from app.core.settings import settings
from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.mappers import (
    entity_login_mapper,
    entity_logout_mapper,
    entity_refresh_mapper,
    login_entity_mapper,
    logout_entity_mapper,
    refresh_entity_mapper,
)
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.domain.enums import TokenType
from app.modules.authentication.presentation.dependencies import (
    get_authentication_use_cases,
)
from app.modules.authentication.presentation.docs import (
    login_docs,
    logout_docs,
    refresh_docs,
    router_docs,
)
from app.modules.authentication.presentation.schemas import (
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
)
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.user.application.exceptions import CookieManagementException

router = APIRouter(**router_docs)


def set_cookies(response: Response, authentication: Authentication) -> None:
    try:
        response.set_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            value=TokenType.BEARER.value,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            value=authentication.refresh_token.access_token.token
            if authentication.refresh_token.access_token.token
            else "",
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.set_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            value=authentication.refresh_token.token
            if authentication.refresh_token.token
            else "",
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the set_cookies function.")
        raise CookieManagementException()


def delete_cookies(response: Response) -> None:
    try:
        response.delete_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )

        response.delete_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite=settings.COOKIES_SAME_SITE,
        )
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the delete_cookies function."
        )
        raise CookieManagementException()


# CREATE
@router.post("/login/", **login_docs)
@router.post("/login", include_in_schema=False)
async def login(
    request: Request,
    response: Response,
    _: Annotated[None, Depends(no_authentication)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LoginResponse:
    try:
        request_domain = login_entity_mapper(form_data, request)
        response_domain = await use_case.login(request_domain)
        output = entity_login_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the login endpoint.")
        raise AuthenticationException()


# UPDATE
@router.patch("/refresh/", **refresh_docs)
@router.patch("/refresh", include_in_schema=False)
async def refresh(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_refresh)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> RefreshResponse:
    try:
        request_domain = refresh_entity_mapper(authentication)
        response_domain = await use_case.refresh(request_domain)
        output = entity_refresh_mapper(response_domain)

        set_cookies(response, response_domain)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the refresh endpoint.")
        raise AuthenticationException()


# DELETE
@router.delete("/logout/", **logout_docs)
@router.delete("/logout", include_in_schema=False)
async def logout(
    response: Response,
    authentication: Annotated[Authentication, Depends(authenticate_logout)],
    use_case: Annotated[AuthenticationUseCases, Depends(get_authentication_use_cases)],
) -> LogoutResponse:
    try:
        request_domain = logout_entity_mapper(authentication)
        response_domain = await use_case.logout(request_domain)
        output = entity_logout_mapper(response_domain)

        delete_cookies(response)
        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the logout endpoint.")
        raise AuthenticationException()
