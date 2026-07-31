from functools import cached_property
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from jwcrypto import jwk
from pydantic import AnyHttpUrl, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from app.modules.shared.domain.enums import ApplicationEnvironment, CookieSameSite


PathRule = Mapping[str, str]


def _path_rule(endpoint: str, method: str) -> PathRule:
    return MappingProxyType({"endpoint": endpoint, "method": method})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
        env_ignore_empty=True,
    )

    # APPLICATION
    APPLICATION_TITLE: str
    APPLICATION_SUMMARY: str
    APPLICATION_DESCRIPTION: str
    APPLICATION_VERSION: str
    APPLICATION_CONTACT_NAME: str
    APPLICATION_CONTACT_URL: str
    APPLICATION_CONTACT_EMAIL: str
    APPLICATION_CONTACT_PHONE: str
    APPLICATION_ENVIRONMENT: ApplicationEnvironment
    APPLICATION_PORT: int
    APPLICATION_CONNECT_TIMEOUT_SECONDS: int
    APPLICATION_URL: AnyHttpUrl
    APPLICATION_TABLE_PREFIX: str

    # API KEY
    API_KEY_PREFIX: str
    API_KEY_HASH_FINGERPRINT: str
    API_KEY_ENTROPY_BYTES: int

    # AUTH
    AUTH_BEARER_TOKEN_SCHEME_NAME: str
    AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION: str
    AUTH_API_KEY_NAME: str
    AUTH_API_KEY_SCHEME_NAME: str
    AUTH_API_KEY_DESCRIPTION: str

    # COOKIES
    COOKIES_MAX_AGE_SECONDS: int
    COOKIES_TOKEN_TYPE_KEY: str
    COOKIES_ACCESS_TOKEN_KEY: str
    COOKIES_ACCESS_TOKEN_PATH: str
    COOKIES_REFRESH_TOKEN_KEY: str
    COOKIES_REFRESH_TOKEN_PATH: str
    COOKIES_DEVICE_KEY: str
    COOKIES_DOMAIN: str
    COOKIES_SAME_SITE: CookieSameSite

    # JWT
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_SIGNING_KEY_PASSWORD: str
    JWT_ENCRYPTION_KEY_PASSWORD: str
    JWT_AUTO_GENERATE_KEYS: bool
    JWT_KEYS_DIR: str
    JWT_SIGNING_PRIVATE_KEY_PATH: str
    JWT_SIGNING_PUBLIC_KEY_PATH: str
    JWT_ENCRYPTION_PRIVATE_KEY_PATH: str
    JWT_ENCRYPTION_PUBLIC_KEY_PATH: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_HASH_FINGERPRINT: str

    # LOGS
    LOGS_NAME: str
    LOGS_PATH: str
    LOGS_LEVEL: str
    LOGS_REQUEST_ID_LENGTH: int
    LOGS_PYGMENTS_STYLE: str

    # NGROK
    NGROK_AUTH_TOKEN: str = ""

    # POSTGRESQL
    POSTGRESQL_DATABASE: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: str

    # REDIS
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int
    REDIS_USERNAME: str
    REDIS_SSL: bool
    REDIS_CONNECTION_TIMEOUT_SECONDS: int
    REDIS_SOCKET_TIMEOUT_SECONDS: int
    REDIS_DEFAULT_TTL_SECONDS: int
    REDIS_SESSION_TTL_SECONDS: int
    REDIS_TOMBSTONE_TTL_SECONDS: int
    REDIS_KEY_PREFIX: str
    REDIS_CACHE_VERSION: int
    REDIS_FLUSH_ON_STARTUP: bool
    REDIS_MAX_CONNECTIONS: int

    # SECURITY SETTINGS
    SECURITY_ALLOW_ORIGINS: list[str]
    SECURITY_ALLOW_HEADERS: list[str]
    SECURITY_ALLOW_METHODS: list[str]
    SECURITY_EMAIL_ALLOWED_DOMAINS: list[str]
    SECURITY_ADMIN_EMAIL: str
    SECURITY_ADMIN_PASSWORD: str

    # GENERAL
    @field_validator("*", mode="before")
    @classmethod
    def strip_quotes(cls, v):
        if isinstance(v, str) and len(v) >= 2:
            if (v.startswith('"') and v.endswith('"')) or (
                v.startswith("'") and v.endswith("'")
            ):
                return v[1:-1]
        return v

    @field_validator("COOKIES_SAME_SITE", mode="before")
    @classmethod
    def validate_cookies_same_site(cls, v):
        if isinstance(v, CookieSameSite):
            return v

        if isinstance(v, str):
            value = v.strip().strip('"').strip("'").lower()
            try:
                return CookieSameSite(value)
            except ValueError:
                pass

        raise ValueError(
            "Invalid COOKIES_SAME_SITE. Allowed values: 'lax', 'strict', 'none'."
        )

    @field_validator("APPLICATION_ENVIRONMENT", mode="before")
    @classmethod
    def validate_application_environment(cls, v):
        if isinstance(v, ApplicationEnvironment):
            return v

        if isinstance(v, str):
            value = v.strip().strip('"').strip("'").lower()
            try:
                return ApplicationEnvironment(value)
            except ValueError:
                pass

        raise ValueError(
            "Invalid APPLICATION_ENVIRONMENT. Allowed values: "
            "'dev', 'homolog', 'production'."
        )

    # APPLICATION
    @computed_field
    @cached_property
    def APPLICATION_ENVIRONMENT_DEBUG(self) -> bool:  # noqa
        if self.APPLICATION_ENVIRONMENT == ApplicationEnvironment.PRODUCTION.value:
            return False
        else:
            return True

    # COOKIES
    @computed_field
    @cached_property
    def COOKIES_ACCESS_TOKEN_MAX_AGE(self) -> int:  # noqa
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @computed_field
    @cached_property
    def COOKIES_REFRESH_TOKEN_MAX_AGE(self) -> int:  # noqa
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # JWT
    @computed_field
    @cached_property
    def JWT_SIGNING_PRIVATE_KEY(self) -> jwk.JWK:  # noqa
        with open(self.JWT_SIGNING_PRIVATE_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(
            pem_data,
            password=self.JWT_SIGNING_KEY_PASSWORD.encode("utf-8"),
        )

    @computed_field
    @cached_property
    def JWT_SIGNING_PUBLIC_KEY(self) -> jwk.JWK:  # noqa
        with open(self.JWT_SIGNING_PUBLIC_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(pem_data)

    @computed_field
    @cached_property
    def JWT_ENCRYPTION_PRIVATE_KEY(self) -> jwk.JWK:  # noqa
        with open(self.JWT_ENCRYPTION_PRIVATE_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(
            pem_data,
            password=self.JWT_ENCRYPTION_KEY_PASSWORD.encode("utf-8"),
        )

    @computed_field
    @cached_property
    def JWT_ENCRYPTION_PUBLIC_KEY(self) -> jwk.JWK:  # noqa
        with open(self.JWT_ENCRYPTION_PUBLIC_KEY_PATH, "rb") as key_file:
            pem_data = key_file.read()

        return jwk.JWK.from_pem(pem_data)

    # POSTGRESQL
    @computed_field
    @cached_property
    def POSTGRESQL_ASYNC_DATABASE_URL(self) -> URL:  # noqa
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOST,
            port=int(self.POSTGRESQL_PORT),
            database=self.POSTGRESQL_DATABASE,
        )

    @computed_field
    @cached_property
    def POSTGRESQL_DATABASE_URL(self) -> URL:  # noqa
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOST,
            port=int(self.POSTGRESQL_PORT),
            database=self.POSTGRESQL_DATABASE,
        )

    # REDIS
    @computed_field
    @cached_property
    def REDIS_URL(self) -> str:  # noqa

        scheme = "rediss" if self.REDIS_SSL else "redis"
        return (
            f"{scheme}://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}"
            f"@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )

    @computed_field
    @cached_property
    def REDIS_NAMESPACE(self) -> str:  # noqa
        # Every cache key hangs off this namespace. Bumping REDIS_CACHE_VERSION
        # makes the previous generation unreachable, so entries written in an old
        # payload format are never read back: they simply expire by ttl. This is
        # what a format change should use instead of flushing the cache.
        return f"{self.REDIS_KEY_PREFIX}:v{self.REDIS_CACHE_VERSION}"

    # SECURITY
    @computed_field
    @cached_property
    def SECURITY_NO_AUTH_PATHS(self) -> tuple[PathRule, ...]:  # noqa
        return (
            # AUTHENTICATION
            _path_rule("/api/v1/authentication/login/", "POST"),
            _path_rule("/api/v1/authentication/login", "POST"),
            _path_rule("/api/v1/authentication/logout/", "DELETE"),
            _path_rule("/api/v1/authentication/logout", "DELETE"),
            # EXAMPLE
            _path_rule("/api/v1/example/", "POST"),
            _path_rule("/api/v1/example", "POST"),
            # HEALTH
            _path_rule("/health/", "GET"),
            _path_rule("/health", "GET"),
            # USER
            _path_rule("/api/v1/user/", "POST"),
            _path_rule("/api/v1/user", "POST"),
            # WEBSOCKET
            _path_rule("/api/v1/websocket/connect/", "GET"),
            _path_rule("/api/v1/websocket/connect", "GET"),
        )

    @computed_field
    @cached_property
    def SECURITY_USER_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:  # noqa
        return (
            *self.SECURITY_NO_AUTH_PATHS,
            # AUTHENTICATION
            _path_rule("/api/v1/authentication/refresh/", "PATCH"),
            _path_rule("/api/v1/authentication/refresh", "PATCH"),
            # USER
            _path_rule("/api/v1/user/me", "GET"),
            _path_rule("/api/v1/user/me/", "GET"),
            # NOTIFICATION
            _path_rule("/api/v1/notification/", "GET"),
            _path_rule("/api/v1/notification", "GET"),
            _path_rule("/api/v1/notification/{id}/", "PATCH"),
            _path_rule("/api/v1/notification/{id}", "PATCH"),
        )

    @computed_field
    @cached_property
    def SECURITY_MANAGER_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:  # noqa
        return (
            *self.SECURITY_USER_ALLOWED_PATHS,
            # KNOWLEDGE
            _path_rule("/api/v1/knowledge/", "POST"),
            _path_rule("/api/v1/knowledge", "POST"),
            _path_rule("/api/v1/knowledge/{id}/", "PATCH"),
            _path_rule("/api/v1/knowledge/{id}", "PATCH"),
            _path_rule("/api/v1/knowledge/{id}/", "DELETE"),
            _path_rule("/api/v1/knowledge/{id}", "DELETE"),
            _path_rule("/api/v1/knowledge/", "GET"),
            _path_rule("/api/v1/knowledge", "GET"),
        )

    @computed_field
    @cached_property
    def SECURITY_ADMIN_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:  # noqa
        return (
            *self.SECURITY_MANAGER_ALLOWED_PATHS,
            # HEALTH
            _path_rule("/api/v1/alembic-version/", "GET"),
            _path_rule("/api/v1/alembic-version", "GET"),
            # KEY
            _path_rule("/api/v1/key/", "POST"),
            _path_rule("/api/v1/key", "POST"),
            _path_rule("/api/v1/key/", "GET"),
            _path_rule("/api/v1/key", "GET"),
            _path_rule("/api/v1/key/{id}/", "GET"),
            _path_rule("/api/v1/key/{id}", "GET"),
            _path_rule("/api/v1/key/{id}/", "PATCH"),
            _path_rule("/api/v1/key/{id}", "PATCH"),
            _path_rule("/api/v1/key/{id}/rotate/", "PATCH"),
            _path_rule("/api/v1/key/{id}/rotate", "PATCH"),
            _path_rule("/api/v1/key/{id}/", "DELETE"),
            _path_rule("/api/v1/key/{id}", "DELETE"),
        )

    @computed_field
    @cached_property
    def SECURITY_API_KEY_ALLOWED_PATHS(self) -> tuple[PathRule, ...]:  # noqa
        return ()

    def generate_authentication_keys(self) -> None:
        if not self.JWT_AUTO_GENERATE_KEYS:
            return

        keys_dir = Path(self.JWT_KEYS_DIR)
        keys_dir.mkdir(parents=True, exist_ok=True)

        signing_private = Path(self.JWT_SIGNING_PRIVATE_KEY_PATH)
        signing_public = Path(self.JWT_SIGNING_PUBLIC_KEY_PATH)
        encryption_private = Path(self.JWT_ENCRYPTION_PRIVATE_KEY_PATH)
        encryption_public = Path(self.JWT_ENCRYPTION_PUBLIC_KEY_PATH)

        if not signing_private.exists() or not signing_public.exists():
            _key = Ed25519PrivateKey.generate()
            signing_private.write_bytes(
                _key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(
                        self.JWT_SIGNING_KEY_PASSWORD.encode()
                    ),
                )
            )
            signing_public.write_bytes(
                _key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        if not encryption_private.exists() or not encryption_public.exists():
            _key = X25519PrivateKey.generate()
            encryption_private.write_bytes(
                _key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(
                        self.JWT_ENCRYPTION_KEY_PASSWORD.encode()
                    ),
                )
            )
            encryption_public.write_bytes(
                _key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.generate_authentication_keys()

        if ":" in self.POSTGRESQL_HOST:
            host_parts = self.POSTGRESQL_HOST.split(":")
            self.POSTGRESQL_HOST = host_parts[0]
            if len(host_parts) > 1 and not self.POSTGRESQL_PORT:
                self.POSTGRESQL_PORT = host_parts[1]

        for field_name, field_info in self.model_fields.items():
            value = getattr(self, field_name)
            if isinstance(value, str) and len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    setattr(self, field_name, value[1:-1])


settings = Settings()
