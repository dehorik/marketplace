import os
from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../.env")


class Settings(BaseSettings):
    # postgresql config
    DATABASE_NAME: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_USER_PASSWORD: str

    # redis config
    REDIS_HOST: str
    REDIS_PORT: int

    # path to images from database
    USER_CONTENT_PATH: str
    PRODUCT_CONTENT_PATH: str
    COMMENT_CONTENT_PATH: str

    # auth
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=DOTENV_FILE_PATH)


config = Settings()
