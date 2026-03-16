from uuid import UUID

from app.modules.shared.domain.entities import DomainError


class Claims:
    iss: str
    sub: UUID
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: UUID
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | dict = None,
        sub: UUID = None,
        aud: str = None,
        iat: int = None,
        nbf: int = None,
        exp: int = None,
        jti: UUID = None,
        grant_id: str = None,
        scope: str = None,
    ) -> None:
        if isinstance(iss, dict):
            data = iss
            iss = data["iss"]
            sub = UUID(data["sub"]) if isinstance(data["sub"], str) else data["sub"]
            aud = data["aud"]
            iat = data["iat"]
            nbf = data["nbf"]
            exp = data["exp"]
            jti = UUID(data["jti"]) if isinstance(data["jti"], str) else data["jti"]
            grant_id = data["grant_id"]
            scope = data["scope"]

        self.iss = iss
        self.sub = sub
        self.aud = aud
        self.iat = iat
        self.nbf = nbf
        self.exp = exp
        self.jti = jti
        self.grant_id = grant_id
        self.scope = scope
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.iss = self.iss.strip() if self.iss else self.iss
        self.aud = self.aud.strip() if self.aud else self.aud
        self.scope = self.scope.strip().lower() if self.scope else self.scope

    def _validate(self) -> None:
        if not self.iss:
            raise DomainError("Claims issuer (iss) is required.")

        if not self.sub:
            raise DomainError("Claims subject (sub) is required.")

        if not self.aud:
            raise DomainError("Claims audience (aud) is required.")

        if self.iat is None:
            raise DomainError("Claims issued at (iat) is required.")
        if not isinstance(self.iat, int) or self.iat <= 0:
            raise DomainError(
                "Claims issued at (iat) must be a positive integer Unix timestamp."
            )

        if self.nbf is None:
            raise DomainError("Claims not before (nbf) is required.")
        if not isinstance(self.nbf, int) or self.nbf <= 0:
            raise DomainError(
                "Claims not before (nbf) must be a positive integer Unix timestamp."
            )
        if self.nbf < self.iat:
            raise DomainError(
                "Claims not before (nbf) cannot be earlier than issued at (iat)."
            )

        if self.exp is None:
            raise DomainError("Claims expiration (exp) is required.")
        if not isinstance(self.exp, int) or self.exp <= 0:
            raise DomainError(
                "Claims expiration (exp) must be a positive integer Unix timestamp."
            )
        if self.exp <= self.iat:
            raise DomainError("Claims expiration (exp) must be after issued at (iat).")

        if not self.jti:
            raise DomainError("Claims JWT ID (jti) is required.")

        if not self.grant_id:
            raise DomainError("Claims grant_id is required.")

        if not self.scope:
            raise DomainError("Claims scope is required.")

    def to_dict(self) -> dict:
        return {
            "iss": self.iss,
            "sub": str(self.sub),
            "aud": self.aud,
            "iat": self.iat,
            "nbf": self.nbf,
            "exp": self.exp,
            "jti": str(self.jti),
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Claims":
        return cls(
            iss=data["iss"],
            sub=UUID(data["sub"]),
            aud=data["aud"],
            iat=data["iat"],
            nbf=data["nbf"],
            exp=data["exp"],
            jti=UUID(data["jti"]),
            grant_id=data["grant_id"],
            scope=data["scope"],
        )

    def __str__(self) -> str:
        return f"Claims(iss={self.iss}, sub={self.sub}, jti={self.jti}, grant_id={self.grant_id}, scope={self.scope})"

    def __eq__(self, other) -> bool:
        return str(self) == str(other)


class RefreshClaims:
    iss: str
    sub: UUID
    aud: str
    iat: int
    nbf: int
    exp: int
    jti: UUID
    client_id: str
    grant_id: str
    scope: str

    def __init__(
        self,
        iss: str | dict = None,
        sub: UUID = None,
        aud: str = None,
        iat: int = None,
        nbf: int = None,
        exp: int = None,
        jti: UUID = None,
        client_id: str = None,
        grant_id: str = None,
        scope: str = None,
    ) -> None:
        if isinstance(iss, dict):
            data = iss
            iss = data["iss"]
            sub = UUID(data["sub"]) if isinstance(data["sub"], str) else data["sub"]
            aud = data["aud"]
            iat = data["iat"]
            nbf = data["nbf"]
            exp = data["exp"]
            jti = UUID(data["jti"]) if isinstance(data["jti"], str) else data["jti"]
            client_id = data["client_id"]
            grant_id = data["grant_id"]
            scope = data["scope"]

        self.iss = iss
        self.sub = sub
        self.aud = aud
        self.iat = iat
        self.nbf = nbf
        self.exp = exp
        self.jti = jti
        self.client_id = client_id
        self.grant_id = grant_id
        self.scope = scope
        self._normalize()
        self._validate()

    def _normalize(self) -> None:
        self.iss = self.iss.strip() if self.iss else self.iss
        self.aud = self.aud.strip() if self.aud else self.aud
        self.client_id = (
            self.client_id.strip().lower() if self.client_id else self.client_id
        )
        self.grant_id = self.grant_id.strip() if self.grant_id else self.grant_id
        if self.scope:
            self.scope = " ".join(self.scope.lower().split())

    def _validate(self) -> None:
        if not self.iss:
            raise DomainError("Refresh claims issuer (iss) is required.")

        if not self.sub:
            raise DomainError("Refresh claims subject (sub) is required.")

        if not self.aud:
            raise DomainError("Refresh claims audience (aud) is required.")

        if self.iat is None:
            raise DomainError("Refresh claims issued at (iat) is required.")
        if not isinstance(self.iat, int) or self.iat <= 0:
            raise DomainError(
                "Refresh claims issued at (iat) must be a positive integer Unix timestamp."
            )

        if self.nbf is None:
            raise DomainError("Refresh claims not before (nbf) is required.")
        if not isinstance(self.nbf, int) or self.nbf <= 0:
            raise DomainError(
                "Refresh claims not before (nbf) must be a positive integer Unix timestamp."
            )
        if self.nbf < self.iat:
            raise DomainError(
                "Refresh claims not before (nbf) cannot be earlier than issued at (iat)."
            )

        if self.exp is None:
            raise DomainError("Refresh claims expiration (exp) is required.")
        if not isinstance(self.exp, int) or self.exp <= 0:
            raise DomainError(
                "Refresh claims expiration (exp) must be a positive integer Unix timestamp."
            )
        if self.exp <= self.iat:
            raise DomainError(
                "Refresh claims expiration (exp) must be after issued at (iat)."
            )

        if not self.jti:
            raise DomainError("Refresh claims JWT ID (jti) is required.")

        if not self.client_id:
            raise DomainError("Refresh claims client_id is required.")

        if not self.grant_id:
            raise DomainError("Refresh claims grant_id is required.")

        if not self.scope:
            raise DomainError("Refresh claims scope is required.")

    def to_dict(self) -> dict:
        return {
            "iss": self.iss,
            "sub": str(self.sub),
            "aud": self.aud,
            "iat": self.iat,
            "nbf": self.nbf,
            "exp": self.exp,
            "jti": str(self.jti),
            "client_id": self.client_id,
            "grant_id": self.grant_id,
            "scope": self.scope,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RefreshClaims":
        return cls(
            iss=data["iss"],
            sub=UUID(data["sub"]),
            aud=data["aud"],
            iat=data["iat"],
            nbf=data["nbf"],
            exp=data["exp"],
            jti=UUID(data["jti"]),
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
        return str(self) == str(other)
