from datetime import datetime, timedelta

from loguru import logger

from app.core.security import (
    verify_password,
    generate_tokens,
    hash_tokens,
)
from app.core.settings import settings
from app.modules.authentication.application.interfaces import (
    IAuthenticationRepository,
)
from app.modules.authentication.domain.entities import (
    Session,
    RefreshToken,
    AccessToken,
)
from app.modules.authentication.presentation.exceptions import (
    AuthenticationException,
    SessionInvalidCredentialsException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.application.utils import BRASILIA_TZ
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.presentation.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.user.domain.entities import User


class AuthenticationUseCases:
    def __init__(
        self,
        repository: IAuthenticationRepository,
        shared_service: SharedUseCases,
    ) -> None:
        self.repository = repository
        self.shared_service = shared_service

    # CREATE
    async def login(self, session: Session) -> Session:
        try:
            logger.debug(
                f"Initializing user login use case for user: {session.user.email} in device: {session.device}."
            )

            db_user: User = await self.shared_service.get_user_by_email(session.user)

            if not await verify_password(
                session.user.password, db_user.hashed_password
            ):
                logger.info("User password does not match, raising exception.")
                raise SessionInvalidCredentialsException()

            session.user = db_user
            session_from_db: Session = (
                await self.repository.get_by_user_id_agent_and_device(session)
            )

            refresh_expires_at = datetime.now(BRASILIA_TZ) + timedelta(
                days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
            )
            access_expires_at = datetime.now(BRASILIA_TZ) + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

            if session_from_db:
                logger.debug(
                    f"Existing session found for user: {session.user.email} in device: {session.device} with agent: {session.user_agent}. Updating session."
                )

                session_from_db.update_last_updated_at()

                session_from_db.refresh_token.expires_at = refresh_expires_at
                session_from_db.refresh_token.generate_updated_at()
                session_from_db.refresh_token.update_previous_hashed_jti()
                session_from_db.refresh_token.activate()

                session_from_db.refresh_token.access_token.expires_at = (
                    access_expires_at
                )
                session_from_db.refresh_token.access_token.generate_created_at()
                session_from_db.refresh_token.access_token.update_previous_hashed_jti()
                session_from_db.refresh_token.access_token.activate()

                session: Session = await generate_tokens(session_from_db)
                session: Session = await hash_tokens(session)
                session.refresh_token.access_token.permission = session.user.role

                await self.repository.update(session)
            else:
                logger.debug(
                    f"No existing session found for user: {session.user.email} in device: {session.device} with agent: {session.user_agent}. Creating new session."
                )

                session.refresh_token = RefreshToken(
                    expires_at=refresh_expires_at,
                    access_token=AccessToken(expires_at=access_expires_at),
                )

                session.refresh_token.generate_created_at()
                session.refresh_token.generate_updated_at()
                session.refresh_token.access_token.generate_created_at()

                session: Session = await generate_tokens(session)
                session: Session = await hash_tokens(session)
                session.refresh_token.access_token.permission = session.user.role

                await self.repository.create(session)

            logger.debug(f"User {session.user.email} logged in successfully.")
            return session
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
    async def refresh(self, session: Session) -> Session:
        try:
            logger.debug(
                f"Initializing user refresh tokens use case for user: {session.user.email} in device: {session.device}."
            )

            session.refresh_token.generate_updated_at()
            session.refresh_token.update_previous_hashed_jti()

            session.refresh_token.access_token.expires_at = datetime.now(
                BRASILIA_TZ
            ) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            session.refresh_token.access_token.generate_created_at()
            session.refresh_token.access_token.update_previous_hashed_jti()

            session: Session = await generate_tokens(session)
            session: Session = await hash_tokens(session)
            session.refresh_token.access_token.permission = session.user.role
            await self.repository.update(session)

            logger.debug(f"User {session.user.email} refreshed tokens successfully.")
            return session
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
    async def logout(self, session: Session) -> Session:
        try:
            logger.debug(
                f"Initializing user logout use case for user: {session.user.email} in device: {session.device}."
            )

            session.refresh_token.generate_updated_at()
            await self.repository.delete(session)

            logger.debug(f"User {session.user.email} refreshed tokens successfully.")
            return session
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the logout use case."
            )
            raise AuthenticationException()
