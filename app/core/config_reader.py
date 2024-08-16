from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE: str
    DATABASE_HOST: str
    DATABASE_PORT: str
    DATABASE_USER: str
    DATABASE_USER_PASSWORD: str

    model_config = SettingsConfigDict(env_file='../../.env', env_file_encoding='utf-8')


def get_config():
    return Settings()

