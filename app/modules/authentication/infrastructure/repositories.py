from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.domain.entities import (
    Session,
    AccessToken,
    RefreshToken,
)
from app.modules.authentication.domain.mappers import model_entity_mapper
from app.modules.authentication.infrastructure.models import (
    SessionModel,
    RefreshTokenModel,
    AccessTokenModel,
)
from app.modules.authentication.presentation.exceptions import AuthenticationException
from app.modules.shared.presentation.exceptions import StandardException


class PostgresSessionRepository(IAuthenticationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, session: Session) -> None:
        try:
            logger.info(
                f"Creating session for user {session.user.email.__str__()} with device {session.device} and user agent {session.user_agent} in database."
            )

            db_session: SessionModel = await model_entity_mapper(session)

            self.session.add(db_session)
            await self.session.flush()

            logger.info(
                f"Session created successfully for user {session.user.email.__str__()} with device {session.device} and user agent {session.user_agent} in database."
            )
            return None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create session repository."
            )
            raise AuthenticationException()

    # READ
    async def get_by_user_id_agent_and_device(
        self, session: Session
    ) -> Optional[Session]:
        try:
            logger.info(
                f"Getting session by user id, agent and device for user {session.user.email} with device {session.device} and user agent {session.user_agent} from database."
            )

            statement = (
                select(SessionModel)
                .options(
                    joinedload(SessionModel.user),
                    joinedload(SessionModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(
                    SessionModel.user_id == session.user.id,
                    SessionModel.user_agent == session.user_agent,
                    SessionModel.device == session.device,
                    SessionModel.blacklisted.is_(False),
                )
            )

            result = await self.session.execute(statement)
            session_model: Optional[SessionModel] = result.scalar_one_or_none()

            if session_model is None:
                logger.info(
                    f"No session found for user {session.user.email} with the given user agent and device."
                )
                return None

            session: Session = await model_entity_mapper(session_model)

            logger.info(
                f"Session retrieved successfully for user {session.user.email} with device {session.device} and user agent {session.user_agent} from database."
            )
            return session
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get session by user agent and device repository."
            )
            raise

    async def get_access_token_by_hashed_jti(
        self, access_token: AccessToken
    ) -> Optional[AccessToken]:
        try:
            logger.info("Getting access token by hashed_jti from database.")

            statement = select(AccessTokenModel).where(
                AccessTokenModel.hashed_jti == access_token.hashed_jti,
                AccessTokenModel.revoked.is_(False),
            )

            result = await self.session.execute(statement)
            access_token_model: Optional[AccessTokenModel] = result.scalar_one_or_none()

            if access_token_model is None:
                logger.info("No session found for the given access token hashed_jti.")
                return None

            access_token: AccessToken = await model_entity_mapper(access_token_model)

            logger.info(
                f"Session retrieved successfully for access token with ID {access_token.id}."
            )
            return access_token
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get access token by hashed_jti repository."
            )
            raise

    async def get_refresh_token_by_hashed_jti(
        self, refresh_token: RefreshToken
    ) -> Optional[RefreshToken]:
        try:
            logger.info("Getting refresh token by hashed_jti from database.")

            statement = (
                select(RefreshTokenModel)
                .options(joinedload(RefreshTokenModel.access_token))
                .where(
                    RefreshTokenModel.hashed_jti == refresh_token.hashed_jti,
                    RefreshTokenModel.revoked.is_(False),
                )
            )

            result = await self.session.execute(statement)
            refresh_token_model: Optional[RefreshTokenModel] = (
                result.scalar_one_or_none()
            )

            if refresh_token_model is None:
                logger.info("No session found for the given access token hashed_jti.")
                return None

            refresh_token: RefreshToken = await model_entity_mapper(refresh_token_model)

            logger.info(
                f"Session retrieved successfully for access token with ID {refresh_token.id}."
            )
            return refresh_token
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get access token by hashed_jti repository."
            )
            raise

    # UPDATE
    async def update(self, session: Session) -> None:
        try:
            logger.info(
                f"Updating session {session.id} for user {session.user.email.__str__()} "
                f"with device {session.device} and user agent {session.user_agent} in database."
            )

            db_session: SessionModel = await model_entity_mapper(session)

            await self.session.merge(db_session)

            await self.session.flush()

            logger.info(
                f"Session {session.id} updated successfully for user {session.user.email.__str__()} "
                f"with device {session.device} and user agent {session.user_agent} in database."
            )
            return None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update session repository."
            )
            raise AuthenticationException()
