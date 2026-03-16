import hashlib
import hmac
import json
import re
import uuid
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwcrypto import jwk, jwt
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

from app.core.settings import settings
from app.modules.authentication.application.interfaces import IAuthenticationRepository
from app.modules.authentication.domain.entities import (
    Session,
)
from app.modules.authentication.domain.mappers import (
    access_token_entity_mapper,
    refresh_token_entity_mapper,
)
from app.modules.authentication.presentation.exceptions import (
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
from app.modules.shared.application.enums import Role
from app.modules.shared.presentation.dependencies import get_authentication_repository
from app.modules.shared.presentation.exceptions import StandardException
from app.modules.user.domain.entities import User

# PASSWORD HASHING
password_hasher = PasswordHash.recommended()


async def hash_password(password: str) -> str:
    try:
        return password_hasher.hash(password)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during password hashing.")
        raise HashingException()


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(plain_password, hashed_password)
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during password verification.")
        raise HashingException()


# JWT TOKEN (JWS + JWE)
async def _read_pem(path: str) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during pem file reading.")
        raise AuthenticationException()


async def load_signing_private_key() -> jwk.JWK:
    try:
        password = settings.JWT_SIGNING_KEY_PASSWORD.encode("utf-8")

        return jwk.JWK.from_pem(
            await _read_pem(settings.JWT_SIGNING_PRIVATE_KEY_PATH), password=password
        )
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during private key loading.")
        raise AuthenticationException()


async def load_signing_public_key() -> jwk.JWK:
    try:
        return jwk.JWK.from_pem(await _read_pem(settings.JWT_SIGNING_PUBLIC_KEY_PATH))
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during public key loading.")
        raise AuthenticationException()


async def load_encryption_private_key() -> jwk.JWK:
    try:
        password = settings.JWT_ENCRYPTION_KEY_PASSWORD.encode("utf-8")

        return jwk.JWK.from_pem(
            await _read_pem(settings.JWT_ENCRYPTION_PRIVATE_KEY_PATH), password=password
        )
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during private key loading.")
        raise AuthenticationException()


async def load_encryption_public_key() -> jwk.JWK:
    try:
        return jwk.JWK.from_pem(
            await _read_pem(settings.JWT_ENCRYPTION_PUBLIC_KEY_PATH)
        )
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during public key loading.")
        raise AuthenticationException()


async def generate_tokens(session: Session) -> Session:
    try:
        # access token
        session.refresh_token.access_token.set_claims(
            iss=settings.JWT_ISSUER,
            sub=session.user.id,
            aud=settings.JWT_AUDIENCE,
            jti=uuid.uuid4(),
            grant_id=str(session.user.email),
            scope=str(session.user.role.value),
        )

        inner = jwt.JWT(
            header={
                "alg": "RS256",
                "typ": "access+jwt",
            },
            claims=session.refresh_token.access_token.claims.to_dict(),
        )

        inner.make_signed_token(await load_signing_private_key())
        signed_jwt = inner.serialize()

        outer = jwt.JWT(
            header={
                "alg": "RSA-OAEP-256",
                "enc": "A256GCM",
                "cty": "JWT",
            },
            claims=signed_jwt,
        )

        outer.make_encrypted_token(await load_encryption_public_key())
        session.refresh_token.access_token.token = outer.serialize()

        # refresh token
        session.refresh_token.set_claims(
            iss=settings.JWT_ISSUER,
            sub=session.user.id,
            aud=settings.JWT_AUDIENCE,
            jti=uuid.uuid4(),
            client_id=str(settings.APPLICATION_URL),
            grant_id=str(session.user.email),
            scope=str(session.user.role.value),
        )

        inner = jwt.JWT(
            header={
                "alg": "RS256",
                "typ": "refresh+jwt",
            },
            claims=session.refresh_token.refresh_claims.to_dict(),
        )

        inner.make_signed_token(await load_signing_private_key())
        signed_jwt = inner.serialize()

        outer = jwt.JWT(
            header={
                "alg": "RSA-OAEP-256",
                "enc": "A256GCM",
                "cty": "JWT",
            },
            claims=signed_jwt,
        )

        outer.make_encrypted_token(await load_encryption_public_key())
        session.refresh_token.token = outer.serialize()

        return session
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token generation.")
        raise AuthenticationException()


async def decode_nested_access_token(token: str) -> Session:
    try:
        outer = jwt.JWT(
            jwt=token,
            key=await load_encryption_private_key(),
            expected_type="JWE",
            algs=["RSA-OAEP-256", "A256GCM"],
        )
        inner_raw = outer.claims

        inner = jwt.JWT(
            jwt=inner_raw,
            key=await load_signing_public_key(),
            expected_type="JWS",
            algs=["RS256"],
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

        session: Session = await access_token_entity_mapper(json.loads(inner.claims))

        logger.debug(
            f"Access token decoded successfully for user: {session.user.email} with role: {session.user.role.value}"
        )
        return session
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


async def decode_nested_refresh_token(token: str) -> Session:
    try:
        outer = jwt.JWT(
            jwt=token,
            key=await load_encryption_private_key(),
            expected_type="JWE",
            algs=["RSA-OAEP-256", "A256GCM"],
        )
        inner_raw = outer.claims

        inner = jwt.JWT(
            jwt=inner_raw,
            key=await load_signing_public_key(),
            expected_type="JWS",
            algs=["RS256"],
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

        session: Session = await refresh_token_entity_mapper(json.loads(inner.claims))

        logger.debug(
            f"Refresh token decoded successfully for user: {session.user.email} with role: {session.user.role.value}"
        )
        return session
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
async def _token_fingerprint(material: str, namespace: str) -> str:
    try:
        key = bytes.fromhex(settings.JWT_HASH_FINGERPRINT)
        msg = f"{namespace}:{material}".encode("utf-8")

        return hmac.new(key, msg, hashlib.sha256).hexdigest()
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token hashing.")
        raise HashingException()


async def hash_tokens(session: Session) -> Session:
    try:
        access_claims = session.refresh_token.access_token.claims
        session.refresh_token.access_token.hashed_jti = (
            await _token_fingerprint(str(access_claims.jti), "access-jti")
            if access_claims and access_claims.jti
            else None
        )

        refresh_claims = session.refresh_token.refresh_claims
        session.refresh_token.hashed_jti = (
            await _token_fingerprint(str(refresh_claims.jti), "refresh-jti")
            if refresh_claims and refresh_claims.jti
            else None
        )

        return session
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error("An error occurred during token hashing.")
        raise HashingException()


# BEARER TOKEN AUTHENTICATION
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/authentication/login/",
    refreshUrl="/api/v1/authentication/refresh/",
    scheme_name=settings.AUTH_BEARER_TOKEN_SCHEME_NAME,
    description=settings.AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION,
    auto_error=False,
)


async def has_access_to_endpoint(
    path: str, method: str, role: Optional[Role] = None
) -> bool:
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

        for allowed_path in paths:
            if allowed_path["method"] != method:
                continue

            pattern = allowed_path["endpoint"]
            pattern = pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
            pattern = f"^{pattern}$"

            if re.match(pattern, path):
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
        logger.opt(exception=e).error(
            "An error occurred during has access to endpoint process."
        )
        return False


async def no_authentication(request: Request) -> None:
    try:
        logger.debug(
            f"No authentication required for this endpoint '{request.url.path}'."
        )

        if not await has_access_to_endpoint(request.url.path, request.method):
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
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
) -> User:
    try:
        logger.debug(
            f"Authenticating user for endpoint '{request.url.path}' with method '{request.method}'."
        )

        token = request.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not token or not device:
            raise AuthenticationCookiesNotProvidedException()

        session: Session = await decode_nested_access_token(token)
        session: Session = await hash_tokens(session)

        session.device = device
        session.user_agent = (request.headers.get("user-agent") or "").lower().strip()

        db_session: Optional[Session] = await repository.get_access_token_by_session(
            session
        )

        if (
            db_session is None
            or db_session.refresh_token is None
            or db_session.refresh_token.access_token is None
        ):
            logger.info(
                f"Access token with hashed jti '{session.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
            )
            raise AuthenticationTokenInvalidException()

        session: Session = db_session

        if not session.user.role == session.refresh_token.access_token.permission:
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with modified role. Raising authentication exception."
            )
            raise ModifiedTokenException()

        if not await has_access_to_endpoint(
            request.url.path, request.method, session.user.role
        ):
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the allowed paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(f"User '{session.user.email}' authenticated successfully.")
        return session.user
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during user authentication process."
        )
        raise AuthenticationException()


