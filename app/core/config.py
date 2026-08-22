from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PushpThreadsAPI"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    applicationinsights_connection_string: str | None = None

    db_server: str = "localhost"
    db_port: int = 1433
    db_name: str = "PushpThreads"
    db_driver: str = "SQL Server"
    db_encrypt: bool = True
    db_trust_server_certificate: bool = True
    db_trusted_connection: bool = True
    db_user: str | None = None
    db_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def database_url(self) -> str:
        auth = "Trusted_Connection=yes;" if self.db_trusted_connection else (
            f"UID={self.db_user};PWD={self.db_password};"
        )
        connection_string = (
            f"DRIVER={{{self.db_driver}}};SERVER={self.db_server},{self.db_port};"
            f"DATABASE={self.db_name};{auth}"
            f"Encrypt={'yes' if self.db_encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if self.db_trust_server_certificate else 'no'};"
        )
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
