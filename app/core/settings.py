from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    APPLICATION_ENVIRONMENT_DEBUG: bool = False
    APPLICATION_CONNECT_TIMEOUT_SECONDS: int = 30
    APPLICATION_URL: AnyHttpUrl

    # SECURITY
    SECURITY_BACKEND_ALLOW_ORIGINS: list[str | AnyHttpUrl]
    SECURITY_BACKEND_ALLOW_HEADERS: list[str] = []
    SECURITY_BACKEND_ALLOW_METHODS: list[str] = []
    SECURITY_BACKEND_SCHEME_NAME: str
    SECURITY_BACKEND_SCHEME_DESCRIPTION: str
    SECURITY_BACKEND_HTTPS_ONLY: bool = True
    SECURITY_API_KEY_HEADER: str
    SECURITY_API_KEY_HEADER_DESCRIPTION: str
    SECURITY_DEFAULT_API_KEY: str
    SECURITY_DEFAULT_API_KEY_NAME: str
    SECURITY_DEFAULT_API_KEY_DESCRIPTION: str

    # LOGS
    LOGS_NAME: str
    LOGS_PATH: str
    LOGS_LEVEL: str
    LOGS_REQUEST_ID_LENGTH: int
    LOGS_PYGMENTS_STYLE: str = "monokai"

    @computed_field
    @property
    def SECURITY_BACKEND_USER_ALLOWED_PATHS(self) -> list[dict[str, str]]:
        return [
            {"endpoint": "/api/v2/example", "method": "POST"},
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for field_name, field_info in self.model_fields.items():
            value = getattr(self, field_name)
            if isinstance(value, str) and len(value) >= 2:
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    setattr(self, field_name, value[1:-1])

        if self.APPLICATION_ENVIRONMENT not in ["DEV", "HOMOLOG", "MAIN"]:
            raise ValueError(
                f"Invalid execution environment: {self.APPLICATION_ENVIRONMENT}. The environment must be DEV, HOMOLOG, or MAIN (case-sensitive)."
                f"Please check your .env file."
            )

        if self.APPLICATION_ENVIRONMENT == "DEV":
            self.APPLICATION_ENVIRONMENT_DEBUG = True
            self.SECURITY_BACKEND_HTTPS_ONLY = False
        else:
            self.APPLICATION_ENVIRONMENT_DEBUG = False
            self.SECURITY_BACKEND_HTTPS_ONLY = True


settings = Settings()
