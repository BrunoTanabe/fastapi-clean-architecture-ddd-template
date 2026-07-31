import hashlib
import hmac
import json
import re
import secrets
import uuid
from datetime import datetime, timezone

from fastapi import BackgroundTasks, Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jwcrypto import jwt
from jwcrypto.common import JWException
from jwcrypto.jwe import InvalidJWEData
from jwcrypto.jws import InvalidJWSSignature, InvalidJWSObject
from jwcrypto.jwt import (
    JWTExpired,
    JWTNotYetValid,
    JWTMissingClaim,
    JWTInvalidClaimValue,
    JWTInvalidClaimFormat,
)
from loguru import logger
from pwdlib import PasswordHash
from fastapi.requests import Request

from app.core.settings import settings, PathRule
from app.modules.authentication.application.interfaces import (
    IAuthenticationRepository,
    IAuthenticationCache,
)
from app.modules.authentication.domain.entities import (
    Authentication,
)
from app.modules.authentication.application.mappers import (
    access_token_entity_mapper,
    refresh_token_entity_mapper,
)
from app.modules.authentication.application.exceptions import (
    AuthenticationTokenExpiredException,
    AuthenticationTokenNotYetValidException,
    AuthenticationTokenException,
    AuthenticationTokenMalformedError,
    AuthenticationException,
    HashingException,
    AuthenticationCookiesNotProvidedException,
    UserHasNotPermissionException,
    AuthenticationTokenInvalidException,
    ModifiedTokenException,
    RefreshTokenNotProvidedException,
    RefreshTokenExpiredException,
    RefreshTokenNotYetValidException,
    RefreshTokenException,
    RefreshTokenMalformedError,
    RefreshTokenInvalidEndpoint,
)
from app.modules.key.application.exceptions import (
    KeyException,
    ApiKeyNotProvidedException,
    ApiKeyInvalidException,
    ApiKeyRevokedException,
    ApiKeyExpiredException,
)
from app.modules.key.application.interfaces import IKeyCache, IKeyRepository
from app.modules.key.domain.entities import Key
from app.modules.shared.application.exceptions import OriginNotAllowedException
from app.modules.shared.domain.enums import Role
from app.modules.shared.presentation.dependencies import (
    get_authentication_cache,
    get_authentication_repository,
    get_key_cache,
    get_key_repository,
)
from app.modules.shared.application.exceptions import StandardException


# PASSWORD HASHING
password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    try:
        return password_hasher.hash(password)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during password hashing.")
        raise HashingException()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during password verification.")
        raise HashingException()


# JWT TOKEN (JWS + JWE)
def generate_tokens(authentication: Authentication) -> Authentication:
    try:
        # access token
        authentication.refresh_token.access_token.set_claims(
            iss=settings.JWT_ISSUER,
            sub=authentication.user.id,
            aud=settings.JWT_AUDIENCE,
            jti=uuid.uuid4(),
            grant_id=str(authentication.user.email),
            scope=str(authentication.user.role.value),
        )

        inner = jwt.JWT(
            header={
                "alg": "EdDSA",
                "typ": "access+jwt",
            },
            claims=authentication.refresh_token.access_token.claims.to_dict(),
        )

        inner.make_signed_token(settings.JWT_SIGNING_PRIVATE_KEY)
        signed_jwt = inner.serialize()

        outer = jwt.JWT(
            header={
                "alg": "ECDH-ES+A256KW",
                "enc": "A256GCM",
                "cty": "JWT",
            },
            claims=signed_jwt,
        )

        outer.make_encrypted_token(settings.JWT_ENCRYPTION_PUBLIC_KEY)
        authentication.refresh_token.access_token.token = outer.serialize()

        # refresh token
        authentication.refresh_token.set_claims(
            iss=settings.JWT_ISSUER,
            sub=authentication.user.id,
            aud=settings.JWT_AUDIENCE,
            jti=uuid.uuid4(),
            client_id=str(settings.APPLICATION_URL),
            grant_id=str(authentication.user.email),
            scope=str(authentication.user.role.value),
        )

        inner = jwt.JWT(
            header={
                "alg": "EdDSA",
                "typ": "refresh+jwt",
            },
            claims=authentication.refresh_token.refresh_claims.to_dict(),
        )

        inner.make_signed_token(settings.JWT_SIGNING_PRIVATE_KEY)
        signed_jwt = inner.serialize()

        outer = jwt.JWT(
            header={
                "alg": "ECDH-ES+A256KW",
                "enc": "A256GCM",
                "cty": "JWT",
            },
            claims=signed_jwt,
        )

        outer.make_encrypted_token(settings.JWT_ENCRYPTION_PUBLIC_KEY)
        authentication.refresh_token.token = outer.serialize()

        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token generation.")
        raise AuthenticationException()


