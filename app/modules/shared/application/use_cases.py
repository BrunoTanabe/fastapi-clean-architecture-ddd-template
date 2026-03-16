from typing import Optional

from loguru import logger

from app.modules.shared.domain.entities import DomainError
from app.modules.shared.presentation.exceptions import (
    StandardException,
    DomainException,
)
from app.modules.user.application.interfaces import IUserRepository
from app.modules.user.domain.entities import User
from app.modules.user.presentation.exceptions import (
    UserException,
    UserEmailNotFoundException,
)


class SharedUseCases:
    def __init__(
        self,
        user_repository: IUserRepository,
    ) -> None:
        self.user_repository = user_repository
        self._raise_exceptions = True

    @property
    def raise_exceptions(self) -> bool:
        return self._raise_exceptions

    def enable_exceptions(self) -> None:
        self._raise_exceptions = True

    def disable_exceptions(self) -> None:
        self._raise_exceptions = False

    async def get_user_by_id(self, user: User) -> Optional[User]:
        try:
            logger.debug(
                f"Initializing get user by email use case for user: {user.email}."
            )

            db_user = await self.user_repository.get_by_id(user)

            if db_user is None and self._raise_exceptions:
                logger.info(
                    f"User with email {user.email} not found. Raising exception."
                )
                raise UserEmailNotFoundException(email=user.email.__str__())

            logger.debug(f"User {user.email} retrieved from database successfully.")
            return db_user
        except StandardException:
            if self._raise_exceptions:
                raise
            return None
        except DomainError as e:
            if self._raise_exceptions:
                raise DomainException(e)
            return None
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get user by email use case."
            )
            if self._raise_exceptions:
                raise UserException()
            return None

    async def get_user_by_email(self, user: User) -> Optional[User]:
        try:
            logger.debug(
                f"Initializing get user by email use case for user: {user.email}."
            )

            db_user = await self.user_repository.get_by_email(user)

            if db_user is None and self._raise_exceptions:
                logger.info(
                    f"User with email {user.email} not found. Raising exception."
                )
                raise UserEmailNotFoundException(email=user.email.__str__())

            logger.debug(f"User {user.email} retrieved from database successfully.")
            return db_user
        except StandardException:
            if self._raise_exceptions:
                raise
            return None
        except DomainError as e:
            if self._raise_exceptions:
                raise DomainException(e)
            return None
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get user by email use case."
            )
            if self._raise_exceptions:
                raise UserException()
            return None
