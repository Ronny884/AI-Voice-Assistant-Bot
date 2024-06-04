from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    token: SecretStr = Field(env='TOKEN')
    admin: int = Field(env='ADMIN')
    openai_api_key: str = Field(env='OPENAI_API_KEY')


config = MySettings()