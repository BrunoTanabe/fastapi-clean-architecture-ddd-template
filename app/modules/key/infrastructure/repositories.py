from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import SortOrder
from app.modules.key.application.exceptions import KeyException
from app.modules.key.application.interfaces import IKeyRepository
from app.modules.key.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    model_entity_with_actors_mapper,
    models_key_list_mapper,
)
from app.modules.key.domain.entities import Key, KeyList, KeyPagination
from app.modules.key.infrastructure.models import KeyModel


class PostgresKeyRepository(IKeyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, key: Key) -> Key:
        try:
            logger.info(
                f"Creating api key '{key.name}' in database. Requested by user {key.created_by.id}."
            )

            db_key: KeyModel = entity_model_mapper(key)

            self.session.add(db_key)
            await self.session.flush()

            logger.info(
                f"Api key '{key.name}' created successfully in database by user {key.created_by.id}."
            )
            return model_entity_mapper(db_key)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create key repository."
            )
            raise KeyException()

    # READ
    async def get_by_id(self, key: Key) -> Key | None:
        try:
            logger.info(f"Getting api key '{key.id}' from database.")

            model = await self.session.scalar(
                select(KeyModel)
                .options(
                    joinedload(KeyModel.creator),
                    joinedload(KeyModel.updater),
                )
                .where(
                    KeyModel.id == key.id,
                    KeyModel.is_active.is_(True),
                )
            )

            logger.info(
                f"Api key '{key.id}' {'found' if model else 'not found'} in database."
            )
            return model_entity_with_actors_mapper(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get key by id repository."
            )
            raise KeyException()

    async def get_all(self, key: Key, pagination: KeyPagination) -> KeyList:
        try:
            logger.info(
                f"Getting all active api keys from database. Requested by user {key.created_by.id}."
            )

            col = getattr(KeyModel, pagination.sort_by.value)
            ordering = (
                col.asc() if pagination.sort_order == SortOrder.ASC else col.desc()
            )

            statement = (
                select(
                    KeyModel,
                    func.count(KeyModel.id).over().label("total"),
                )
                .where(KeyModel.is_active.is_(True))
                .order_by(ordering)
                .offset(pagination.offset)
                .limit(pagination.per_page)
            )

            result = await self.session.execute(statement)
            rows = result.all()

            key_list = models_key_list_mapper(rows)

            logger.info(
                f"Retrieved {len(key_list.items)} of {key_list.total} active api key(s) from database."
            )
            return key_list
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get all keys repository."
            )
            raise KeyException()

    async def get_key_by_hashed_key(self, hashed_key: str) -> Key | None:
        try:
            logger.info("Getting api key by hashed key from database.")

            # No is_active filter here (unlike the other reads): the API-key auth
            # path must distinguish a revoked key (found but inactive) from an
            # invalid one (not found), so revoked keys must still be returned.
            model = await self.session.scalar(
                select(KeyModel).where(KeyModel.hashed_key == hashed_key)
            )

            logger.info(
                f"Api key {'found' if model else 'not found'} by hashed key in database."
            )
            return model_entity_mapper(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get key by hashed key repository."
            )
            raise KeyException()

    # UPDATE
    async def update(self, key: Key) -> Key:
        try:
            logger.info(
                f"Updating api key '{key.id}' in database. Requested by user {key.updated_by.id}."
            )

            model = await self.session.get(KeyModel, key.id)

            model.name = key.name
            model.description = key.description
            model.updated_by = key.updated_by.id
            model.is_active = key.is_active

            await self.session.flush()

            logger.info(f"Api key '{key.id}' updated successfully in database.")
            return model_entity_mapper(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update key repository."
            )
            raise KeyException()

    async def rotate(self, key: Key) -> Key:
        try:
            logger.info(
                f"Rotating api key '{key.id}' in database. Requested by user {key.updated_by.id}."
            )

            model = await self.session.get(KeyModel, key.id)

            model.prefix = key.prefix
            model.last_four = key.last_four
            model.hashed_key = key.hashed_key
            model.updated_by = key.updated_by.id

            await self.session.flush()

            logger.info(f"Api key '{key.id}' rotated successfully in database.")
            return model_entity_mapper(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the rotate key repository."
            )
            raise KeyException()
