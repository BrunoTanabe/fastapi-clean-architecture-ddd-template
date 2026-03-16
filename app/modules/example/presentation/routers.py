from typing import Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.security import no_authentication
from app.modules.example.application.use_cases import ExampleUseCases
from app.modules.example.domain.mappers import example_entity_mapper
from app.modules.example.presentation.dependencies import get_example_use_cases
from app.modules.example.presentation.docs import example_docs, example_request_docs
from app.modules.example.presentation.exceptions import ExampleException
from app.modules.example.presentation.schemas import ExampleRequest, ExampleResponse
from app.modules.shared.presentation.exceptions import (
    StandardException,
    DomainError,
    DomainException,
)

router = APIRouter(**example_docs)


@router.post("/", **example_request_docs)
@router.post("", include_in_schema=False)
async def hello(
    payload: ExampleRequest,
    _: Annotated[None, Depends(no_authentication)],
    use_case: ExampleUseCases = Depends(get_example_use_cases),
) -> ExampleResponse:
    try:
        request_domain = await example_entity_mapper(payload)
        response_domain = await use_case.hello(request_domain)
        output = await example_entity_mapper(response_domain)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error("An error occurred in the hello router.")
        raise ExampleException()
