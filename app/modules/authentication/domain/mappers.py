from datetime import datetime
from typing import Union, Optional
from uuid import UUID

from automapper import mapper
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm

from app.modules.authentication.domain.entities import (
    Session,
    AccessToken,
    RefreshToken,
)
from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.authentication.infrastructure.models import (
    SessionModel,
    AccessTokenModel,
    RefreshTokenModel,
)
from app.modules.authentication.presentation.schemas import (
    LoginResponse,
    RefreshResponse,
    LogoutResponse,
)
from app.modules.shared.application.enums import Role
from app.modules.shared.application.utils import BRASILIA_TZ

from app.modules.user.domain.entities import User
from app.modules.user.domain.mappers import (
    model_entity_mapper as user_model_entity_mapper,
)


# ENTITY / DTOS
async def login_entity_mapper(
    session: Union[OAuth2PasswordRequestForm, Session],
    request: Optional[Request] = None,
) -> Union[Session, LoginResponse]:
    if isinstance(session, OAuth2PasswordRequestForm) and request is not None:
        return mapper.to(Session).map(
            session,
            fields_mapping={
                "user": User(email=session.username, password=session.password),
                "ip_address": request.headers.get("x-forwarded-for")
                or request.headers.get("x-real-ip")
                or request.client.host,
                "user_agent": request.headers.get("user-agent"),
                "device": getattr(request.state, "device_id", None),
                "accept_language": request.headers.get("accept-language"),
                "accept_encoding": request.headers.get("accept-encoding"),
                "origin": request.headers.get("origin"),
                "referer": request.headers.get("referer"),
                "location": getattr(request.state, "location", None),
                "refresh_token": RefreshToken(access_token=AccessToken()),
            },
        )
    elif isinstance(session, Session) and request is None:
        return LoginResponse()
    else:
        raise ValueError(
            "Session must be either a OAuth2PasswordRequestForm with a request or a Session without a request."
        )


async def refresh_entity_mapper(
    session: Session,
    output: bool = False,
) -> Union[Session, RefreshResponse]:
    if isinstance(session, Session) and not output:
        return session
    elif isinstance(session, Session) and output:
        return RefreshResponse()
    else:
        raise ValueError(
            "Session must be either a User with a request or a Session without a request."
        )


async def logout_entity_mapper(
    session: Session,
    output: bool = False,
) -> Union[Session, LogoutResponse]:
    if isinstance(session, Session) and not output:
        return session
    elif isinstance(session, Session) and output:
        return LogoutResponse()
    else:
        raise ValueError(
            "Session must be either a User with a request or a Session without a request."
        )


async def access_token_entity_mapper(claims: dict) -> Session:
    access = AccessToken(
        claims=Claims(claims),
        permission=Role(claims["scope"]),
        created_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
    )

    refresh = RefreshToken(access_token=access)

    return Session(
        user=User(
            id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"],
            role=Role(claims["scope"]),
            email=claims["grant_id"],
        ),
        refresh_token=refresh,
    )


async def refresh_token_entity_mapper(claims: dict) -> Session:
    access = AccessToken(
        permission=Role(claims["scope"]),
    )

    refresh = RefreshToken(
        access_token=access,
        refresh_claims=RefreshClaims(claims),
        updated_at=datetime.fromtimestamp(claims["iat"], tz=BRASILIA_TZ),
        expires_at=datetime.fromtimestamp(claims["exp"], tz=BRASILIA_TZ),
    )

    return Session(
        user=User(
            id=UUID(claims["sub"]) if isinstance(claims["sub"], str) else claims["sub"],
            role=Role(claims["scope"]),
            email=claims["grant_id"],
        ),
        refresh_token=refresh,
    )


