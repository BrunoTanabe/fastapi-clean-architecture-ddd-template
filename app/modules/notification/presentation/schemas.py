from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from pydantic import BaseModel, Field, ConfigDict

from app.modules.notification.domain.enums import (
    NotificationSortField,
    NotificationType,
)
from app.modules.shared.domain.enums import ResponseMessages
from app.modules.shared.presentation.schemas import PaginationMeta, PaginationParams


# RESPONSE
class NotificationResponse(BaseModel):
    id: UUID = Field(
        title="ID",
        description="The unique identifier of the notification.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
        json_schema_extra={
            "example": "550e8400-e29b-41d4-a716-446655440000",
            "readOnly": True,
        },
    )

    created_at: datetime = Field(
        title="Created At",
        description="The timestamp when the notification was created.",
        examples=["2025-01-15T10:30:00Z", "2024-05-01T12:00:00Z"],
        json_schema_extra={
            "example": "2025-01-15T10:30:00Z",
            "readOnly": True,
        },
    )

    notification_type: NotificationType = Field(
        title="Notification Type",
        description=f"The event that triggered this notification. Allowed values: {', '.join([t.value for t in NotificationType])}.",
        examples=[
            NotificationType.KNOWLEDGE_CREATED.value,
            NotificationType.SYSTEM_ALERT.value,
        ],
        json_schema_extra={
            "example": NotificationType.KNOWLEDGE_CREATED.value,
            "readOnly": True,
        },
    )

    title: str = Field(
        title="Title",
        description="Short title of the notification.",
        examples=["Knowledge base created", "System alert"],
        json_schema_extra={
            "example": "Knowledge base created",
            "readOnly": True,
        },
    )

    body: str = Field(
        title="Body",
        description="Full text body of the notification.",
        examples=[
            "The knowledge base 'ML Fundamentals' was created successfully.",
            "Scheduled maintenance on 2025-02-01 at 02:00 UTC.",
        ],
        json_schema_extra={
            "example": "The knowledge base 'ML Fundamentals' was created successfully.",
            "readOnly": True,
        },
    )

    redirect_url: str | None = Field(
        default=None,
        title="Redirect URL",
        description="Optional URL for deep linking from the notification.",
        examples=["https://app.example.com/knowledge/550e8400", None],
        json_schema_extra={
            "example": "https://app.example.com/knowledge/550e8400",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="NotificationResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Notification payload delivered over WebSocket.",
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2025-01-15T10:30:00Z",
                "notification_type": NotificationType.KNOWLEDGE_CREATED.value,
                "title": "Knowledge base created",
                "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                "redirect_url": "https://app.example.com/knowledge/550e8400",
            },
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "created_at": "2025-01-15T10:30:00Z",
                    "notification_type": NotificationType.KNOWLEDGE_CREATED.value,
                    "title": "Knowledge base created",
                    "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                    "redirect_url": "https://app.example.com/knowledge/550e8400",
                },
                {
                    "id": "661f9511-f3ac-52e5-b827-557766551111",
                    "created_at": "2025-01-16T08:00:00Z",
                    "notification_type": NotificationType.SYSTEM_ALERT.value,
                    "title": "System alert",
                    "body": "Scheduled maintenance on 2025-02-01 at 02:00 UTC.",
                    "redirect_url": None,
                },
            ],
        },
    )


# QUERY PARAMS
class NotificationPaginationParams:
    def __init__(
        self,
        pagination: Annotated[PaginationParams, Depends()],
        sort_by: NotificationSortField = Query(
            default=NotificationSortField.CREATED_AT,
            title="Sort Field",
            description=f"Field to sort notifications by. Allowed values: {', '.join([f.value for f in NotificationSortField])}.",
        ),
    ):
        self.sort_order = pagination.sort_order
        self.page = pagination.page
        self.limit = pagination.limit
        self.offset = pagination.offset
        self.sort_by = sort_by


