import os
from dataclasses import dataclass
from datetime import date

DEFAULT_DATABASE_URL = "postgresql+psycopg://relay:relay@localhost:5432/relay"
DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://localhost:8080"


@dataclass(frozen=True)
class Settings:
    database_url: str
    as_of_date: date | None
    cors_origins: list[str]

    @classmethod
    def from_env(cls) -> "Settings":
        as_of = os.environ.get("AS_OF_DATE")
        origins = os.environ.get("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
        return cls(
            database_url=os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL),
            as_of_date=date.fromisoformat(as_of) if as_of else None,
            cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
        )
