from enum import Enum


class NotificationType(str, Enum):
    KNOWLEDGE_CREATED = "knowledge_created"
    KNOWLEDGE_UPDATED = "knowledge_updated"
    KNOWLEDGE_DELETED = "knowledge_deleted"
    SYSTEM_ALERT = "system_alert"


class NotificationSortField(str, Enum):
    CREATED_AT = "created_at"
    IS_READ = "is_read"