def decode_nested_access_token(token: str) -> Authentication:
    try:
        outer = jwt.JWT(
            jwt=token,
            key=settings.JWT_ENCRYPTION_PRIVATE_KEY,
            expected_type="JWE",
            algs=["ECDH-ES+A256KW", "A256GCM"],
        )
        inner_raw = outer.claims

        inner = jwt.JWT(
            jwt=inner_raw,
            key=settings.JWT_SIGNING_PUBLIC_KEY,
            expected_type="JWS",
            algs=["EdDSA"],
            check_claims={
                "iss": settings.JWT_ISSUER,
                "sub": None,
                "aud": settings.JWT_AUDIENCE,
                "jti": None,
                "grant_id": None,
                "scope": None,
                "iat": None,
                "exp": None,
                "nbf": None,
            },
        )

        authentication: Authentication = access_token_entity_mapper(
            json.loads(inner.claims)
        )

        logger.debug(
            f"Access token decoded successfully for user: {authentication.user.email} with role: {authentication.user.role.value}"
        )
        return authentication
    except JWTExpired:
        logger.warning(
            "Attempt to use an expired token. Raising token expired exception."
        )
        raise AuthenticationTokenExpiredException()
    except JWTNotYetValid:
        logger.warning(
            "Attempt to use a token that has not yet been valid. Raising token not yet valid exception."
        )
        raise AuthenticationTokenNotYetValidException()
    except JWTMissingClaim as e:
        logger.opt(exception=e).warning(
            "Attempt to use a token with missing claims. Raising authentication token exception."
        )
        raise AuthenticationTokenException()
    except JWTInvalidClaimValue as e:
        logger.opt(exception=e).warning(
            "Attempt to use a token with invalid claims. Raising authentication token exception."
        )
        raise AuthenticationTokenException()
    except JWTInvalidClaimFormat as e:
        logger.opt(exception=e).warning(
            "Attempt to use a token with invalid claim format. Raising token authentication exception."
        )
        raise AuthenticationTokenException()
    except InvalidJWSSignature as e:
        logger.opt(exception=e).warning(
            "Attempt to use a token with an invalid signature. Raising token authentication exception."
        )
        raise AuthenticationTokenException()
    except (InvalidJWEData, InvalidJWSObject) as e:
        logger.opt(exception=e).warning(
            "Attempt to use a token with an invalid format. Raising token authentication exception."
        )
        raise AuthenticationTokenException()
    except json.JSONDecodeError as e:
        logger.opt(exception=e).warning(
            "Attempt to use a token with an invalid format. Raising token authentication exception."
        )
        raise AuthenticationTokenMalformedError()
    except JWException as e:
        logger.opt(exception=e).error(
            "Attempt to use a token with an invalid format or signature. Raising token authentication exception."
        )
        raise AuthenticationTokenException()
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token decoding.")
        raise AuthenticationTokenException()


