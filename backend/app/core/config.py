from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OBELIX_")

    data_dir: Path = Path("data")
    shared_configurations_dir: Path = Path("configurations")
    shared_scenarios_dir: Path = Path("scenarios/shared")
    local_configurations_dir: Path = Path("data/configurations")
    local_link16_configurations_dir: Path = Path("data/link16_configurations")
    shared_link16_configurations_dir: Path = Path("configurations/link16")
    templates_dir: Path = Path("data/templates")  # legacy alias
    scenarios_dir: Path = Path("data/scenarios")
    link16_scenarios_dir: Path = Path("data/link16_scenarios")
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
