from typing import List, Optional, Union
import json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _clean_database_url(url: Optional[str]) -> Optional[str]:
    if not url or not isinstance(url, str):
        return url
    # Normalization: Supabase or Heroku may provide postgres:// which SQLAlchemy 1.4+ rejects
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    
    # Strip parameters like ?pgbouncer=true which Prisma uses but psycopg2/libpq rejects
    parsed = urlparse(url)
    if parsed.query:
        unsupported = {"pgbouncer", "connection_limit", "schema"}
        pairs = parse_qsl(parsed.query, keep_blank_values=True)
        filtered = [(k, v) for k, v in pairs if k.lower() not in unsupported]
        new_query = urlencode(filtered)
        url = urlunparse(parsed._replace(query=new_query))
    return url


class Settings(BaseSettings):
    PROJECT_NAME: str = "LeadPulse AI"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # CORS origins
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database URLs
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    DIRECT_URL: Optional[str] = None  # Dedicated port 5432 connection for Alembic migrations

    # Google Gemini AI Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    @field_validator("DATABASE_URL", "DIRECT_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Optional[str]:
        return _clean_database_url(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
