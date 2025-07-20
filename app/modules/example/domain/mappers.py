from app.modules.example.domain.entities import Example
from app.modules.example.presentation.schemas import ExampleRequest, ExampleResponse


def example_request_to_domain(
    req: ExampleRequest,
) -> Example:
    return Example(
        name=req.name,
    )


def domain_to_example_response(
    entity: Example,
) -> ExampleResponse:
    if entity.message is None:
        raise ValueError("Entity message must be set, all fields must be filled.")

    return ExampleResponse(
        message=entity.message,
    )