# LIST RESPONSE
class NotificationListItem(BaseModel):
    id: UUID = Field(
        title="ID",
        description="The unique identifier of the notification.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
        json_schema_extra={
            "example": "550e8400-e29b-41d4-a716-446655440000",
            "readOnly": True,
        },
    )

    notification_type: NotificationType = Field(
        title="Notification Type",
        description=f"The event that triggered this notification. Allowed values: {', '.join([t.value for t in NotificationType])}.",
        examples=[
            NotificationType.KNOWLEDGE_CREATED.value,
            NotificationType.SYSTEM_ALERT.value,
        ],
        json_schema_extra={
            "example": NotificationType.KNOWLEDGE_CREATED.value,
            "readOnly": True,
        },
    )

    title: str = Field(
        title="Title",
        description="Short title of the notification.",
        examples=["Knowledge base created", "System alert"],
        json_schema_extra={
            "example": "Knowledge base created",
            "readOnly": True,
        },
    )

    body: str = Field(
        title="Body",
        description="Full text body of the notification.",
        examples=[
            "The knowledge base 'ML Fundamentals' was created successfully.",
            "Scheduled maintenance on 2025-02-01 at 02:00 UTC.",
        ],
        json_schema_extra={
            "example": "The knowledge base 'ML Fundamentals' was created successfully.",
            "readOnly": True,
        },
    )

    redirect_url: str | None = Field(
        default=None,
        title="Redirect URL",
        description="Optional URL for deep linking from the notification.",
        examples=["https://app.example.com/knowledge/550e8400", None],
        json_schema_extra={
            "example": "https://app.example.com/knowledge/550e8400",
            "readOnly": True,
        },
    )

    is_read: bool = Field(
        title="Is Read",
        description="Whether the authenticated user has read this notification.",
        examples=[False, True],
        json_schema_extra={
            "example": False,
            "readOnly": True,
        },
    )

    created_at: datetime = Field(
        title="Created At",
        description="The timestamp when the notification was created.",
        examples=["2025-01-15T10:30:00Z", "2024-05-01T12:00:00Z"],
        json_schema_extra={
            "example": "2025-01-15T10:30:00Z",
            "readOnly": True,
        },
    )

    model_config = ConfigDict(
        title="NotificationListItem",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "A single notification item in a paginated list.",
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "notification_type": NotificationType.KNOWLEDGE_CREATED.value,
                "title": "Knowledge base created",
                "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                "redirect_url": "https://app.example.com/knowledge/550e8400",
                "is_read": False,
                "created_at": "2025-01-15T10:30:00Z",
            },
        },
    )


class GetAllNotificationsResponse(BaseModel):
    message: str = ResponseMessages.RETRIEVED.value
    notifications: list[NotificationListItem]
    pagination: PaginationMeta

    model_config = ConfigDict(
        title="GetAllNotificationsResponse",
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
        validate_return=True,
        json_schema_extra={
            "description": "Response model for retrieving all notifications for the authenticated user.",
            "example": {
                "message": ResponseMessages.RETRIEVED.value,
                "Notification": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "notification_type": NotificationType.KNOWLEDGE_CREATED.value,
                        "title": "Knowledge base created",
                        "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                        "redirect_url": "https://app.example.com/knowledge/550e8400",
                        "is_read": False,
                        "created_at": "2025-01-15T10:30:00Z",
                    }
                ],
                "pagination": {
                    "total": 1,
                    "page": 1,
                    "limit": 20,
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False,
                },
            },
            "examples": [
                {
                    "message": ResponseMessages.RETRIEVED.value,
                    "Notification": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "notification_type": NotificationType.KNOWLEDGE_CREATED.value,
                            "title": "Knowledge base created",
                            "body": "The knowledge base 'ML Fundamentals' was created successfully.",
                            "redirect_url": "https://app.example.com/knowledge/550e8400",
                            "is_read": False,
                            "created_at": "2025-01-15T10:30:00Z",
                        }
                    ],
                    "pagination": {
                        "total": 1,
                        "page": 1,
                        "limit": 20,
                        "total_pages": 1,
                        "has_next": False,
                        "has_prev": False,
                    },
                },
                {
                    "message": ResponseMessages.RETRIEVED.value,
                    "Notification": [],
                    "pagination": {
                        "total": 0,
                        "page": 1,
                        "limit": 20,
                        "total_pages": 0,
                        "has_next": False,
                        "has_prev": False,
                    },
                },
            ],
        },
    )
