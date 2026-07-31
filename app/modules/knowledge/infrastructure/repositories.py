from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.knowledge.application.exceptions import KnowledgeException
from app.modules.knowledge.application.interfaces import IKnowledgeRepository
from app.modules.knowledge.application.mappers import (
    entity_model_mapper,
    model_entity_mapper,
    models_knowledge_list_mapper,
)
from app.modules.knowledge.domain.entities import (
    Knowledge,
    KnowledgeList,
    KnowledgePagination,
)
from app.modules.knowledge.infrastructure.models import KnowledgeModel
from app.modules.shared.application.exceptions import StandardException
from app.modules.shared.domain.enums import SortOrder


class PostgresKnowledgeRepository(IKnowledgeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # CREATE
    async def create(self, knowledge: Knowledge) -> Knowledge:
        try:
            logger.info(
                f"Creating knowledge '{knowledge.name}' in database. Requested by user {knowledge.created_by.id}."
            )

            db_knowledge: KnowledgeModel = entity_model_mapper(knowledge)

            self.session.add(db_knowledge)
            await self.session.flush()

            logger.info(
                f"Knowledge '{knowledge.name}' created successfully in database by user {knowledge.created_by.id}."
            )
            return model_entity_mapper(db_knowledge)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the create knowledge repository."
            )
            raise KnowledgeException()

    # READ
    async def get_by_id(self, knowledge: Knowledge) -> Knowledge | None:
        try:
            logger.info(f"Getting knowledge '{knowledge.id}' from database.")

            model = await self.session.scalar(
                select(KnowledgeModel).where(
                    KnowledgeModel.id == knowledge.id,
                    KnowledgeModel.is_active.is_(True),
                )
            )

            logger.info(
                f"Knowledge '{knowledge.id}' {'found' if model else 'not found'} in database."
            )
            return model_entity_mapper(model) if model else None
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get knowledge by id repository."
            )
            raise KnowledgeException()

    async def exists_by_name(self, knowledge: Knowledge) -> bool:
        try:
            logger.info(
                f"Checking if knowledge name '{knowledge.name}' exists in database."
            )

            conditions = [
                KnowledgeModel.name == knowledge.name,
                KnowledgeModel.is_active.is_(True),
            ]
            if knowledge.id is not None:
                conditions.append(KnowledgeModel.id != knowledge.id)

            result = await self.session.scalar(
                select(KnowledgeModel.id).where(*conditions).limit(1)
            )
            exists = result is not None

            logger.info(
                f"Existence check for knowledge name '{knowledge.name}' completed. Exists: {exists}."
            )
            return exists
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "Unexpected error during the existence check of a knowledge in the database."
            )
            raise KnowledgeException()

    async def get_all(
        self,
        knowledge: Knowledge,
        pagination: KnowledgePagination,
    ) -> KnowledgeList:
        try:
            logger.info(
                f"Getting all active knowledge bases from database. Requested by user {knowledge.created_by.id}."
            )

            col = getattr(KnowledgeModel, pagination.sort_by.value)
            ordering = (
                col.asc() if pagination.sort_order == SortOrder.ASC else col.desc()
            )

            statement = (
                select(
                    KnowledgeModel,
                    func.count(KnowledgeModel.id).over().label("total"),
                )
                .where(KnowledgeModel.is_active.is_(True))
                .order_by(ordering)
                .offset(pagination.offset)
                .limit(pagination.per_page)
            )

            result = await self.session.execute(statement)
            rows = result.all()

            knowledge_list = models_knowledge_list_mapper(rows)

            logger.info(
                f"Retrieved {len(knowledge_list.items)} of {knowledge_list.total} active knowledge base(s) from database."
            )
            return knowledge_list
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the get all knowledge bases repository."
            )
            raise KnowledgeException()

    # UPDATE
    async def update(self, knowledge: Knowledge) -> Knowledge:
        try:
            logger.info(
                f"Updating knowledge '{knowledge.id}' in database. Requested by user {knowledge.updated_by.id}."
            )

            model = await self.session.get(KnowledgeModel, knowledge.id)

            model.name = knowledge.name
            model.description = knowledge.description
            model.updated_by = knowledge.updated_by.id
            model.is_active = knowledge.is_active

            await self.session.flush()

            logger.info(f"Knowledge '{knowledge.id}' updated successfully in database.")
            return model_entity_mapper(model)
        except StandardException:
            raise
        except Exception as e:
            logger.opt(exception=e).error(
                "An error occurred in the update knowledge repository."
            )
            raise KnowledgeException()
