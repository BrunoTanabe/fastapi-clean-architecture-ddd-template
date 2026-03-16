from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestFormStrict
from loguru import logger

from app.core.security import (
    no_authentication,
    authenticate_refresh,
    authenticate_logout,
)
from app.core.settings import settings
from app.modules.authentication.application.use_cases import AuthenticationUseCases
from app.modules.authentication.domain.entities import Session
from app.modules.authentication.domain.mappers import (
    login_entity_mapper,
    refresh_entity_mapper,
    logout_entity_mapper,
)
from app.modules.authentication.presentation.dependencies import (
    get_authentication_use_cases,
)
from app.modules.authentication.presentation.docs import (
    router_docs,
    login_docs,
    refresh_docs,
    logout_docs,
)
from app.modules.authentication.presentation.exceptions import AuthenticationException
from app.modules.authentication.presentation.schemas import (
    LoginResponse,
    RefreshResponse,
    LogoutResponse,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.presentation.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.user.presentation.exceptions import CookieManagementException

router = APIRouter(**router_docs)


async def set_cookies(response: Response, session: Session) -> None:
    try:
        response.set_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            value=session.token_type,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite="lax",
        )

        response.set_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            value=session.refresh_token.access_token.token,
            max_age=settings.COOKIES_ACCESS_TOKEN_MAX_AGE,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite="lax",
        )

        response.set_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            value=session.refresh_token.token,
            max_age=settings.COOKIES_REFRESH_TOKEN_MAX_AGE,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite="strict",
        )
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the set_cookies function.")
        raise CookieManagementException()


async def delete_cookies(response: Response) -> None:
    try:
        response.delete_cookie(
            key=settings.COOKIES_TOKEN_TYPE_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite="lax",
        )

        response.delete_cookie(
            key=settings.COOKIES_ACCESS_TOKEN_KEY,
            path=settings.COOKIES_ACCESS_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite="lax",
        )

        response.delete_cookie(
            key=settings.COOKIES_REFRESH_TOKEN_KEY,
            path=settings.COOKIES_REFRESH_TOKEN_PATH,
            domain=settings.COOKIES_DOMAIN,
            secure=not settings.APPLICATION_ENVIRONMENT_DEBUG,
            httponly=True,
            samesite="lax",
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
    form_data: OAuth2PasswordRequestFormStrict = Depends(),
    use_case: AuthenticationUseCases = Depends(get_authentication_use_cases),
) -> LoginResponse:
    try:
        request_domain = await login_entity_mapper(form_data, request)
        response_domain = await use_case.login(request_domain)
        output = await login_entity_mapper(response_domain)

        await set_cookies(response, response_domain)

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
    session: Session = Depends(authenticate_refresh),
    use_case: AuthenticationUseCases = Depends(get_authentication_use_cases),
) -> RefreshResponse:
    try:
        request_domain = await refresh_entity_mapper(session, False)
        response_domain = await use_case.refresh(request_domain)
        output = await refresh_entity_mapper(response_domain, True)

        await set_cookies(response, response_domain)

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
    session: Session = Depends(authenticate_logout),
    use_case: AuthenticationUseCases = Depends(get_authentication_use_cases),
) -> LogoutResponse:
    try:
        # await delete_cookies(response)

        request_domain = await logout_entity_mapper(session, False)
        response_domain = await use_case.logout(request_domain)
        output = await logout_entity_mapper(response_domain, True)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the refresh endpoint.")
        raise AuthenticationException()
