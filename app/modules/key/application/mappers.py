import json
import math
from datetime import datetime
from uuid import UUID

from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.key.application.utils import resolve_expires_at
from app.modules.key.domain.entities import Key, KeyList, KeyPagination
from app.modules.key.infrastructure.models import KeyModel
from app.modules.key.presentation.schemas import (
    ActorResponse,
    CreateKeyResponse,
    CreateRequest,
    GetAllResponse,
    GetResponse,
    KeyListItem,
    KeyPaginationParams,
    RotateKeyResponse,
    UpdateRequest,
)
from app.modules.shared.domain.enums import SortOrder
from app.modules.shared.domain.value_objects import UNSET, Name
from app.modules.shared.presentation.schemas import (
    DeleteResponse,
    PaginationMeta,
    UpdateResponse,
)
from app.modules.user.domain.entities import User


# ENTITY / DTOS
def create_entity_mapper(payload: CreateRequest, authentication: Authentication) -> Key:
    return mapper.to(Key).map(
        payload,
        fields_mapping={
            "name": payload.name,
            "description": payload.description,
            "expires_at": resolve_expires_at(payload.expires_in),
            "created_by": authentication.user,
            "updated_by": authentication.user,
        },
    )


def entity_create_mapper(key: Key) -> CreateKeyResponse:
    return mapper.to(CreateKeyResponse).map(
        key,
        fields_mapping={
            "api_key": key.plain_key,
        },
    )


def get_all_entity_mapper(
    authentication: Authentication, query_params: KeyPaginationParams
) -> tuple[Key, KeyPagination]:
    key = Key(created_by=authentication.user, updated_by=authentication.user)
    pagination = KeyPagination(
        page=query_params.page,
        per_page=query_params.limit,
        sort_order=SortOrder(query_params.sort_order),
        sort_by=query_params.sort_by,
    )

    return key, pagination


def get_entity_mapper(id: UUID, authentication: Authentication) -> Key:
    return Key(id=id, created_by=authentication.user, updated_by=authentication.user)


def update_entity_mapper(
    id: UUID, payload: UpdateRequest, authentication: Authentication
) -> Key:
    return Key(
        id=id,
        name=payload.name if "name" in payload.model_fields_set else UNSET,
        description=payload.description
        if "description" in payload.model_fields_set
        else UNSET,
        updated_by=authentication.user,
    )


def entity_update_mapper(key: Key) -> UpdateResponse:
    return UpdateResponse()


def rotate_entity_mapper(id: UUID, authentication: Authentication) -> Key:
    return Key(id=id, updated_by=authentication.user)


def entity_rotate_mapper(key: Key) -> RotateKeyResponse:
    return mapper.to(RotateKeyResponse).map(
        key,
        fields_mapping={
            "api_key": key.plain_key,
        },
    )


def delete_entity_mapper(id: UUID, authentication: Authentication) -> Key:
    return Key(id=id, updated_by=authentication.user)


def entity_delete_mapper(key: Key) -> DeleteResponse:
    return DeleteResponse()


def _actor_response(user: User) -> ActorResponse:
    return ActorResponse(
        email=str(user.email),
        preferred_name=user.name.preferred_name,
    )


def entity_get_mapper(key: Key) -> GetResponse:
    return mapper.to(GetResponse).map(
        key,
        fields_mapping={
            "id": key.id,
            "name": key.name,
            "description": key.description if key.description is not UNSET else None,
            "prefix": key.prefix,
            "last_four": key.last_four,
            "expires_at": key.expires_at,
            "last_used_at": key.last_used_at,
            "created_by": _actor_response(key.created_by),
            "updated_by": _actor_response(key.updated_by),
            "created_at": key.created_at,
            "updated_at": key.updated_at,
        },
    )


def entities_get_all_mapper(
    key_list: KeyList, pagination: KeyPagination
) -> GetAllResponse:
    total = key_list.total
    total_pages = math.ceil(total / pagination.per_page) if pagination.per_page else 0

    return GetAllResponse(
        api_keys=[
            KeyListItem(
                id=key.id,
                name=key.name,
                description=key.description if key.description is not UNSET else None,
                created_at=key.created_at,
            )
            for key in key_list.items
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
def model_entity_mapper(model: KeyModel) -> Key:
    return mapper.to(Key).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "prefix": model.prefix,
            "last_four": model.last_four,
            "hashed_key": model.hashed_key,
            "expires_at": model.expires_at,
            "last_used_at": model.last_used_at,
            "created_by": User(id=model.created_by),
            "updated_by": User(id=model.updated_by),
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def _model_user_mapper(model) -> User:
    return User(
        id=model.id,
        name=Name(
            first_name=model.first_name,
            last_name=model.last_name,
            preferred_name=model.preferred_name,
        ),
        email=str(model.email),
    )


def model_entity_with_actors_mapper(model: KeyModel) -> Key:
    return mapper.to(Key).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": model.name,
            "description": model.description,
            "prefix": model.prefix,
            "last_four": model.last_four,
            "hashed_key": model.hashed_key,
            "expires_at": model.expires_at,
            "last_used_at": model.last_used_at,
            "created_by": _model_user_mapper(model.creator),
            "updated_by": _model_user_mapper(model.updater),
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def models_key_list_mapper(rows: list) -> KeyList:
    return KeyList(
        items=[model_entity_mapper(row[0]) for row in rows],
        total=rows[0][1] if rows else 0,
    )


def entity_model_mapper(key: Key) -> KeyModel:
    return mapper.to(KeyModel).map(
        key,
        fields_mapping={
            "id": key.id,
            "name": key.name,
            "description": key.description,
            "prefix": key.prefix,
            "last_four": key.last_four,
            "hashed_key": key.hashed_key,
            "expires_at": key.expires_at,
            "last_used_at": key.last_used_at,
            "created_by": key.created_by.id,
            "updated_by": key.updated_by.id,
            "is_active": key.is_active,
            "created_at": key.created_at,
            "updated_at": key.updated_at,
        },
    )


# ENTITY / CACHE
def entity_cache_mapper(key: Key) -> str:
    return json.dumps(
        {
            "id": str(key.id) if key.id else None,
            "name": key.name,
            "description": key.description if key.description is not UNSET else None,
            "prefix": key.prefix,
            "last_four": key.last_four,
            "hashed_key": key.hashed_key,
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            "created_by": str(key.created_by.id) if key.created_by else None,
            "updated_by": str(key.updated_by.id) if key.updated_by else None,
            "is_active": key.is_active,
            "created_at": key.created_at.isoformat() if key.created_at else None,
            "updated_at": key.updated_at.isoformat() if key.updated_at else None,
        }
    )


def cache_entity_mapper(raw: str) -> Key:
    data = json.loads(raw)

    key = Key(
        id=UUID(data["id"]) if data["id"] else None,
        name=data["name"],
        description=data["description"],
        prefix=data["prefix"],
        last_four=data["last_four"],
        hashed_key=data["hashed_key"],
        expires_at=datetime.fromisoformat(data["expires_at"])
        if data["expires_at"]
        else None,
        last_used_at=datetime.fromisoformat(data["last_used_at"])
        if data["last_used_at"]
        else None,
        created_by=User(id=UUID(data["created_by"])) if data["created_by"] else None,
        updated_by=User(id=UUID(data["updated_by"])) if data["updated_by"] else None,
        created_at=datetime.fromisoformat(data["created_at"])
        if data["created_at"]
        else None,
        updated_at=datetime.fromisoformat(data["updated_at"])
        if data["updated_at"]
        else None,
    )
    key.is_active = data["is_active"]
    return key
