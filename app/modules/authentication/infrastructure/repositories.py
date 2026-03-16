from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.domain.entities import (
    Session,
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

    async def get_access_token_by_session(
        self,
        session: Session,
    ) -> Optional[Session]:
        try:
            logger.info(
                "Getting session by access token hashed_jti and device from database."
            )

            conditions = [
                AccessTokenModel.hashed_jti
                == session.refresh_token.access_token.hashed_jti,
                SessionModel.user_agent == session.user_agent,
                SessionModel.user_id == session.user.id,
                AccessTokenModel.revoked.is_(False),
                RefreshTokenModel.revoked.is_(False),
                SessionModel.blacklisted.is_(False),
            ]

            if session.device is not None:
                conditions.append(SessionModel.device == session.device)

            statement = (
                select(SessionModel)
                .join(SessionModel.refresh_token)
                .join(RefreshTokenModel.access_token)
                .options(
                    joinedload(SessionModel.user),
                    joinedload(SessionModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            session_model: Optional[SessionModel] = result.scalar_one_or_none()

            if session_model is None:
                logger.info(
                    "No session found for the given access token hashed_jti and device."
                )
                return None

            session: Session = await model_entity_mapper(session_model)

            logger.info(
                f"Session retrieved successfully for access token with ID {session.refresh_token.access_token.id} and device {session.device}."
            )
            return session
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get access token by hashed_jti repository."
            )
            raise

    async def get_refresh_token_by_session(
        self,
        session: Session,
    ) -> Optional[Session]:
        try:
            logger.info(
                "Getting session by refresh token hashed_jti and device from database."
            )

            conditions = [
                RefreshTokenModel.hashed_jti == session.refresh_token.hashed_jti,
                SessionModel.user_agent == session.user_agent,
                SessionModel.user_id == session.user.id,
                RefreshTokenModel.revoked.is_(False),
                SessionModel.blacklisted.is_(False),
            ]

            if session.device is not None:
                conditions.append(SessionModel.device == session.device)

            statement = (
                select(SessionModel)
                .join(SessionModel.refresh_token)
                .options(
                    joinedload(SessionModel.user),
                    joinedload(SessionModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            session_model: Optional[SessionModel] = result.scalar_one_or_none()

            if session_model is None:
                logger.info(
                    "No session found for the given refresh token hashed_jti and device."
                )
                return None

            session: Session = await model_entity_mapper(session_model)

            logger.info(
                f"Session retrieved successfully for refresh token with ID {session.id} and device {session.device}."
            )
            return session
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

    # DELETE
    async def delete(self, session: Session) -> None:
        try:
            logger.info(
                f"Revoking session {session.id} for user {session.user.email.__str__()} "
                f"with device {session.device} and user agent {session.user_agent} in database."
            )

            session.refresh_token.revoke()
            session.refresh_token.access_token.revoke()

            db_session: SessionModel = await model_entity_mapper(session)

            await self.session.merge(db_session)
            await self.session.flush()

            logger.info(
                f"Session {session.id} revoked successfully for user {session.user.email.__str__()} "
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
