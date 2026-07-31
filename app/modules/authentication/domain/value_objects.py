from uuid import UUID

from app.modules.shared.domain.entities import DomainError


class BaseClaims:
    iss: str
    sub: UUID
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: UUID

    def __setattr__(self, name: str, value) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable.")

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
    ) -> None:
        object.__setattr__(self, "iss", iss.strip() if iss else iss)
        object.__setattr__(self, "sub", sub)
        object.__setattr__(self, "aud", aud.strip() if aud else aud)
        object.__setattr__(self, "iat", iat)
        object.__setattr__(self, "nbf", nbf)
        object.__setattr__(self, "exp", exp)
        object.__setattr__(self, "jti", jti)

    def _validate_base(self, prefix: str = "Claims") -> None:
        if not self.iss:
            raise DomainError(f"{prefix} issuer (iss) is required.")

        if not self.sub:
            raise DomainError(f"{prefix} subject (sub) is required.")

        if not self.aud:
            raise DomainError(f"{prefix} audience (aud) is required.")

        if self.iat is None:
            raise DomainError(f"{prefix} issued at (iat) is required.")
        if not isinstance(self.iat, int) or self.iat <= 0:
            raise DomainError(
                f"{prefix} issued at (iat) must be a positive integer Unix timestamp."
            )

        if self.nbf is None:
            raise DomainError(f"{prefix} not before (nbf) is required.")
        if not isinstance(self.nbf, int) or self.nbf <= 0:
            raise DomainError(
                f"{prefix} not before (nbf) must be a positive integer Unix timestamp."
            )
        if self.nbf < self.iat:
            raise DomainError(
                f"{prefix} not before (nbf) cannot be earlier than issued at (iat)."
            )

        if self.exp is None:
            raise DomainError(f"{prefix} expiration (exp) is required.")
        if not isinstance(self.exp, int) or self.exp <= 0:
            raise DomainError(
                f"{prefix} expiration (exp) must be a positive integer Unix timestamp."
            )
        if self.exp <= self.iat:
            raise DomainError(
                f"{prefix} expiration (exp) must be after issued at (iat)."
            )

        if not self.jti:
            raise DomainError(f"{prefix} JWT ID (jti) is required.")

    def _base_to_dict(self) -> dict:
        return {
            "iss": self.iss,
            "sub": str(self.sub),
            "aud": self.aud,
            "iat": self.iat,
            "nbf": self.nbf,
            "exp": self.exp,
            "jti": str(self.jti),
        }

    @staticmethod
    def _base_kwargs_from_dict(data: dict) -> dict:
        return {
            "iss": data["iss"],
            "sub": UUID(data["sub"]) if isinstance(data["sub"], str) else data["sub"],
            "aud": data["aud"],
            "iat": data["iat"],
            "nbf": data["nbf"],
            "exp": data["exp"],
            "jti": UUID(data["jti"]) if isinstance(data["jti"], str) else data["jti"],
        }


class Claims(BaseClaims):
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
        grant_id: str | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(iss=iss, sub=sub, aud=aud, iat=iat, nbf=nbf, exp=exp, jti=jti)
        object.__setattr__(self, "grant_id", grant_id)
        object.__setattr__(self, "scope", scope.strip().lower() if scope else scope)
        self._validate()

    def _validate(self) -> None:
        self._validate_base()
        if not self.grant_id:
            raise DomainError("Claims grant_id is required.")
        if not self.scope:
            raise DomainError("Claims scope is required.")

    def to_dict(self) -> dict:
        return {
            **self._base_to_dict(),
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Claims:
        return cls(
            **cls._base_kwargs_from_dict(data),
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return f"Claims(iss={self.iss}, sub={self.sub}, jti={self.jti}, grant_id={self.grant_id}, scope={self.scope})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Claims):
            return False
        return (
            self.iss == other.iss
            and self.sub == other.sub
            and self.aud == other.aud
            and self.jti == other.jti
            and self.grant_id == other.grant_id
            and self.scope == other.scope
        )

    def __hash__(self) -> int:
        return hash((self.iss, self.sub, self.aud, self.jti, self.grant_id, self.scope))


class RefreshClaims(BaseClaims):
    client_id: str
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | None = None,
        sub: UUID | None = None,
        aud: str | None = None,
        iat: int | None = None,
        nbf: int | None = None,
        exp: int | None = None,
        jti: UUID | None = None,
        client_id: str | None = None,
        grant_id: str | None = None,
        scope: str | None = None,
    ) -> None:
        super().__init__(iss=iss, sub=sub, aud=aud, iat=iat, nbf=nbf, exp=exp, jti=jti)
        object.__setattr__(
            self, "client_id", client_id.strip().lower() if client_id else client_id
        )
        object.__setattr__(self, "grant_id", grant_id.strip() if grant_id else grant_id)
        object.__setattr__(
            self, "scope", " ".join(scope.lower().split()) if scope else scope
        )
        self._validate()

    def _validate(self) -> None:
        self._validate_base("Refresh claims")
        if not self.client_id:
            raise DomainError("Refresh claims client_id is required.")
        if not self.grant_id:
            raise DomainError("Refresh claims grant_id is required.")
        if not self.scope:
            raise DomainError("Refresh claims scope is required.")

    def to_dict(self) -> dict:
        return {
            **self._base_to_dict(),
            "client_id": self.client_id,
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> RefreshClaims:
        return cls(
            **cls._base_kwargs_from_dict(data),
            client_id=data["client_id"],
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return (
            f"RefreshClaims(iss={self.iss}, sub={self.sub}, "
            f"jti={self.jti}, client_id={self.client_id}, scope={self.scope})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, RefreshClaims):
            return False
        return (
            self.iss == other.iss
            and self.sub == other.sub
            and self.aud == other.aud
            and self.jti == other.jti
            and self.client_id == other.client_id
            and self.grant_id == other.grant_id
            and self.scope == other.scope
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.iss,
                self.sub,
                self.aud,
                self.jti,
                self.client_id,
                self.grant_id,
                self.scope,
            )
        )
