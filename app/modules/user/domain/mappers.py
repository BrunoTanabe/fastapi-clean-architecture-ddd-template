from typing import Union

from automapper import mapper

from app.modules.user.domain.entities import User
from app.modules.user.domain.value_objects import Name
from app.modules.user.infrastructure.models import UserModel
from app.modules.user.presentation.schemas import (
    CreateRequest,
    CreateResponse,
    MeResponse,
)


# ENTITY / DTOS
async def create_entity_mapper(
    user: Union[CreateRequest, User],
) -> Union[User, CreateResponse]:
    if isinstance(user, CreateRequest):
        return mapper.to(User).map(
            user,
            fields_mapping={
                "name": Name(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    preferred_name=user.preferred_name,
                ),
            },
        )
    else:
        return mapper.to(CreateResponse).map(user)


async def me_entity_mapper(user: User) -> MeResponse:
    return mapper.to(MeResponse).map(
        user,
        fields_mapping={
            "first_name": user.name.first_name,
            "last_name": user.name.last_name,
            "preferred_name": user.name.preferred_name,
            "email": user.email.__str__(),
            "phone": user.phone.__str__() if user.phone else None,
        },
    )


# ENTITY / MODELS
async def model_entity_mapper(
    user: Union[UserModel, User],
) -> Union[User, UserModel]:
    if isinstance(user, UserModel):
        return mapper.to(User).map(
            user,
            fields_mapping={
                "id": user.id,
                "name": Name(
                    first_name=user.first_name,
                    last_name=user.last_name,
                    preferred_name=user.preferred_name,
                ),
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
    else:
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
