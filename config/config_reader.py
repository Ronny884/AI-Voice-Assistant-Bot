from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    token: SecretStr = Field(env='TOKEN')
    admin: int = Field(env='ADMIN')
    openai_api_key: str = Field(env='OPENAI_API_KEY')
    based_assistant_id: str = Field(env='BASED_ASSISTANT_ID')
    values_assistant_id: str = Field(env='VALUES_ASSISTANT_ID')

    DB_HOST: str = Field(env='DB_HOST')
    DB_PORT: int = Field(env='DB_PORT')
    DB_USER: str = Field(env='DB_USER')
    DB_PASS: str = Field(env='DB_PASS')
    DB_NAME: str = Field(env='DB_NAME')


config = MySettings()