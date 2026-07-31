from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from loguru import logger

from app.core.security import authenticate_user
from app.modules.authentication.domain.entities import Authentication
from app.modules.shared.domain.entities import DomainError
from app.modules.shared.application.exceptions import StandardException, DomainException
from app.modules.shared.presentation.schemas import UpdateResponse
from app.modules.notification.application.exceptions import NotificationException
from app.modules.notification.application.mappers import (
    get_all_entity_mapper,
    entities_get_all_mapper,
    mark_as_read_entity_mapper,
    entity_mark_as_read_mapper,
)
from app.modules.notification.application.use_cases import NotificationUseCases
from app.modules.notification.presentation.dependencies import (
    get_notification_use_cases,
)
from app.modules.notification.presentation.docs import (
    router_docs,
    get_all_docs,
    mark_as_read_docs,
)
from app.modules.notification.presentation.schemas import (
    GetAllNotificationsResponse,
    NotificationPaginationParams,
)

router = APIRouter(**router_docs)


# READ
@router.get("/", **get_all_docs)
@router.get("", include_in_schema=False)
async def get_all(
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    use_case: Annotated[NotificationUseCases, Depends(get_notification_use_cases)],
    query_params: Annotated[NotificationPaginationParams, Depends()],
) -> GetAllNotificationsResponse:
    try:
        request_domain, pagination = get_all_entity_mapper(authentication, query_params)
        notification_list = await use_case.get_all(request_domain, pagination)
        output = entities_get_all_mapper(notification_list, pagination)

        return output
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the get all notifications endpoint."
        )
        raise NotificationException()


# UPDATE
@router.patch("/{id}/", **mark_as_read_docs)
@router.patch("/{id}", include_in_schema=False)
async def mark_notification_as_read(
    id: UUID,
    authentication: Annotated[Authentication, Depends(authenticate_user)],
    use_case: Annotated[NotificationUseCases, Depends(get_notification_use_cases)],
) -> UpdateResponse:
    try:
        request_domain = mark_as_read_entity_mapper(authentication, id)
        response_domain = await use_case.mark_as_read(request_domain)

        return entity_mark_as_read_mapper(response_domain)
    except StandardException:
        raise
    except DomainError as e:
        raise DomainException(e)
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred in the mark notification as read endpoint."
        )
        raise NotificationException()
