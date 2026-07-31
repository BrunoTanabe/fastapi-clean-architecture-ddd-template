from enum import Enum


class KnowledgeSortField(str, Enum):
    NAME = "name"
    UPDATED_AT = "updated_at"
    CREATED_AT = "created_at"
