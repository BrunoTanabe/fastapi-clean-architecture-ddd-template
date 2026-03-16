from typing import Union

from automapper import mapper

from app.modules.example.domain.entities import Example
from app.modules.example.domain.value_objects import FullName
from app.modules.example.presentation.schemas import ExampleRequest, ExampleResponse


async def example_entity_mapper(
    example: Union[ExampleRequest, Example],
) -> Union[Example, ExampleResponse]:
    if isinstance(example, ExampleRequest):
        return mapper.to(Example).map(
            example,
            fields_mapping={
                "full_name": FullName(
                    first_name=example.first_name, last_name=example.last_name
                )
            },
        )
    else:
        return mapper.to(ExampleResponse).map(example)
