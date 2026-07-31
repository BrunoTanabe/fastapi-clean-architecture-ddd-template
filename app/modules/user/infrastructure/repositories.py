from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.shared.application.exceptions import StandardException
from app.modules.user.application.exceptions import UserException
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
)
from app.modules.user.domain.entities import User
from app.modules.user.infrastructure.models import UserModel


class PostgresUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, user: User) -> User:
        try:
            logger.info(f"Creating user {user.email!s} in database.")

            db_user: UserModel = entity_model_mapper(user)

            self.session.add(db_user)
            await self.session.flush()

            logger.info(
                f"User {user.email!s} with id {db_user.id} created successfully."
            )
            return model_entity_mapper(db_user)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create user repository."
            )
            raise UserException()

    # READ
    async def exists_by_email(self, user: User) -> bool:
        try:
            logger.info(f"Checking if user {user.email!s} exists in database.")

            statement = (
                select(UserModel.id)
                .where(
                    UserModel.email == str(user.email),
                    UserModel.is_active.is_(True),
                )
                .limit(1)
            )

            result = await self.session.scalar(statement)
            exists = result is not None

            logger.info(
                f"Existence check for user {user.email!s} completed. Exists: {exists}."
            )
            return exists
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "Unexpected error during the existence check of a user in the database."
            )
            raise UserException()

    async def get_by_id(self, user: User) -> User | None:
        try:
            logger.info(f"Retrieving user with id {user.id} from database.")

            statement = select(UserModel).where(
                UserModel.id == user.id, UserModel.is_active.is_(True)
            )

            result = await self.session.execute(statement)
            user_model: UserModel | None = result.scalar_one_or_none()

            if user_model is None:
                logger.info(f"User with id {user.id} not found in database.")
                return None

            user: User = model_entity_mapper(user_model)

            logger.info(f"User with id {user.id} retrieved successfully from database.")
            return user
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "Unexpected error during the get user by id repository."
            )
            raise UserException()

    async def get_by_email(self, user: User) -> User | None:
        try:
            logger.info(f"Getting user {user.email!s} from database.")

            statement = select(UserModel).where(
                UserModel.email == str(user.email), UserModel.is_active
            )

            result = await self.session.execute(statement)
            user_model: UserModel | None = result.scalar_one_or_none()

            if user_model is None:
                logger.info(
                    f"User with email {user.email!s} not found in database. Returning None."
                )
                return None

            user: User = model_entity_mapper(user_model)

            logger.info(f"User {user.email} retrieved successfully.")
            return user
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "Unexpected error during the get by email of a user in the database."
            )
            raise UserException()
