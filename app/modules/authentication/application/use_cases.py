from datetime import datetime, timedelta

from loguru import logger

from app.core.settings import settings
from app.modules.authentication.application.exceptions import (
    AuthenticationException,
    InvalidCredentialsException,
)
from app.modules.authentication.application.interfaces import (
    IAuthenticationCache,
    IAuthenticationRepository,
    ITokenService,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import DomainError
from app.modules.user.domain.entities import User


class AuthenticationUseCases:
    def __init__(
        self,
        cache: IAuthenticationCache,
        repository: IAuthenticationRepository,
        shared_service: SharedUseCases,
        token_service: ITokenService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.shared_service = shared_service
        self.token_service = token_service
        self.shared_service.disable_exceptions()

    # CREATE
    async def login(self, authentication: Authentication) -> Authentication:
        try:
            logger.debug(
                f"Initializing user login use case for user: {authentication.user.censored_email} in device: {authentication.device}. The user/authentication identifier has not yet been retrieved."
            )

            db_user: User | None = await self.shared_service.get_user_by_email(
                authentication.user
            )

            if not db_user:
                logger.info(
                    f"User with email {authentication.user.censored_email} not found, raising exception. The user identifier not found."
                )
                raise InvalidCredentialsException()

            if not await self.token_service.verify_password(
                authentication.user.password, db_user.hashed_password
            ):
                logger.info(
                    f"Invalid password for user {authentication.user.id}, raising exception."
                )
                raise InvalidCredentialsException()

            authentication.user = db_user
            authentication_from_db = (
                await self.repository.get_by_user_id_agent_and_device(authentication)
            )

            now = datetime.now(BRASILIA_TZ)
            refresh_expires_at = now + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            if authentication_from_db:
                logger.debug(
                    f"Existing authentication found for user: {authentication.user.id} in device: {authentication.device}. Renewing tokens. Authentication identifier: {authentication_from_db.id}."
                )

                await self.cache.delete_by_access_token(authentication_from_db)
                await self.cache.delete_by_refresh_token(authentication_from_db)

                authentication = authentication_from_db.renew_tokens(
                    now, refresh_expires_at, access_expires_at
                )
            else:
                logger.debug(
                    f"No existing authentication found for user: {authentication.user.id} in device: {authentication.device}. Creating new authentication."
                )
                authentication = authentication.create_tokens(
                    now, refresh_expires_at, access_expires_at
                )

            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            if authentication_from_db:
                await self.repository.update(authentication)
            else:
                await self.repository.create(authentication)

            logger.debug(
                f"User {authentication.user.id} logged in successfully in device: {authentication.device}. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the login use case."
            )
            raise AuthenticationException()

    # UPDATE
    async def refresh(self, authentication: Authentication) -> Authentication:
        try:
            logger.debug(
                f"Initializing user refresh tokens use case for user: {authentication.user.id} in device: {authentication.device}."
            )

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            now = datetime.now(BRASILIA_TZ)
            access_expires_at = now + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            authentication = authentication.refresh_access_token(now, access_expires_at)
            authentication = await self.token_service.generate(authentication)
            authentication = await self.token_service.hash_tokens(authentication)
            authentication.refresh_token.access_token.permission = (
                authentication.user.role
            )

            await self.repository.update(authentication)

            logger.debug(
                f"User {authentication.user.id} refreshed tokens successfully."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the refresh tokens use case."
            )
            raise AuthenticationException()

    # DELETE
    async def logout(self, authentication: Authentication) -> Authentication:
        try:
            logger.debug(
                f"Initializing user logout use case for user: {authentication.user.id} in device: {authentication.device}."
            )

            authentication.revoke(datetime.now(BRASILIA_TZ))
            await self.repository.delete(authentication)

            await self.cache.delete_by_access_token(authentication)
            await self.cache.delete_by_refresh_token(authentication)

            logger.debug(
                f"User {authentication.user.id} logged out successfully from device: {authentication.device}."
            )
            return authentication
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the logout use case."
            )
            raise AuthenticationException()
