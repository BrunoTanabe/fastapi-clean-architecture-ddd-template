from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.modules.authentication.domain.value_objects import Claims, RefreshClaims
from app.modules.shared.domain.enums import Role
from app.modules.user.domain.entities import User


@dataclass(kw_only=True, slots=True)
class Authentication:
    ip_address: str | None = field(default=None, repr=True, compare=True)
    user_agent: str | None = field(default=None, repr=True, compare=True)
    device: str | None = field(default=None, repr=True, compare=True)
    location: str | None = field(default=None, repr=True, compare=False)
    accept_language: str | None = field(default=None, repr=True, compare=False)
    accept_encoding: str | None = field(default=None, repr=True, compare=False)
    origin: str | None = field(default=None, repr=True, compare=False)
    referer: str | None = field(default=None, repr=True, compare=False)

    # Application generated fields
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=False)
    last_updated_at: datetime | None = field(default=None, repr=False, compare=False)
    blacklisted: bool = field(init=False, default=False, repr=False, compare=False)

    # Foreign entities
    user: User = field(compare=True, repr=True)
    refresh_token: RefreshToken | None = field(default=None, compare=True, repr=True)

    def __post_init__(self):
        self._normalize()

    def _normalize(self):
        self.ip_address = self.ip_address.lower().strip() if self.ip_address else ""
        self.user_agent = self.user_agent.lower().strip() if self.user_agent else ""
        self.accept_language = (
            self.accept_language.lower().strip() if self.accept_language else None
        )
        self.accept_encoding = (
            self.accept_encoding.lower().strip() if self.accept_encoding else None
        )
        self.origin = self.origin.lower().strip() if self.origin else ""
        self.referer = self.referer.lower().strip() if self.referer else None
        self.location = self.location.lower().strip() if self.location else None

    def update_last_updated_at(self, now: datetime) -> None:
        self.last_updated_at = now

    def create_tokens(
        self,
        now: datetime,
        refresh_expires_at: datetime,
        access_expires_at: datetime,
    ) -> Authentication:
        self.refresh_token = RefreshToken(
            expires_at=refresh_expires_at,
            access_token=AccessToken(expires_at=access_expires_at),
        )
        self.refresh_token.generate_created_at(now)
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.access_token.generate_created_at(now)
        return self

    def renew_tokens(
        self,
        now: datetime,
        refresh_expires_at: datetime,
        access_expires_at: datetime,
    ) -> Authentication:
        self.update_last_updated_at(now)
        self.refresh_token.expires_at = refresh_expires_at
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.update_previous_hashed_jti()
        self.refresh_token.activate()
        self.refresh_token.access_token.expires_at = access_expires_at
        self.refresh_token.access_token.generate_created_at(now)
        self.refresh_token.access_token.update_previous_hashed_jti()
        self.refresh_token.access_token.activate()
        return self

    def refresh_access_token(
        self, now: datetime, access_expires_at: datetime
    ) -> Authentication:
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.update_previous_hashed_jti()
        self.refresh_token.access_token.expires_at = access_expires_at
        self.refresh_token.access_token.generate_created_at(now)
        self.refresh_token.access_token.update_previous_hashed_jti()
        return self

    def revoke(self, now: datetime) -> Authentication:
        self.refresh_token.generate_updated_at(now)
        self.refresh_token.revoke(now)
        return self


@dataclass(kw_only=True, slots=True)
class RefreshToken:
    token: str | None = field(default=None, repr=False, compare=False)
    hashed_jti: str | None = field(default=None, repr=False, compare=True)
    previous_hashed_jti: str | None = field(default=None, repr=False, compare=True)

    # Application generated fields
    replaced_by_token: UUID | None = field(default=None, repr=False, compare=False)
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=True)
    updated_at: datetime | None = field(default=None, repr=False, compare=False)
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    revoked: bool = field(init=False, default=False, repr=False, compare=False)
    revoked_at: datetime | None = field(
        init=False, default=None, repr=False, compare=False
    )
    refresh_claims: RefreshClaims | None = field(
        default=None, repr=False, compare=False
    )

    # Foreign entities
    access_token: AccessToken | None = field(default=None, repr=False, compare=False)

    def revoke(self, now: datetime) -> None:
        self.revoked = True
        self.revoked_at = now
        if self.access_token:
            self.access_token.revoke(now)

    def activate(self) -> None:
        self.revoked = False
        self.revoked_at = None

    def generate_created_at(self, dt: datetime) -> None:
        self.created_at = dt

    def generate_updated_at(self, dt: datetime) -> None:
        self.updated_at = dt

    def update_previous_hashed_jti(self) -> None:
        self.previous_hashed_jti = self.hashed_jti

    def set_claims(
        self,
        iss: str,
        sub: UUID,
        aud: str,
        jti: UUID,
        client_id: str,
        grant_id: str,
        scope: str,
    ) -> None:
        self.refresh_claims = RefreshClaims(
            iss=iss,
            sub=sub,
            aud=aud,
            iat=int(self.updated_at.timestamp()),
            nbf=int(self.updated_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            jti=jti,
            client_id=client_id,
            grant_id=grant_id,
            scope=scope,
        )


@dataclass(kw_only=True, slots=True)
class AccessToken:
    token: str | None = field(default=None, repr=False, compare=False)
    hashed_jti: str | None = field(default=None, repr=False, compare=True)
    previous_hashed_jti: str | None = field(default=None, repr=False, compare=True)
    permission: Role = field(default=Role.USER, repr=False, compare=False)

    # Application generated fields
    id: UUID | None = field(default=None, repr=True, compare=True)
    created_at: datetime | None = field(default=None, repr=False, compare=True)
    expires_at: datetime | None = field(default=None, repr=False, compare=False)
    claims: Claims | None = field(default=None, repr=False, compare=False)
    revoked: bool = field(init=False, default=False, repr=False, compare=False)
    revoked_at: datetime | None = field(
        init=False, default=None, repr=False, compare=False
    )

    def revoke(self, now: datetime) -> None:
        self.revoked = True
        self.revoked_at = now

    def activate(self) -> None:
        self.revoked = False
        self.revoked_at = None

    def generate_created_at(self, dt: datetime) -> None:
        self.created_at = dt

    def update_previous_hashed_jti(self) -> None:
        self.previous_hashed_jti = self.hashed_jti

    def set_claims(
        self, iss: str, sub: UUID, aud: str, jti: UUID, grant_id: str, scope: str
    ) -> None:
        self.claims = Claims(
            iss=iss,
            sub=sub,
            aud=aud,
            iat=int(self.created_at.timestamp()),
            nbf=int(self.created_at.timestamp()),
            exp=int(self.expires_at.timestamp()),
            jti=jti,
            grant_id=grant_id,
            scope=scope,
        )