def decode_nested_refresh_token(token: str) -> Authentication:
    try:
        outer = jwt.JWT(
            jwt=token,
            key=settings.JWT_ENCRYPTION_PRIVATE_KEY,
            expected_type="JWE",
            algs=["ECDH-ES+A256KW", "A256GCM"],
        )
        inner_raw = outer.claims

        inner = jwt.JWT(
            jwt=inner_raw,
            key=settings.JWT_SIGNING_PUBLIC_KEY,
            expected_type="JWS",
            algs=["EdDSA"],
            check_claims={
                "iss": settings.JWT_ISSUER,
                "sub": None,
                "aud": settings.JWT_AUDIENCE,
                "jti": None,
                "client_id": None,
                "grant_id": None,
                "scope": None,
                "iat": None,
                "exp": None,
                "nbf": None,
            },
        )

        authentication: Authentication = refresh_token_entity_mapper(
            json.loads(inner.claims)
        )

        logger.debug(
            f"Refresh token decoded successfully for user: {authentication.user.email} with role: {authentication.user.role.value}"
        )
        return authentication
    except JWTExpired:
        logger.warning(
            "Attempt to use an expired refresh token. Raising refresh token expired exception."
        )
        raise RefreshTokenExpiredException()
    except JWTNotYetValid:
        logger.warning(
            "Attempt to use a refresh token that has not yet been valid. Raising refresh token not yet valid exception."
        )
        raise RefreshTokenNotYetValidException()
    except JWTMissingClaim as e:
        logger.opt(exception=e).warning(
            "Attempt to use a refresh token with missing claims. Raising authentication refresh token exception."
        )
        raise RefreshTokenException()
    except JWTInvalidClaimValue as e:
        logger.opt(exception=e).warning(
            "Attempt to use a refresh token with invalid claims. Raising authentication refresh token exception."
        )
        raise RefreshTokenException()
    except JWTInvalidClaimFormat as e:
        logger.opt(exception=e).warning(
            "Attempt to use a refresh token with invalid claim format. Raising refresh token authentication exception."
        )
        raise RefreshTokenException()
    except InvalidJWSSignature as e:
        logger.opt(exception=e).warning(
            "Attempt to use a refresh token with an invalid signature. Raising refresh token authentication exception."
        )
        raise RefreshTokenException()
    except (InvalidJWEData, InvalidJWSObject) as e:
        logger.opt(exception=e).warning(
            "Attempt to use a refresh token with an invalid format. Raising refresh token authentication exception."
        )
        raise RefreshTokenException()
    except json.JSONDecodeError as e:
        logger.opt(exception=e).warning(
            "Attempt to use a refresh token with an invalid format. Raising refresh token authentication exception."
        )
        raise RefreshTokenMalformedError()
    except JWException as e:
        logger.opt(exception=e).error(
            "Attempt to use a refresh token with an invalid format or signature. Raising refresh token authentication exception."
        )
        raise RefreshTokenException()
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during refresh token decoding."
        )
        raise RefreshTokenException()


# JWT HASHING
def _token_fingerprint(material: str, namespace: str) -> str:
    try:
        key = bytes.fromhex(settings.JWT_HASH_FINGERPRINT)
        msg = f"{namespace}:{material}".encode("utf-8")

        return hmac.new(key, msg, hashlib.sha256).hexdigest()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token hashing.")
        raise HashingException()


def hash_tokens(authentication: Authentication) -> Authentication:
    try:
        access_claims = authentication.refresh_token.access_token.claims
        authentication.refresh_token.access_token.hashed_jti = (
            _token_fingerprint(str(access_claims.jti), "access-jti")
            if access_claims and access_claims.jti
            else None
        )

        refresh_claims = authentication.refresh_token.refresh_claims
        authentication.refresh_token.hashed_jti = (
            _token_fingerprint(str(refresh_claims.jti), "refresh-jti")
            if refresh_claims and refresh_claims.jti
            else None
        )

        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token hashing.")
        raise HashingException()


