"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/railways",
        description="Async SQLAlchemy database URL",
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/railways",
        description="Sync database URL (for Alembic / scripts)",
    )

    # ── Security ──────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="super-secret-change-me-in-production",
        description="JWT signing secret",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    # ── Simulator ─────────────────────────────────────────────
    SIMULATOR_INTERVAL_MS: int = Field(
        default=1000,
        description="Telemetry tick interval in milliseconds (1000 = 1 Hz)",
    )
    SIMULATOR_ENABLED: bool = True
    SIMULATOR_LOCOMOTIVE_ID: str = "LOC-001"

    # ── WebSocket ─────────────────────────────────────────────
    WS_HEARTBEAT_SEC: int = 30

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
    ]

    # ── Health Config ─────────────────────────────────────────
    HEALTH_CONFIG_PATH: str = "health_config.yaml"

    # ── Buffer ────────────────────────────────────────────────
    BUFFER_SIZE: int = 1000  # ring-buffer capacity (frames)
    EMA_ALPHA: float = 0.3  # smoothing factor

    # ── Default admin ─────────────────────────────────────────
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
