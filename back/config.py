from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    anthropic_api_key: str = Field()
    weather_api_key: str = Field()
    model: str = "claude-4-sonnet-20250514"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


config = Config()