def _match_path_rules(paths: tuple[PathRule, ...], path: str, method: str) -> bool:
    for allowed_path in paths:
        if allowed_path["method"] != method:
            continue

        pattern = allowed_path["endpoint"]
        pattern = pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
        pattern = f"^{pattern}$"

        if re.match(pattern, path):
            return True

    return False


# API KEY AUTHENTICATION
api_key_header = APIKeyHeader(
    name=settings.AUTH_API_KEY_NAME,
    scheme_name=settings.AUTH_API_KEY_SCHEME_NAME,
    description=settings.AUTH_API_KEY_DESCRIPTION,
    auto_error=False,
)


def _api_key_fingerprint(material: str) -> str:
    try:
        key = bytes.fromhex(settings.API_KEY_HASH_FINGERPRINT)
        msg = f"api-key:{material}".encode("utf-8")

        return hmac.new(key, msg, hashlib.sha256).hexdigest()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during API key hashing.")
        raise HashingException()


def generate_api_key(key: Key) -> Key:
    try:
        key.prefix = settings.API_KEY_PREFIX
        random_part = secrets.token_urlsafe(settings.API_KEY_ENTROPY_BYTES)
        raw_key = f"{key.prefix}_{random_part}"

        key.plain_key = raw_key
        key.hashed_key = _api_key_fingerprint(raw_key)
        key.last_four = random_part[-4:]

        logger.debug(
            f"API key '{key.prefix}...{key.last_four}' generated successfully."
        )
        return key
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during API key generation.")
        raise KeyException()


def _has_access_to_api_key_endpoint(path: str, method: str) -> bool:
    try:
        logger.debug(
            f"Checking if API key has access to endpoint '{path}' with method '{method}'."
        )

        if _match_path_rules(settings.SECURITY_API_KEY_ALLOWED_PATHS, path, method):
            logger.debug(
                f"API key has access to endpoint '{path}' with method '{method}'."
            )
            return True

        logger.debug(
            f"API key does not have access to endpoint '{path}' with method '{method}'."
        )
        return False
    except StandardException:
        return False
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during API key endpoint access check."
        )
        return False


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    try:
        computed = _api_key_fingerprint(plain_key)

        return hmac.compare_digest(computed, hashed_key)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during API key verification.")
        raise HashingException()


async def _resolve_api_key(
    request: Request,
    background_tasks: BackgroundTasks,
    plain_key: str | None = Depends(api_key_header),
    repository: IKeyRepository = Depends(get_key_repository),
    cache: IKeyCache = Depends(get_key_cache),
) -> Key:
    if not plain_key:
        raise ApiKeyNotProvidedException()

    fingerprint = _api_key_fingerprint(plain_key)

    db_key: Key | None = await cache.get_by_hashed_key(fingerprint)

    if db_key is None:
        db_key = await repository.get_key_by_hashed_key(fingerprint)

        if db_key is not None:
            background_tasks.add_task(cache.insert, db_key)

    if db_key is None or not verify_api_key(plain_key, db_key.hashed_key):
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            f"API key attempt from '{client_host}' to endpoint '{request.url.path}' with method '{request.method}' did not match any key. Raising API key invalid exception."
        )
        raise ApiKeyInvalidException()

    if not db_key.is_active:
        logger.info(
            f"Revoked API key '{db_key.prefix}...{db_key.last_four}' was used on endpoint '{request.url.path}' with method '{request.method}'. Raising API key revoked exception."
        )
        raise ApiKeyRevokedException()

    if db_key.expires_at is not None and db_key.expires_at < datetime.now(timezone.utc):
        logger.info(
            f"Expired API key '{db_key.prefix}...{db_key.last_four}' was used on endpoint '{request.url.path}' with method '{request.method}'. Raising API key expired exception."
        )
        raise ApiKeyExpiredException()

    return db_key


