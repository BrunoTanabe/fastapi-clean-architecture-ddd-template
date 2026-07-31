from redis.asyncio import Redis

from app.core.settings import settings
from app.modules.knowledge.application.interfaces import IKnowledgeCache


class RedisKnowledgeCache(IKnowledgeCache):
    def __init__(self, cache: Redis) -> None:
        self.cache = cache
        self.prefix = f"{settings.REDIS_NAMESPACE}:knowledge:"

    def _key(self, suffix: str) -> str:
        return f"{self.prefix}{suffix}"
