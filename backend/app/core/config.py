from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Frontier Radar API"
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/frontier_radar"
    resend_api_key: str = ""
    email_from: str = "alerts@frontierradar.local"
    email_to: str = ""
    rrc_production_source_url: str = "https://www.rrc.texas.gov/media/sample/frontier-rrc-production.csv"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