async def authenticate_manager(
    request: Request,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
) -> User:
    try:
        logger.debug(
            f"Authenticating manager for endpoint '{request.url.path}' with method '{request.method}'."
        )

        token = request.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not token or not device:
            raise AuthenticationCookiesNotProvidedException()

        session: Session = await decode_nested_access_token(token)
        session: Session = await hash_tokens(session)

        session.device = device
        session.user_agent = (request.headers.get("user-agent") or "").lower().strip()

        db_session: Optional[Session] = await repository.get_access_token_by_session(
            session
        )

        if (
            db_session is None
            or db_session.refresh_token is None
            or db_session.refresh_token.access_token is None
        ):
            logger.info(
                f"Access token with hashed jti '{session.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
            )
            raise AuthenticationTokenInvalidException()

        session: Session = db_session

        if not session.user.role == session.refresh_token.access_token.permission:
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with modified role. Raising authentication exception."
            )
            raise ModifiedTokenException()

        if session.refresh_token.access_token.permission == Role.USER:
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with insufficient permissions. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        if not await has_access_to_endpoint(
            request.url.path,
            request.method,
            session.refresh_token.access_token.permission,
        ):
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the allowed paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(f"Manager '{session.user.email}' authenticated successfully.")
        return session.user
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during manager authentication process."
        )
        raise AuthenticationException()