# ENTITY / MODELS
async def model_entity_mapper(
    session: Union[
        SessionModel,
        Session,
        AccessTokenModel,
        AccessToken,
        RefreshTokenModel,
        RefreshToken,
    ],
) -> Union[
    Session,
    SessionModel,
    AccessToken,
    AccessTokenModel,
    RefreshToken,
    RefreshTokenModel,
]:
    if isinstance(session, SessionModel):
        mapped_user = (
            await user_model_entity_mapper(session.user) if session.user else None
        )

        mapped_access_token = None
        if session.refresh_token and session.refresh_token.access_token:
            access = session.refresh_token.access_token
            mapped_access_token = AccessToken(
                id=access.id,
                hashed_jti=access.hashed_jti,
                previous_hashed_jti=access.previous_hashed_jti,
                created_at=access.created_at,
                expires_at=access.expires_at,
                permission=access.permission,
            )

        mapped_refresh_token = None
        if session.refresh_token:
            refresh = session.refresh_token
            mapped_refresh_token = RefreshToken(
                id=refresh.id,
                hashed_jti=refresh.hashed_jti,
                previous_hashed_jti=refresh.previous_hashed_jti,
                created_at=refresh.created_at,
                updated_at=refresh.updated_at,
                expires_at=refresh.expires_at,
                access_token=mapped_access_token,
            )
            mapped_refresh_token.revoked = refresh.revoked
            mapped_refresh_token.revoked_at = refresh.revoked_at

        mapped_session = mapper.to(Session).map(
            session,
            fields_mapping={
                "id": session.id,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "device": session.device,
                "accept_language": session.accept_language,
                "accept_encoding": session.accept_encoding,
                "origin": session.origin,
                "referer": session.referrer,
                "location": session.location,
                "created_at": session.created_at,
                "last_updated_at": session.last_updated_at,
                "user": mapped_user,
                "refresh_token": mapped_refresh_token,
            },
        )
        mapped_session.blacklisted = session.blacklisted
        return mapped_session
    elif isinstance(session, Session):
        mapped_access_token = None
        if session.refresh_token and session.refresh_token.access_token:
            access = session.refresh_token.access_token
            mapped_access_token = AccessTokenModel(
                id=access.id,
                hashed_jti=access.hashed_jti,
                previous_hashed_jti=access.previous_hashed_jti,
                created_at=access.created_at,
                expires_at=access.expires_at,
                permission=access.permission,
            )

        mapped_refresh_token = None
        if session.refresh_token:
            refresh = session.refresh_token
            mapped_refresh_token = RefreshTokenModel(
                id=refresh.id,
                hashed_jti=refresh.hashed_jti,
                previous_hashed_jti=refresh.previous_hashed_jti,
                created_at=refresh.created_at,
                updated_at=refresh.updated_at,
                expires_at=refresh.expires_at,
                revoked=refresh.revoked if refresh.revoked is not None else False,
                revoked_at=refresh.revoked_at
                if refresh.revoked_at is not None
                else None,
                access_token=mapped_access_token,
            )

        session_model = SessionModel(
            id=session.id,
            user_id=session.user.id,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            device=session.device,
            accept_language=session.accept_language,
            accept_encoding=session.accept_encoding,
            origin=session.origin,
            referrer=session.referer,
            location=session.location,
            created_at=session.created_at,
            last_updated_at=session.last_updated_at,
            blacklisted=session.blacklisted,
        )
        session_model.refresh_token = mapped_refresh_token
        return session_model
    elif isinstance(session, AccessTokenModel):
        return AccessToken(
            id=session.id,
            hashed_jti=session.hashed_jti,
            previous_hashed_jti=session.previous_hashed_jti,
            created_at=session.created_at,
            expires_at=session.expires_at,
            permission=session.permission,
        )
    elif isinstance(session, AccessToken):
        return AccessTokenModel(
            id=session.id,
            hashed_jti=session.hashed_jti,
            previous_hashed_jti=session.previous_hashed_jti,
            created_at=session.created_at,
            expires_at=session.expires_at,
            permission=session.permission,
        )
    elif isinstance(session, RefreshTokenModel):
        mapped_refresh_token = RefreshToken(
            id=session.id,
            hashed_jti=session.hashed_jti,
            previous_hashed_jti=session.previous_hashed_jti,
            created_at=session.created_at,
            updated_at=session.updated_at,
            expires_at=session.expires_at,
            access_token=AccessToken(),
        )
        mapped_refresh_token.revoked = session.revoked
        mapped_refresh_token.revoked_at = session.revoked_at
        return mapped_refresh_token
    elif isinstance(session, RefreshToken):
        return RefreshTokenModel(
            id=session.id,
            hashed_jti=session.hashed_jti,
            previous_hashed_jti=session.previous_hashed_jti,
            created_at=session.created_at,
            updated_at=session.updated_at,
            expires_at=session.expires_at,
            revoked=session.revoked if session.revoked is not None else False,
            revoked_at=session.revoked_at if session.revoked_at is not None else None,
            access_token=AccessTokenModel(),
        )
    else:
        raise ValueError(
            "Session must be either a SessionModel, Session, AccessTokenModel, "
            "AccessToken, RefreshTokenModel or RefreshToken."
        )
