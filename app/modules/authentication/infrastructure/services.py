from app.core.security import (
    generate_tokens,
    hash_tokens,
    verify_password,
)
from app.modules.authentication.application.interfaces import ITokenService
from app.modules.authentication.domain.entities import Authentication


class TokenService(ITokenService):
    async def generate(self, authentication: Authentication) -> Authentication:
        return generate_tokens(authentication)

    async def hash_tokens(self, authentication: Authentication) -> Authentication:
        return hash_tokens(authentication)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)
