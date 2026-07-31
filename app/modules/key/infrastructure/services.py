from app.core.security import generate_api_key
from app.modules.key.application.interfaces import IKeyService
from app.modules.key.domain.entities import Key


class KeyService(IKeyService):
    async def generate(self, key: Key) -> Key:
        return generate_api_key(key)
