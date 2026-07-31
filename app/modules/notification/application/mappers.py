import math
from uuid import UUID

from automapper import mapper

from app.modules.notification.domain.entities import (
    Notification,
    NotificationList,
    NotificationPagination,
)
from app.modules.notification.domain.value_objects import RedirectUrl
from app.modules.notification.infrastructure.models import NotificationModel
from app.modules.notification.presentation.schemas import (
    GetAllNotificationsResponse,
    NotificationListItem,
    NotificationPaginationParams,
    NotificationResponse,
)
from app.modules.shared.domain.enums import Role
from app.modules.shared.presentation.schemas import PaginationMeta, UpdateResponse
from app.modules.authentication.domain.entities import Authentication
from app.modules.user.domain.entities import User


# ENTITY / DTOS
def get_all_entity_mapper(
    authentication: Authentication, query_params: NotificationPaginationParams
) -> tuple[Notification, NotificationPagination]:
    notification = Notification(user=authentication.user)
    pagination = NotificationPagination(
        page=query_params.page,
        per_page=query_params.limit,
        sort_order=query_params.sort_order,
        sort_by=query_params.sort_by,
    )
    return notification, pagination


def entities_get_all_mapper(
    notification_list: NotificationList, pagination: NotificationPagination
) -> GetAllNotificationsResponse:
    total = notification_list.total
    total_pages = math.ceil(total / pagination.per_page) if pagination.per_page else 0

    return GetAllNotificationsResponse(
        notifications=[
            NotificationListItem(
                id=n.id,
                notification_type=n.notification_type,
                title=n.title,
                body=n.body,
                redirect_url=str(n.redirect_url) if n.redirect_url else None,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notification_list.items
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


def entity_notification_mapper(entity: Notification) -> NotificationResponse:
    return mapper.to(NotificationResponse).map(
        entity,
        fields_mapping={
            "id": entity.id,
            "redirect_url": str(entity.redirect_url) if entity.redirect_url else None,
        },
    )


# ENTITY / MODELS
def model_entity_mapper(model: NotificationModel) -> Notification:
    return mapper.to(Notification).map(
        model,
        fields_mapping={
            "id": model.id,
            "user": User(id=model.user_id),
            "notification_type": model.notification_type,
            "redirect_url": RedirectUrl(value=model.redirect_url)
            if model.redirect_url
            else None,
            "metadata": model.notification_metadata,
            "originated_from_broadcast": Role(model.originated_from_broadcast)
            if model.originated_from_broadcast
            else None,
            "is_read": model.is_read,
            "read_at": model.read_at,
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
        },
    )


def models_notification_list_mapper(rows: list) -> NotificationList:
    return NotificationList(
        items=[model_entity_mapper(row[0]) for row in rows],
        total=rows[0][1] if rows else 0,
    )


def mark_as_read_entity_mapper(
    authentication: Authentication, notification_id: UUID
) -> Notification:
    return Notification(user=authentication.user, id=notification_id)


def entity_mark_as_read_mapper(entity: Notification) -> UpdateResponse:
    return UpdateResponse()


def entity_model_mapper(entity: Notification) -> NotificationModel:
    return mapper.to(NotificationModel).map(
        entity,
        fields_mapping={
            "id": entity.id,
            "user_id": entity.user.id,
            "notification_type": entity.notification_type,
            "redirect_url": str(entity.redirect_url) if entity.redirect_url else None,
            "notification_metadata": entity.metadata,
            "originated_from_broadcast": entity.originated_from_broadcast.value
            if entity.originated_from_broadcast
            else None,
            "is_read": entity.is_read,
            "read_at": entity.read_at,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        },
    )
