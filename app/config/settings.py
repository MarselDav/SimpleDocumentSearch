from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    postgres_user : str
    postgres_password : SecretStr
    postgres_host : str
    postgres_port : int
    postgres_db : str

    elasticsearch_url : str
    elasticsearch_username : str
    elastic_password : SecretStr

    table_name : str = "documents"
    postgres_test_db: str = "test_documents"

    index_name : str = "documents"
    test_index_name : str = "test_documents"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Кэшируем синглтон настроек
@lru_cache
def get_settings() -> Settings:
    return Settings()


# Создаем глобальный объект настроек
settings = get_settings()