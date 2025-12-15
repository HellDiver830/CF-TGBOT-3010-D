from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2: настройки чтения из окружения/.env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Общие настройки
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crypto P2P API"

    # Значения, которые берём из .env
    DB_URL: str
    SECRET_KEY: str = "super-secret-key-change-me"  # ⚠️ в проде ОБЯЗАТЕЛЬНО поменять
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3
    TATUM_API_KEY: str | None = None
    # В README указан именно TATUM_BASE_URL, поэтому держим поле в UPPER_SNAKE
    # и даём совместимый алиас-свойство ниже.
    TATUM_BASE_URL: str = "https://api.tatum.io"

    # --- alias-ы, которыми пользуется остальной код (snake_case) ---

    @property
    def db_url(self) -> str:
        return self.DB_URL

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def jwt_algorithm(self) -> str:
        return self.JWT_ALGORITHM

    @property
    def access_token_expire_minutes(self) -> int:
        return self.ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def tatum_api_key(self) -> str | None:
        return self.TATUM_API_KEY

    @property
    def tatum_base_url(self) -> str:
        return self.TATUM_BASE_URL


@lru_cache
def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
