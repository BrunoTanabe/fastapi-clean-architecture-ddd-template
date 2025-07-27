# Enum com os tipos de saúde disponíveis no sistema.
from enum import Enum


class HealthType(str, Enum):
    OK = "ok"
    ERROR = "error"

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [member.value for member in cls]
