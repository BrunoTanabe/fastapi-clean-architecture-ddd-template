import math
from uuid import UUID

from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.knowledge.domain.entities import (
    Knowledge,
    KnowledgeList,
    KnowledgePagination,
)
from app.modules.knowledge.infrastructure.models import KnowledgeModel
from app.modules.knowledge.presentation.schemas import (
    CreateRequest,
    GetAllResponse,
    KnowledgeListItem,
    KnowledgePaginationParams,
    UpdateRequest,
)
from app.modules.shared.domain.enums import SortOrder
from app.modules.shared.domain.value_objects import UNSET
from app.modules.shared.presentation.schemas import (
    CreateResponse,
    DeleteResponse,
    PaginationMeta,
    UpdateResponse,
)
from app.modules.user.domain.entities import User


# ENTITY / DTOS
def create_entity_mapper(
    payload: CreateRequest, authentication: Authentication
) -> Knowledge:
    return mapper.to(Knowledge).map(
        payload,
        fields_mapping={
            "name": payload.name,
            "created_by": authentication.user,
            "updated_by": authentication.user,
        },
    )


def get_all_entity_mapper(
    authentication: Authentication, query_params: KnowledgePaginationParams
) -> tuple[Knowledge, KnowledgePagination]:
    knowledge = Knowledge(
        created_by=authentication.user, updated_by=authentication.user
    )
    pagination = KnowledgePagination(
        page=query_params.page,
        per_page=query_params.limit,
        sort_order=SortOrder(query_params.sort_order),
        sort_by=query_params.sort_by,
    )

    return knowledge, pagination


def delete_entity_mapper(id: UUID, authentication: Authentication) -> Knowledge:
    return Knowledge(id=id, updated_by=authentication.user)


def entity_delete_mapper(knowledge: Knowledge) -> DeleteResponse:
    return DeleteResponse()


def update_entity_mapper(
    id: UUID, payload: UpdateRequest, authentication: Authentication
) -> Knowledge:
    return Knowledge(
        id=id,
        name=payload.name if "name" in payload.model_fields_set else UNSET,
        description=payload.description
        if "description" in payload.model_fields_set
        else UNSET,
        updated_by=authentication.user,
    )


def entity_update_mapper(knowledge: Knowledge) -> UpdateResponse:
    return UpdateResponse()


def entity_create_mapper(knowledge: Knowledge) -> CreateResponse:
    return mapper.to(CreateResponse).map(knowledge)


def entities_get_all_mapper(
    knowledge_list: KnowledgeList, pagination: KnowledgePagination
) -> GetAllResponse:
    total = knowledge_list.total
    total_pages = math.ceil(total / pagination.per_page) if pagination.per_page else 0

    return GetAllResponse(
        knowledge_bases=[
            KnowledgeListItem(
                id=knowledge.id,
                name=knowledge.name,
                description=knowledge.description
                if knowledge.description is not UNSET
                else None,
                updated_at=knowledge.updated_at,
            )
            for knowledge in knowledge_list.items
        ],
        pagination=PaginationMeta(
            total=total,
            page=pagination.page,
            limit=pagination.per_page,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_prev=pagination.page > 1,
        ),
    )


# ENTITY / MODELS
def model_entity_mapper(model: KnowledgeModel) -> Knowledge:
    return mapper.to(Knowledge).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "created_by": User(id=model.created_by),
            "updated_by": User(id=model.updated_by),
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def models_knowledge_list_mapper(rows: list) -> KnowledgeList:
    return KnowledgeList(
        items=[model_entity_mapper(row[0]) for row in rows],
        total=rows[0][1] if rows else 0,
    )


def entity_model_mapper(knowledge: Knowledge) -> KnowledgeModel:
    return mapper.to(KnowledgeModel).map(
        knowledge,
        fields_mapping={
            "id": knowledge.id,
            "name": knowledge.name,
            "description": knowledge.description,
            "created_by": knowledge.created_by.id,
            "updated_by": knowledge.updated_by.id,
            "is_active": knowledge.is_active,
            "created_at": knowledge.created_at,
            "updated_at": knowledge.updated_at,
        },
    )
