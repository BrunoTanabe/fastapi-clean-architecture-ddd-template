from enum import Enum


class HealthType(str, Enum):
    OK = "ok"
    ERROR = "error"
