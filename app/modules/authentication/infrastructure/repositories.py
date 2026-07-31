from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.authentication.application.exceptions import AuthenticationException
from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    sync_entity_from_model,
)
from app.modules.authentication.domain.entities import Authentication
from app.modules.authentication.infrastructure.models import (
    AccessTokenModel,
    AuthenticationModel,
    RefreshTokenModel,
)
from app.modules.shared.application.exceptions import StandardException


class PostgresAuthenticationRepository(IAuthenticationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Creating authentication for user {authentication.user.id} with device {authentication.device} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            self.session.add(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, db_authentication
            )

            logger.info(
                f"Authentication created successfully for user {authentication.user.id} with device {authentication.device} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create authentication repository."
            )
            raise AuthenticationException()

    # READ
    async def get_by_user_id_agent_and_device(
        self, authentication: Authentication
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by user id, agent and device for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} from database."
            )

            statement = (
                select(AuthenticationModel)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(
                    AuthenticationModel.user_id == authentication.user.id,
                    AuthenticationModel.user_agent == authentication.user_agent,
                    AuthenticationModel.device == authentication.device,
                    AuthenticationModel.blacklisted.is_(False),
                )
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent}."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} from database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get authentication by user agent and device repository."
            )
            raise AuthenticationException()

    async def get_access_token_by_authentication(
        self,
        authentication: Authentication,
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by access token hashed_jti {authentication.refresh_token.access_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} from database."
            )

            conditions = [
                AccessTokenModel.hashed_jti
                == authentication.refresh_token.access_token.hashed_jti,
                AuthenticationModel.user_agent == authentication.user_agent,
                AuthenticationModel.user_id == authentication.user.id,
                AccessTokenModel.revoked.is_(False),
                RefreshTokenModel.revoked.is_(False),
                AuthenticationModel.blacklisted.is_(False),
            ]

            if authentication.device is not None:
                conditions.append(AuthenticationModel.device == authentication.device)

            statement = (
                select(AuthenticationModel)
                .join(AuthenticationModel.refresh_token)
                .join(RefreshTokenModel.access_token)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for access token hashed_jti {authentication.refresh_token.access_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for access token with ID {authentication.id} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get access token by hashed_jti repository."
            )
            raise AuthenticationException()

    async def get_refresh_token_by_authentication(
        self,
        authentication: Authentication,
    ) -> Authentication | None:
        try:
            logger.info(
                f"Getting authentication by refresh token hashed_jti {authentication.refresh_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} from database."
            )

            conditions = [
                RefreshTokenModel.hashed_jti == authentication.refresh_token.hashed_jti,
                AuthenticationModel.user_agent == authentication.user_agent,
                AuthenticationModel.user_id == authentication.user.id,
                RefreshTokenModel.revoked.is_(False),
                AuthenticationModel.blacklisted.is_(False),
            ]

            if authentication.device is not None:
                conditions.append(AuthenticationModel.device == authentication.device)

            statement = (
                select(AuthenticationModel)
                .join(AuthenticationModel.refresh_token)
                .options(
                    joinedload(AuthenticationModel.user),
                    joinedload(AuthenticationModel.refresh_token).joinedload(
                        RefreshTokenModel.access_token
                    ),
                )
                .where(*conditions)
            )

            result = await self.session.execute(statement)
            authentication_model: AuthenticationModel | None = (
                result.scalar_one_or_none()
            )

            if authentication_model is None:
                logger.info(
                    f"No authentication found for refresh token hashed_jti {authentication.refresh_token.hashed_jti} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database."
                )
                return None

            authentication: Authentication = model_entity_mapper(authentication_model)

            logger.info(
                f"Authentication retrieved successfully for refresh token with ID {authentication.id} and user identifier {authentication.user.id} and user agent {authentication.user_agent} in database. Authentication identifier: {authentication.id}."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get refresh token by hashed_jti repository."
            )
            raise AuthenticationException()

    # UPDATE
    async def update(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Updating authentication {authentication.id} for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            merged: AuthenticationModel = await self.session.merge(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, merged
            )

            logger.info(
                f"Authentication {authentication.id} updated successfully for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update authentication repository."
            )
            raise AuthenticationException()

    # DELETE
    async def delete(self, authentication: Authentication) -> Authentication:
        try:
            logger.info(
                f"Persisting revoked authentication {authentication.id} for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )

            db_authentication: AuthenticationModel = entity_model_mapper(authentication)

            merged: AuthenticationModel = await self.session.merge(db_authentication)
            await self.session.flush()

            authentication: Authentication = sync_entity_from_model(
                authentication, merged
            )

            logger.info(
                f"Authentication {authentication.id} revoked successfully for user {authentication.user.id} with device {authentication.device} and user agent {authentication.user_agent} in database."
            )
            return authentication
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the delete authentication repository."
            )
            raise AuthenticationException()