async def authenticate_api_key(
    request: Request,
    key: Key = Depends(_resolve_api_key),
) -> Key:
    try:
        logger.debug(
            f"Authenticating API key for endpoint '{request.url.path}' with method '{request.method}'."
        )

        if not _has_access_to_api_key_endpoint(request.url.path, request.method):
            logger.info(
                f"API key '{key.prefix}...{key.last_four}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the API key allowed paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(
            f"API key '{key.prefix}...{key.last_four}' authenticated successfully."
        )
        return key
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during API key authentication process."
        )
        raise KeyException()


# BEARER TOKEN AUTHENTICATION
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/authentication/login/",
    refreshUrl="/api/v1/authentication/refresh/",
    scheme_name=settings.AUTH_BEARER_TOKEN_SCHEME_NAME,
    description=settings.AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION,
    auto_error=False,
)


def _matches_authentication_binding(
    cached: Authentication, authentication: Authentication
) -> bool:
    if cached.blacklisted:
        return False

    if cached.refresh_token is None or cached.refresh_token.revoked:
        return False

    if cached.user is None or cached.user.id != authentication.user.id:
        return False

    if cached.user_agent != authentication.user_agent:
        return False

    if authentication.device is not None and cached.device != authentication.device:
        return False

    return True


async def _resolve_access_token_authentication(
    request: Request,
    background_tasks: BackgroundTasks,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    cache: IAuthenticationCache = Depends(get_authentication_cache),
) -> Authentication:
    token = request.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
    device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

    if not token or not device:
        raise AuthenticationCookiesNotProvidedException()

    authentication: Authentication = decode_nested_access_token(token)
    authentication: Authentication = hash_tokens(authentication)

    authentication.device = device
    authentication.user_agent = (
        (request.headers.get("user-agent") or "").lower().strip()
    )

    # Cache-aside: read from Redis first, fall back to PostgreSQL on a miss and
    # repopulate the cache after the response is sent, never before it.
    db_authentication: Authentication | None = await cache.get_by_access_token(
        authentication
    )

    if db_authentication is not None:
        access_token = (
            db_authentication.refresh_token.access_token
            if db_authentication.refresh_token
            else None
        )

        if (
            access_token is None
            or access_token.revoked
            or not _matches_authentication_binding(db_authentication, authentication)
        ):
            logger.info(
                "Cached authentication did not match the request binding. Falling back to the database."
            )
            db_authentication = None

    if db_authentication is None:
        db_authentication = await repository.get_access_token_by_authentication(
            authentication
        )

        if db_authentication is not None:
            background_tasks.add_task(
                cache.insert_by_access_token,
                db_authentication,
                settings.REDIS_SESSION_TTL_SECONDS,
            )

    if (
        db_authentication is None
        or db_authentication.refresh_token is None
        or db_authentication.refresh_token.access_token is None
    ):
        logger.info(
            f"Access token with hashed jti '{authentication.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
        )
        raise AuthenticationTokenInvalidException()

    authentication: Authentication = db_authentication

    if (
        not authentication.user.role
        == authentication.refresh_token.access_token.permission
    ):
        logger.info(
            f"User '{authentication.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with modified role. Raising authentication exception."
        )
        raise ModifiedTokenException()

    return authentication


def _assert_endpoint_access(request: Request, authentication: Authentication) -> None:
    if not _has_access_to_endpoint(
        request.url.path, request.method, authentication.user.role
    ):
        logger.info(
            f"User '{authentication.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the allowed paths. Raising authentication exception."
        )
        raise UserHasNotPermissionException()


