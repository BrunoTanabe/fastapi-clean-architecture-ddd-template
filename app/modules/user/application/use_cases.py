from loguru import logger

from app.core.security import hash_password
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.application.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.domain.entities import User
from app.modules.user.application.exceptions import (
    UserEmailAlreadyExistsException,
    UserException,
)


class UserUseCases:
    def __init__(
        self,
        repository: IUserRepository,
    ) -> None:
        self.repository = repository

    # CREATE
    async def create(self, user: User) -> User:
        try:
            logger.debug(
                f"Initializing create user use case with user: {user.censored_email}."
            )

            if await self.repository.exists_by_email(user):
                logger.info(
                    f"User with email {user.censored_email} already exists. Raising exception."
                )
                raise UserEmailAlreadyExistsException(email=str(user.email))

            user.hashed_password = hash_password(user.password)
            user = await self.repository.create(user)

            logger.debug(
                f"User {user.censored_email} with id {user.id} created successfully."
            )
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create user use case."
            )
            raise UserException()

    # READ
    async def me(self, user: User) -> User:
        try:
            logger.debug(f"Initializing /me user use case for user {user.id}.")

            logger.debug(f"User {user.id} retrieved successfully in /me use case.")
            return user
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error("An error occurred in the me use case.")
            raise UserException()
