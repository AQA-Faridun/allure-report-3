from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INTERSHOP_", env_file=".env", extra="ignore", env_ignore_empty=True
    )

    base_url: str = "https://intershop6.skillbox.ru"
    stand_name: str = "intershop6 (public demo)"
    api_timeout_s: float = Field(default=20.0, gt=0)
    ui_timeout_ms: int = Field(default=15_000, gt=0)
    web_artifacts: Literal["on-failure", "always"] = "on-failure"
    data_seed: int | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
