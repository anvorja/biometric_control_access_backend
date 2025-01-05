from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Biometric Access Control"
    API_V1_STR: str = "/api/v1"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    ZKTECO_IP: str
    ZKTECO_PORT: int

    FINGERPRINT_ENCRYPTION_KEY: str

    model_config = SettingsConfigDict(env_file='.env')


@lru_cache()
def get_settings():
    return Settings()
