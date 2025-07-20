from fastapi import APIRouter, Depends
from loguru import logger

from app.core.exceptions import StandardException
from app.modules.example.application.use_cases import ExampleUseCases
from app.modules.example.domain.mappers import (
    domain_to_example_response,
    example_request_to_domain,
)
from app.modules.example.presentation.dependencies import get_example_use_cases
from app.modules.example.presentation.docs import example_docs, example_request_docs
from app.modules.example.presentation.exceptions import ExampleException
from app.modules.example.presentation.schemas import ExampleRequest, ExampleResponse

router = APIRouter(**example_docs)


@router.post("/", **example_request_docs)
async def hello(
    payload: ExampleRequest,
    use_case: ExampleUseCases = Depends(get_example_use_cases),
) -> ExampleResponse:
    try:
        request_domain = example_request_to_domain(payload)
        response_domain = await use_case.hello(request_domain)
        output = domain_to_example_response(response_domain)

        return output
    except StandardException:
        raise
    except Exception as e:
        logger.error(f"An error occurred in the hello endpoint: {e}")
        raise ExampleException()
