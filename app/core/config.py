from pydantic_settings import BaseSettings
from pydantic import Field


class GeneralConfig(BaseSettings):
    # Environment
    ENV_STATE: str = Field(default="dev")
    API_URL: str = Field(default="http://localhost:8000")
    API_KEY: str | None = None

    # Database
    POSTGRES_HOST: str
    POSTGRES_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str
    POSTGRES_DATA_PATH: str | None = None

    # DigitalOcean Spaces (S3)
    DO_SPACES_ENDPOINT: str
    DO_SPACES_REGION: str
    DO_SPACES_KEY: str
    DO_SPACES_SECRET: str
    DO_SPACES_BUCKET: str
    DO_SPACES_CDN_URL: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance
env_var = GeneralConfig()
