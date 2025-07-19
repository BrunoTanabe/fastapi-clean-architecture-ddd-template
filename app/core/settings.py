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

    # ENVIRONMENT
    ENVIRONMENT: str
    ENVIRONMENT_DEBUG: bool = False

    # SECURITY
    SECURITY_API_KEY_HEADER: str
    SECURITY_API_KEY_HEADER_DESCRIPTION: str
    SECURITY_SCHEME_NAME: str
    SECURITY_DEFAULT_API_KEY: str
    SECURITY_DEFAULT_API_KEY_NAME: str
    SECURITY_DEFAULT_API_KEY_DESCRIPTION: str

    # LOGS
    LOGS_NAME: str
    LOGS_PATH: str
    LOGS_LEVEL: str
    LOGS_REQUEST_ID_LENGTH: int
    LOGS_PYGMENTS_STYLE: str = "monokai"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ENVIRONMENT not in ["DEV", "HOMOLOG", "MAIN"]:
            raise ValueError(
                f"Invalid execution environment: {self.ENVIRONMENT}. The environment must be DEV, HOMOLOG, or MAIN (case-sensitive)."
                f"Please check your .env file."
            )

        if self.ENVIRONMENT == "DEV":
            self.ENVIRONMENT_DEBUG = True
        else:
            self.ENVIRONMENT_DEBUG = False


settings = Settings()
