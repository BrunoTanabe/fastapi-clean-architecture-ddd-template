from loguru import logger

from app.modules.key.application.exceptions import (
    KeyException,
    KeyNotFoundException,
    KeyNotModifiedException,
)
from app.modules.key.application.interfaces import (
    IKeyCache,
    IKeyRepository,
    IKeyService,
)
from app.modules.key.domain.entities import Key, KeyList, KeyPagination
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.domain.value_objects import UNSET


class KeyUseCases:
    def __init__(
        self,
        cache: IKeyCache,
        repository: IKeyRepository,
        service: IKeyService,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.service = service

    # CREATE
    async def create(self, key: Key) -> Key:
        try:
            logger.debug(
                f"Initializing create key use case for key '{key.name}'. Requested by user {key.created_by.id}."
            )

            key = await self.service.generate(key)
            plain_key = key.plain_key

            key = await self.repository.create(key)
            key.plain_key = plain_key

            logger.debug(
                f"Create key use case completed successfully for key {key.id}."
            )
            return key
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create key use case."
            )
            raise KeyException()

    # READ
    async def get_by_id(self, key: Key) -> Key:
        try:
            logger.debug(
                f"Initializing get key by id use case for key {key.id}. Requested by user {key.created_by.id}."
            )

            existing = await self.repository.get_by_id(key)
            if existing is None:
                logger.info(f"Api key with id '{key.id}' not found. Raising exception.")
                raise KeyNotFoundException(id=str(key.id))

            logger.debug(
                f"Get key by id use case completed successfully for key {key.id}."
            )
            return existing
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get key by id use case."
            )
            raise KeyException()

    async def get_all(self, key: Key, pagination: KeyPagination) -> KeyList:
        try:
            logger.debug(
                f"Initializing get all keys use case. Requested by user {key.created_by.id}."
            )

            key_list = await self.repository.get_all(key, pagination)

            logger.debug(
                f"Get all keys use case completed. Found {len(key_list.items)} of {key_list.total} total."
            )
            return key_list
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get all keys use case."
            )
            raise KeyException()

    # UPDATE
    async def update(self, key: Key) -> Key:
        try:
            logger.debug(
                f"Initializing update key use case for key {key.id}. Requested by user {key.updated_by.id}."
            )

            existing = await self.repository.get_by_id(key)
            if existing is None:
                logger.info(f"Api key with id '{key.id}' not found. Raising exception.")
                raise KeyNotFoundException(id=str(key.id))

            merged = Key(
                id=key.id,
                name=key.name if key.name is not UNSET else existing.name,
                description=(
                    key.description
                    if key.description is not UNSET
                    else existing.description
                ),
                updated_by=key.updated_by,
                created_by=existing.created_by,
            )

            if (
                merged.name == existing.name
                and merged.description == existing.description
            ):
                logger.info(
                    f"No changes detected for api key '{key.id}'. Raising not modified exception."
                )
                raise KeyNotModifiedException(id=str(key.id))

            updated = await self.repository.update(merged)

            await self.cache.delete(existing)

            logger.debug(
                f"Api key '{updated.id}' updated successfully by user {key.updated_by.id}."
            )
            return updated
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the update key use case."
            )
            raise KeyException()

    async def rotate(self, key: Key) -> Key:
        try:
            logger.debug(
                f"Initializing rotate key use case for key {key.id}. Requested by user {key.updated_by.id}."
            )

            existing = await self.repository.get_by_id(key)
            if existing is None:
                logger.info(f"Api key with id '{key.id}' not found. Raising exception.")
                raise KeyNotFoundException(id=str(key.id))

            # The cache is addressed by hashed_key, and generate() overwrites that
            # field in place. Invalidating first is therefore the only ordering that
            # can still reach the outgoing entry -- afterwards the old key would be
            # unaddressable and the revoked secret would keep authenticating from
            # cache until its ttl expired.
            await self.cache.delete(existing)

            rotated = await self.service.generate(existing)
            plain_key = rotated.plain_key
            rotated.updated_by = key.updated_by

            rotated = await self.repository.rotate(rotated)
            rotated.plain_key = plain_key

            logger.debug(
                f"Api key '{rotated.id}' rotated successfully by user {key.updated_by.id}."
            )
            return rotated
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the rotate key use case."
            )
            raise KeyException()

    # DELETE
    async def delete(self, key: Key) -> Key:
        try:
            logger.debug(
                f"Initializing delete key use case for key {key.id}. Requested by user {key.updated_by.id}."
            )

            existing = await self.repository.get_by_id(key)
            if existing is None:
                logger.info(f"Api key with id '{key.id}' not found. Raising exception.")
                raise KeyNotFoundException(id=str(key.id))

            existing.deactivate(key.updated_by)
            deleted = await self.repository.update(existing)

            await self.cache.delete(deleted)

            logger.debug(
                f"Api key '{deleted.id}' deactivated successfully by user {key.updated_by.id}."
            )
            return deleted
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the delete key use case."
            )
            raise KeyException()
