import secrets
from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader

from app.core.settings import settings

# API Key Authentication

api_key_header = APIKeyHeader(
    name=settings.SECURITY_API_KEY_HEADER,
    scheme_name=settings.SECURITY_SCHEME_NAME,
    description=settings.SECURITY_API_KEY_HEADER_DESCRIPTION,
    auto_error=False,
)


async def api_key_auth(
    api_key: str = Security(api_key_header),
) -> str:
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKeyAuth"},
        )

    if not secrets.compare_digest(api_key, settings.SECURITY_DEFAULT_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "ApiKeyAuth"},
        )

    return api_key