def _has_access_to_endpoint(path: str, method: str, role: Role | None = None) -> bool:
    try:
        logger.debug(
            f"Checking if user has access to endpoint '{path}' with method '{method}'."
        )

        if role is None:
            paths = settings.SECURITY_NO_AUTH_PATHS
        elif role == Role.ADMIN:
            paths = settings.SECURITY_ADMIN_ALLOWED_PATHS
        elif role == Role.MANAGER:
            paths = settings.SECURITY_MANAGER_ALLOWED_PATHS
        else:
            paths = settings.SECURITY_USER_ALLOWED_PATHS

        if _match_path_rules(paths, path, method):
            logger.debug(
                f"User has access to endpoint '{path}' with method '{method}'."
            )
            return True

        logger.debug(
            f"User does not have access to endpoint '{path}' with method '{method}'."
        )
        return False
    except StandardException:
        return False
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during endpoint access check.")
        return False


async def no_authentication(request: Request) -> None:
    try:
        logger.debug(
            f"No authentication required for this endpoint '{request.url.path}'."
        )

        if not _has_access_to_endpoint(request.url.path, request.method):
            logger.info(
                f"Access attempt to endpoint '{request.url.path}' with method '{request.method}' that is not in the no authentication paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(f"No authentication required for endpoint '{request.url.path}'.")
        return None
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during no authentication process."
        )
        raise AuthenticationException()


async def authenticate_user(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        logger.debug(
            f"Authenticating user for endpoint '{request.url.path}' with method '{request.method}'."
        )

        _assert_endpoint_access(request, authentication)

        logger.debug(f"User '{authentication.user.email}' authenticated successfully.")
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during user authentication process."
        )
        raise AuthenticationException()


