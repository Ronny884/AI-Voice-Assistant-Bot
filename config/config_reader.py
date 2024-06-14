from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class MySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    token: SecretStr = Field(env='TOKEN')
    admin: int = Field(env='ADMIN')
    openai_api_key: str = Field(env='OPENAI_API_KEY')
    assistant_id: str = Field(env='ASSISTANT_ID')
    vector_store_id: str = Field(env='VECTOR_STORE_ID')
    amplitude_api_key: str = Field(env='AMPLITUDE_API_KEY')
    DB_HOST: str = Field(env='DB_HOST')
    DB_PORT: int = Field(env='DB_PORT')
    DB_USER: str = Field(env='DB_USER')
    DB_PASS: str = Field(env='DB_PASS')
    DB_NAME: str = Field(env='DB_NAME')
    db_url: str = Field(env='DB_URL')
    redis_url: str = Field(env='REDIS_URL')


config = MySettings()