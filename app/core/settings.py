from pydantic import AnyHttpUrl, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from app.modules.shared.application.enums import ApplicationEnvironment


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
    APPLICATION_ENVIRONMENT: str
    APPLICATION_PORT: int
    APPLICATION_CONNECT_TIMEOUT_SECONDS: int
    APPLICATION_URL: AnyHttpUrl
    APPLICATION_TABLE_PREFIX: str

    # AUTH
    AUTH_BEARER_TOKEN_SCHEME_NAME: str
    AUTH_BEARER_TOKEN_SCHEME_DESCRIPTION: str
    AUTH_API_KEY_SCHEME_NAME: str
    AUTH_API_KEY_SCHEME_DESCRIPTION: str
    AUTH_API_KEY_HEADER: str
    AUTH_API_KEY_HEADER_DESCRIPTION: str

    # COOKIES
    COOKIES_MAX_AGE_SECONDS: int
    COOKIES_TOKEN_TYPE_KEY: str
    COOKIES_ACCESS_TOKEN_KEY: str
    COOKIES_ACCESS_TOKEN_PATH: str
    COOKIES_REFRESH_TOKEN_KEY: str
    COOKIES_REFRESH_TOKEN_PATH: str
    COOKIES_DEVICE_KEY: str
    COOKIES_DOMAIN: str

    # JWT
    JWT_ISSUER: str
    JWT_AUDIENCE: str
    JWT_SIGNING_KEY_PASSWORD: str
    JWT_ENCRYPTION_KEY_PASSWORD: str
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
    LOGS_PYGMENTS_STYLE: str = "monokai"

    # POSTGRESQL
    POSTGRESQL_DATABASE: str
    POSTGRESQL_USERNAME: str
    POSTGRESQL_PASSWORD: str
    POSTGRESQL_HOST: str
    POSTGRESQL_PORT: str

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

    # APPLICATION
    @computed_field
    @property
    def APPLICATION_ENVIRONMENT_DEBUG(self) -> bool:  # noqa
        if self.APPLICATION_ENVIRONMENT == ApplicationEnvironment.PRODUCTION.value:
            return False
        else:
            return True

    # COOKIES
    @computed_field
    @property
    def COOKIES_ACCESS_TOKEN_MAX_AGE(self) -> int:  # noqa
        return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @computed_field
    @property
    def COOKIES_REFRESH_TOKEN_MAX_AGE(self) -> int:  # noqa
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # POSTGRESQL
    @computed_field
    @property
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
    @property
    def POSTGRESQL_DATABASE_URL(self) -> URL:  # noqa
        return URL.create(
            drivername="postgresql+psycopg2",
            username=self.POSTGRESQL_USERNAME,
            password=self.POSTGRESQL_PASSWORD,
            host=self.POSTGRESQL_HOST,
            port=int(self.POSTGRESQL_PORT),
            database=self.POSTGRESQL_DATABASE,
        )

    # SECURITY
    @computed_field
    @property
    def SECURITY_NO_AUTH_PATHS(self) -> list[dict[str, str]]:  # noqa
        return [
            # AUTHENTICATION
            {"endpoint": "/api/v1/authentication/login/", "method": "POST"},
            {"endpoint": "/api/v1/authentication/login", "method": "POST"},
            {"endpoint": "/api/v1/authentication/logout/", "method": "DELETE"},
            {"endpoint": "/api/v1/authentication/logout", "method": "DELETE"},
            # EXAMPLE
            {"endpoint": "/api/v1/example/", "method": "POST"},
            {"endpoint": "/api/v1/example", "method": "POST"},
            # HEALTH
            {"endpoint": "/health/", "method": "GET"},
            {"endpoint": "/health", "method": "GET"},
            # USER
            {"endpoint": "/api/v1/user/", "method": "POST"},
            {"endpoint": "/api/v1/user", "method": "POST"},
        ]

    @computed_field
    @property
    def SECURITY_USER_ALLOWED_PATHS(self) -> list[dict[str, str]]:  # noqa
        return [
            *self.SECURITY_NO_AUTH_PATHS,
            # AUTHENTICATION
            {"endpoint": "/api/v1/authentication/refresh/", "method": "PATCH"},
            {"endpoint": "/api/v1/authentication/refresh", "method": "PATCH"},
            # USER
            {"endpoint": "/api/v1/user/me", "method": "GET"},
            {"endpoint": "/api/v1/user/me/", "method": "GET"},
        ]

    @computed_field
    @property
    def SECURITY_MANAGER_ALLOWED_PATHS(self) -> list[dict[str, str]]:  # noqa
        return [
            *self.SECURITY_USER_ALLOWED_PATHS,
        ]

    @computed_field
    @property
    def SECURITY_ADMIN_ALLOWED_PATHS(self) -> list[dict[str, str]]:  # noqa
        return [
            *self.SECURITY_MANAGER_ALLOWED_PATHS,
            # HEALTH
            {"endpoint": "/api/v1/alembic-version/", "method": "GET"},
            {"endpoint": "/api/v1/alembic-version", "method": "GET"},
        ]

    @computed_field
    @property
    def SECURITY_API_KEY_ALLOWED_PATHS(self) -> list[dict[str, str]]:  # noqa
        return []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

        if self.APPLICATION_ENVIRONMENT not in [
            env.value for env in ApplicationEnvironment
        ]:
            raise ValueError(
                f"Invalid execution environment: {self.APPLICATION_ENVIRONMENT}."
                f"The environment must be {', '.join([env.value for env in ApplicationEnvironment])} (case-sensitive). "
                f"Please check your .env file."
            )


settings = Settings()