async def authenticate_manager(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        logger.debug(
            f"Authenticating manager for endpoint '{request.url.path}' with method '{request.method}'."
        )

        if authentication.refresh_token.access_token.permission == Role.USER:
            logger.info(
                f"User '{authentication.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with insufficient permissions. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        _assert_endpoint_access(request, authentication)

        logger.debug(
            f"Manager '{authentication.user.email}' authenticated successfully."
        )
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during manager authentication process."
        )
        raise AuthenticationException()


async def authenticate_admin(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        logger.debug(
            f"Authenticating admin for endpoint '{request.url.path}' with method '{request.method}'."
        )

        if not authentication.refresh_token.access_token.permission == Role.ADMIN:
            logger.info(
                f"User '{authentication.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with insufficient permissions. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        _assert_endpoint_access(request, authentication)

        logger.debug(f"Admin '{authentication.user.email}' authenticated successfully.")
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during admin authentication process."
        )
        raise AuthenticationException()


async def authenticate_refresh(
    request: Request,
    background_tasks: BackgroundTasks,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    cache: IAuthenticationCache = Depends(get_authentication_cache),
) -> Authentication:
    try:
        logger.debug("Authenticating access for refresh token endpoint.")

        if not request.url.path.endswith("/api/v1/authentication/refresh/"):
            logger.info(
                f"Access attempt to endpoint '{request.url.path}' with method '{request.method}' that is not the refresh token endpoint. Raising authentication exception."
            )
            raise RefreshTokenInvalidEndpoint()

        token = request.cookies.get(settings.COOKIES_REFRESH_TOKEN_KEY, None)
        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not token or not device:
            raise RefreshTokenNotProvidedException()

        authentication: Authentication = decode_nested_refresh_token(token)
        authentication: Authentication = hash_tokens(authentication)

        authentication.device = device
        authentication.user_agent = (
            (request.headers.get("user-agent") or "").lower().strip()
        )

        # Cache-aside: read from Redis first, fall back to PostgreSQL on a miss
        # and repopulate the cache after the response is sent, never before it.
        db_authentication: Authentication | None = await cache.get_by_refresh_token(
            authentication
        )

        if db_authentication is not None and not _matches_authentication_binding(
            db_authentication, authentication
        ):
            logger.info(
                "Cached authentication did not match the request binding. Falling back to the database."
            )
            db_authentication = None

        if db_authentication is None:
            db_authentication = await repository.get_refresh_token_by_authentication(
                authentication
            )

            if db_authentication is not None:
                background_tasks.add_task(
                    cache.insert_by_refresh_token,
                    db_authentication,
                    settings.REDIS_SESSION_TTL_SECONDS,
                )

        if (
            db_authentication is None
            or db_authentication.refresh_token is None
            or db_authentication.refresh_token.access_token is None
        ):
            logger.info(
                f"Refresh token with hashed jti '{authentication.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
            )
            raise AuthenticationTokenInvalidException()

        logger.debug(
            f"Refresh token authenticated successfully for user '{authentication.user.email}'."
        )
        return db_authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during admin authentication process."
        )
        raise RefreshTokenException()


async def authenticate_logout(
    request: Request,
    authentication: Authentication = Depends(_resolve_access_token_authentication),
) -> Authentication:
    try:
        logger.debug("Authenticating access for logout endpoint.")

        if not request.url.path.endswith("/api/v1/authentication/logout/"):
            logger.info(
                f"Access attempt to endpoint '{request.url.path}' with method '{request.method}' that is not the refresh token endpoint. Raising authentication exception."
            )
            raise RefreshTokenInvalidEndpoint()

        if not _has_access_to_endpoint(
            request.url.path, request.method, authentication.user.role
        ):
            logger.info(
                f"User '{authentication.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the allowed paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(f"User '{authentication.user.email}' authenticated successfully.")
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during admin authentication process."
        )
        raise RefreshTokenException()


async def authenticate_websocket(
    websocket: WebSocket,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
    cache: IAuthenticationCache = Depends(get_authentication_cache),
) -> Authentication:
    try:
        logger.debug("Authenticating user for WebSocket connection.")

        origin = (websocket.headers.get("origin") or "").strip()
        if origin not in [str(o) for o in settings.SECURITY_ALLOW_ORIGINS]:
            logger.info(
                f"WebSocket connection rejected: origin '{origin}' not in allowlist."
            )
            raise OriginNotAllowedException()

        token = websocket.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = websocket.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not token or not device:
            raise AuthenticationCookiesNotProvidedException()

        authentication: Authentication = decode_nested_access_token(token)
        authentication: Authentication = hash_tokens(authentication)

        authentication.device = device
        authentication.user_agent = (
            (websocket.headers.get("user-agent") or "").lower().strip()
        )

        # Read-only cache-aside: WebSocket routes produce no Response, so there
        # is no BackgroundTasks to defer a write to. The cache is only read here
        # and stays populated by the HTTP paths, which share the same key.
        db_authentication: Authentication | None = await cache.get_by_access_token(
            authentication
        )

        if db_authentication is not None:
            access_token = (
                db_authentication.refresh_token.access_token
                if db_authentication.refresh_token
                else None
            )

            if (
                access_token is None
                or access_token.revoked
                or not _matches_authentication_binding(
                    db_authentication, authentication
                )
            ):
                logger.info(
                    "Cached WebSocket authentication did not match the request binding. Falling back to the database."
                )
                db_authentication = None

        if db_authentication is None:
            db_authentication = await repository.get_access_token_by_authentication(
                authentication
            )

        if (
            db_authentication is None
            or db_authentication.refresh_token is None
            or db_authentication.refresh_token.access_token is None
        ):
            logger.info(
                f"WebSocket access token with hashed jti "
                f"'{authentication.refresh_token.access_token.hashed_jti}' not found in database. "
                "Raising authentication exception."
            )
            raise AuthenticationTokenInvalidException()

        authentication = db_authentication

        if (
            not authentication.user.role
            == authentication.refresh_token.access_token.permission
        ):
            logger.info(
                f"WebSocket user '{authentication.user.email}' has a modified role token. "
                "Raising authentication exception."
            )
            raise ModifiedTokenException()

        logger.debug(
            f"WebSocket user '{authentication.user.email}' authenticated successfully."
        )
        return authentication
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during WebSocket authentication process."
        )
        raise AuthenticationException()
