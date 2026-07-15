from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """환경 변수 / .env 로부터 로드되는 애플리케이션 설정."""

    database_url: str = "mysql+pymysql://appuser:apppassword@localhost:3306/authdb"
    jwt_secret_key: str = "change-me-to-a-secure-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
