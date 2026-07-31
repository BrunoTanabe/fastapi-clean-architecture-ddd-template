from automapper import mapper

from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.domain.value_objects import Name
from app.modules.user.domain.entities import User
from app.modules.user.infrastructure.models import UserModel
from app.modules.user.presentation.schemas import (
    CreateRequest,
    CreateResponse,
    MeResponse,
)


# ENTITY / DTOS
def create_entity_mapper(payload: CreateRequest) -> User:
    return mapper.to(User).map(
        payload,
        fields_mapping={
            "name": Name(
                first_name=payload.first_name,
                last_name=payload.last_name,
                preferred_name=payload.preferred_name,
            ),
        },
    )


def entity_create_mapper(user: User) -> CreateResponse:
    return mapper.to(CreateResponse).map(user)


def me_entity_mapper(authentication: Authentication) -> User:
    return authentication.user


def entity_me_mapper(user: User) -> MeResponse:
    return mapper.to(MeResponse).map(
        user,
        fields_mapping={
            "first_name": user.name.first_name,
            "last_name": user.name.last_name,
            "preferred_name": user.name.preferred_name,
            "email": str(user.email),
            "phone": str(user.phone) if user.phone else None,
        },
    )


# ENTITY / MODELS
def model_entity_mapper(model: UserModel) -> User:
    return mapper.to(User).map(
        model,
        fields_mapping={
            "id": model.id,
            "name": Name(
                first_name=model.first_name,
                last_name=model.last_name,
                preferred_name=model.preferred_name,
            ),
            "gender": model.gender,
            "birthdate": model.birthdate,
            "email": str(model.email),
            "phone": str(model.phone) if model.phone else None,
            "hashed_password": model.hashed_password,
            "role": model.role,
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def entity_model_mapper(user: User) -> UserModel:
    return mapper.to(UserModel).map(
        user,
        fields_mapping={
            "id": user.id,
            "first_name": user.name.first_name,
            "last_name": user.name.last_name,
            "preferred_name": user.name.preferred_name,
            "gender": user.gender,
            "birthdate": user.birthdate,
            "email": str(user.email),
            "phone": str(user.phone) if user.phone else None,
            "hashed_password": user.hashed_password,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        },
    )
