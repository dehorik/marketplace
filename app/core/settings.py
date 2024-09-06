import os
from pydantic_settings import BaseSettings, SettingsConfigDict


DOTENV = os.path.join(os.path.dirname(__file__), "../../.env")


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

    # path to database photos
    USER_PHOTO_PATH: str
    PRODUCT_PHOTO_PATH: str
    COMMENT_PHOTO_PATH: str

    # auth
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=DOTENV)


config = Settings()
