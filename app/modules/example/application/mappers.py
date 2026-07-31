from automapper import mapper

from app.modules.example.domain.entities import Example
from app.modules.example.domain.value_objects import FullName
from app.modules.example.presentation.schemas import ExampleRequest, ExampleResponse
from app.modules.shared.domain.enums import ResponseMessages


# ENTITY / DTOS
def example_entity_mapper(payload: ExampleRequest) -> Example:
    return mapper.to(Example).map(
        payload,
        fields_mapping={
            "full_name": FullName(
                first_name=payload.first_name, last_name=payload.last_name
            )
        },
    )


def entity_example_mapper(example: Example) -> ExampleResponse:
    return mapper.to(ExampleResponse).map(
        example,
        fields_mapping={
            "message": ResponseMessages.SUCCESS.value,
            "greeting": example.message,
        },
    )
