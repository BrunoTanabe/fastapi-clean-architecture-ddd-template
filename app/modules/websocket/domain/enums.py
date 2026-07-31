from enum import Enum


class WebSocketMessageType(str, Enum):
    NOTIFICATION = "notification"
