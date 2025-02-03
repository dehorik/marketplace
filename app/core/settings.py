from os.path import join
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_PATH = str(Path(__file__).resolve().parent.parent.parent)
DOTENV_FILE_PATH = join(ROOT_PATH, ".env")


class Settings(BaseSettings):
    # postgresql config
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_USER_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_PORT: int

    # redis config
    REDIS_HOST: str
    REDIS_PORT: int

    # auth
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    REFRESH_COOKIE_KEY: str
    USER_ID_COOKIE_KEY: str

    # email sender
    SENDER_ADDRESS: str
    SENDER_PASSWORD: str
    SMTP_SERVER_HOST: str
    SMTP_SERVER_PORT: int

    # superuser credentials
    SUPERUSER_USERNAME: str
    SUPERUSER_PASSWORD: str

    model_config = SettingsConfigDict(env_file=DOTENV_FILE_PATH)


config = Settings()

config.PRIVATE_KEY_PATH = join(ROOT_PATH, config.PRIVATE_KEY_PATH)
config.PUBLIC_KEY_PATH = join(ROOT_PATH, config.PUBLIC_KEY_PATH)
