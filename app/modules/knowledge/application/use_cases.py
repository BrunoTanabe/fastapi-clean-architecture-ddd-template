from loguru import logger

from app.modules.knowledge.application.exceptions import (
    KnowledgeException,
    KnowledgeNameAlreadyExistsException,
    KnowledgeNotFoundException,
    KnowledgeNotModifiedException,
)
from app.modules.knowledge.application.interfaces import (
    IKnowledgeCache,
    IKnowledgeRepository,
)
from app.modules.knowledge.domain.entities import (
    Knowledge,
    KnowledgeList,
    KnowledgePagination,
)
from app.modules.notification.domain.entities import Notification
from app.modules.notification.domain.enums import NotificationType
from app.modules.shared.application.exceptions import (
    DomainException,
    StandardException,
)
from app.modules.shared.application.use_cases import SharedUseCases
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.domain.enums import Role
from app.modules.shared.domain.value_objects import UNSET


class KnowledgeUseCases:
    def __init__(
        self,
        cache: IKnowledgeCache,
        repository: IKnowledgeRepository,
        shared_service: SharedUseCases,
    ) -> None:
        self.cache = cache
        self.repository = repository
        self.shared_service = shared_service
        self.shared_service.disable_exceptions()

    # CREATE
    async def create(self, knowledge: Knowledge) -> Knowledge:
        try:
            logger.debug(
                f"Initializing create knowledge use case for manager {knowledge.created_by.id} with name: {knowledge.name}."
            )

            if await self.repository.exists_by_name(knowledge):
                logger.info(
                    f"Knowledge with name '{knowledge.name}' already exists. Request by manager {knowledge.created_by.id}. Raising exception."
                )
                raise KnowledgeNameAlreadyExistsException(name=knowledge.name)

            creator = knowledge.created_by

            knowledge = await self.repository.create(knowledge)

            await self.shared_service.create_broadcast_notification(
                Notification(
                    originated_from_broadcast=Role.MANAGER,
                    notification_type=NotificationType.KNOWLEDGE_CREATED,
                    title="Knowledge base created",
                    body=f"Knowledge base '{knowledge.name}' was created by {creator.name}.",
                )
            )

            logger.debug(
                f"Knowledge '{knowledge.name}' created successfully by manager {creator.id}."
            )
            return knowledge
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the create knowledge use case."
            )
            raise KnowledgeException()

    # READ
    async def get_all(
        self,
        knowledge: Knowledge,
        pagination: KnowledgePagination,
    ) -> KnowledgeList:
        try:
            logger.debug(
                f"Initializing get all knowledge bases use case. Requested by manager {knowledge.created_by.id}."
            )

            knowledge_list = await self.repository.get_all(knowledge, pagination)

            logger.debug(
                f"Get all knowledge bases use case completed. Found {len(knowledge_list.items)} of {knowledge_list.total} total."
            )
            return knowledge_list
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the get all knowledge bases use case."
            )
            raise KnowledgeException()

    # UPDATE
    async def update(self, knowledge: Knowledge) -> Knowledge:
        try:
            logger.debug(
                f"Initializing update knowledge use case for manager {knowledge.updated_by.id}, knowledge id: {knowledge.id}."
            )

            existing = await self.repository.get_by_id(knowledge)
            if existing is None:
                logger.info(
                    f"Knowledge with id '{knowledge.id}' not found. Raising exception."
                )
                raise KnowledgeNotFoundException(id=str(knowledge.id))

            if knowledge.name is not UNSET and await self.repository.exists_by_name(
                knowledge
            ):
                logger.info(
                    f"Knowledge with name '{knowledge.name}' already exists. Raising exception."
                )
                raise KnowledgeNameAlreadyExistsException(name=knowledge.name)

            merged = Knowledge(
                id=knowledge.id,
                name=knowledge.name if knowledge.name is not UNSET else existing.name,
                description=(
                    knowledge.description
                    if knowledge.description is not UNSET
                    else existing.description
                ),
                updated_by=knowledge.updated_by,
                created_by=existing.created_by,
            )

            if (
                merged.name == existing.name
                and merged.description == existing.description
            ):
                logger.info(
                    f"No changes detected for knowledge '{knowledge.id}'. Raising not modified exception."
                )
                raise KnowledgeNotModifiedException(id=str(knowledge.id))

            updated = await self.repository.update(merged)

            logger.debug(
                f"Knowledge '{updated.name}' updated successfully by manager {knowledge.updated_by.id}."
            )
            return updated
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the update knowledge use case."
            )
            raise KnowledgeException()

    # DELETE
    async def delete(self, knowledge: Knowledge) -> Knowledge:
        try:
            logger.debug(
                f"Initializing delete knowledge use case for manager {knowledge.updated_by.id}, knowledge id: {knowledge.id}."
            )

            existing = await self.repository.get_by_id(knowledge)
            if existing is None:
                logger.info(
                    f"Knowledge with id '{knowledge.id}' not found. Raising exception."
                )
                raise KnowledgeNotFoundException(id=str(knowledge.id))

            existing.deactivate(knowledge.updated_by)
            deleted = await self.repository.update(existing)

            logger.debug(
                f"Knowledge '{deleted.name}' deactivated successfully by manager {knowledge.updated_by.id}."
            )
            return deleted
        except StandardException:
            raise
        except DomainError as e:
            raise DomainException(e)
        except Exception as e:
            logger.opt(exception=e).error(
                "An unexpected error occurred during the delete knowledge use case."
            )
            raise KnowledgeException()
