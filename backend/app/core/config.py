from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Frontier Radar API"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/frontier_radar"
    resend_api_key: str = ""
    email_from: str = "alerts@frontierradar.local"
    email_to: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
