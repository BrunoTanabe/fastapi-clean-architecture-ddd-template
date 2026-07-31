from typing import Protocol

from app.modules.knowledge.domain.entities import (
    Knowledge,
    KnowledgeList,
    KnowledgePagination,
)


class IKnowledgeRepository(Protocol):
    # CREATE
    async def create(self, knowledge: Knowledge) -> Knowledge: ...

    # READ
    async def exists_by_name(self, knowledge: Knowledge) -> bool: ...

    async def get_by_id(self, knowledge: Knowledge) -> Knowledge | None: ...

    async def get_all(
        self,
        knowledge: Knowledge,
        pagination: KnowledgePagination,
    ) -> KnowledgeList: ...

    # UPDATE
    async def update(self, knowledge: Knowledge) -> Knowledge: ...


class IKnowledgeCache(Protocol):
    # CREATE
    async def insert(self, knowledge: Knowledge) -> None: ...

    async def insert_many(self, knowledge_list: KnowledgeList) -> None: ...
