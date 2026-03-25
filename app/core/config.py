import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeneralConfig(BaseModel):
    # Environment
    ENV_STATE: str = Field(default="dev")
    API_URL: str = Field(default="http://localhost:8000")
    API_KEY: str | None = None

    # Database Settings
    POSTGRES_NAME: str | None = Field(default=None)
    POSTGRES_USER: str | None = Field(default=None)
    POSTGRES_PASSWORD: str | None = Field(default=None)
    POSTGRES_DATA_PATH: str | None = Field(default=None)
    DATABASE_URL: str | None = Field(default=None)
    

    # DigitalOcean Spaces (S3)
    DO_SPACES_ENDPOINT: str | None = None
    DO_SPACES_REGION: str | None = None
    DO_SPACES_KEY: str | None = None
    DO_SPACES_SECRET: str | None = None
    DO_SPACES_BUCKET: str | None = None
    DO_SPACES_CDN_URL: str | None = None

    # API Keys
    OPENEXCHANGERATES_API_KEY: str | None = None
    COINMARKETCAP_API_KEY: str | None = None
    OPENEXCHANGERATES_CRON_KEY: str | None = None

    # Notifications
    SLACK_WEBHOOK_URL: str | None = None

    WRITE_FILE_ON_S3: int = Field(default=60)
    FETCH_API_DATA: int = Field(default=60)

    # Interval for Jobs in minutes

    def __init__(self, **kwargs):
        # Load from environment variables
        env_values = {}
        for field_name in self.__fields__.keys():
            env_value = os.getenv(field_name)
            env_values[field_name] = env_value
                    
        # Merge with any passed kwargs
        env_values.update(kwargs)
        super().__init__(**env_values)


# Singleton instance
env_var = GeneralConfig()