async def authenticate_admin(
    request: Request,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
) -> User:
    try:
        logger.debug(
            f"Authenticating admin for endpoint '{request.url.path}' with method '{request.method}'."
        )

        token = request.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not token or not device:
            raise AuthenticationCookiesNotProvidedException()

        session: Session = await decode_nested_access_token(token)
        session: Session = await hash_tokens(session)

        session.device = device
        session.user_agent = (request.headers.get("user-agent") or "").lower().strip()

        db_session: Optional[Session] = await repository.get_access_token_by_session(
            session
        )

        if (
            db_session is None
            or db_session.refresh_token is None
            or db_session.refresh_token.access_token is None
        ):
            logger.info(
                f"Access token with hashed jti '{session.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
            )
            raise AuthenticationTokenInvalidException()

        session: Session = db_session

        if not session.user.role == session.refresh_token.access_token.permission:
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with modified role. Raising authentication exception."
            )
            raise ModifiedTokenException()

        if not session.refresh_token.access_token.permission == Role.ADMIN:
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with insufficient permissions. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        if not await has_access_to_endpoint(
            request.url.path,
            request.method,
            session.refresh_token.access_token.permission,
        ):
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the allowed paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(f"Admin '{session.user.email}' authenticated successfully.")
        return session.user
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during admin authentication process."
        )
        raise AuthenticationException()


async def authenticate_refresh(
    request: Request,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
) -> Session:
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

        session: Session = await decode_nested_refresh_token(token)
        session: Session = await hash_tokens(session)

        session.device = device
        session.user_agent = (request.headers.get("user-agent") or "").lower().strip()

        db_session: Optional[Session] = await repository.get_refresh_token_by_session(
            session
        )

        if (
            db_session is None
            or db_session.refresh_token is None
            or db_session.refresh_token.access_token is None
        ):
            logger.info(
                f"Refresh token with hashed jti '{session.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
            )
            raise AuthenticationTokenInvalidException()

        logger.debug(
            f"Refresh token authenticated successfully for user '{session.user.email}'."
        )
        return db_session
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during admin authentication process."
        )
        raise RefreshTokenException()


async def authenticate_logout(
    request: Request,
    repository: IAuthenticationRepository = Depends(get_authentication_repository),
) -> Session:
    try:
        logger.debug("Authenticating access for logout endpoint.")

        if not request.url.path.endswith("/api/v1/authentication/logout/"):
            logger.info(
                f"Access attempt to endpoint '{request.url.path}' with method '{request.method}' that is not the refresh token endpoint. Raising authentication exception."
            )
            raise RefreshTokenInvalidEndpoint()

        token = request.cookies.get(settings.COOKIES_ACCESS_TOKEN_KEY, None)
        device = request.cookies.get(settings.COOKIES_DEVICE_KEY, None)

        if not token or not device:
            raise AuthenticationCookiesNotProvidedException()

        session: Session = await decode_nested_access_token(token)
        session: Session = await hash_tokens(session)

        session.device = device
        session.user_agent = (request.headers.get("user-agent") or "").lower().strip()

        db_session: Optional[Session] = await repository.get_access_token_by_session(
            session
        )

        if (
            db_session is None
            or db_session.refresh_token is None
            or db_session.refresh_token.access_token is None
        ):
            logger.info(
                f"Access token with hashed jti '{session.refresh_token.access_token.hashed_jti}' not found in database. Raising authentication token exception."
            )
            raise AuthenticationTokenInvalidException()

        session: Session = db_session

        if not session.user.role == session.refresh_token.access_token.permission:
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' with modified role. Raising authentication exception."
            )
            raise ModifiedTokenException()

        if not await has_access_to_endpoint(
            request.url.path, request.method, session.user.role
        ):
            logger.info(
                f"User '{session.user.email}' attempted to access endpoint '{request.url.path}' with method '{request.method}' that is not in the allowed paths. Raising authentication exception."
            )
            raise UserHasNotPermissionException()

        logger.debug(f"User '{session.user.email}' authenticated successfully.")
        return session
    except StandardException:
        raise
    except Exception as e:
        logger.opt(exception=e).error(
            "An error occurred during admin authentication process."
        )
        raise RefreshTokenException()
