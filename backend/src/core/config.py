"""
CP'S Enterprise POS - Configuration Module
============================================
Centralized configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================
    # Application Settings
    # ============================================
    app_name: str = Field(default="CP'S Enterprise POS", alias="APP_NAME")
    app_version: str = Field(default="2.0.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    secret_key: str = Field(..., alias="SECRET_KEY")

    # ============================================
    # Server Settings
    # ============================================
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=4, alias="WORKERS")
    reload: bool = Field(default=False, alias="RELOAD")

    # ============================================
    # Database Settings
    # ============================================
    database_url: PostgresDsn = Field(..., alias="DATABASE_URL")
    database_pool_size: int = Field(default=20, alias="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, alias="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, alias="DATABASE_POOL_TIMEOUT")

    # ============================================
    # Redis Settings
    # ============================================
    redis_url: RedisDsn = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    redis_pool_size: int = Field(default=50, alias="REDIS_POOL_SIZE")

    # ============================================
    # JWT Settings
    # ============================================
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # ============================================
    # Email Settings
    # ============================================
    smtp_host: Optional[str] = Field(default=None, alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, alias="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_tls: bool = Field(default=True, alias="SMTP_TLS")
    smtp_from_email: str = Field(
        default="noreply@cps-enterprise.com", alias="SMTP_FROM_EMAIL"
    )
    smtp_from_name: str = Field(
        default="CP'S Enterprise POS", alias="SMTP_FROM_NAME"
    )

    # ============================================
    # Storage Settings
    # ============================================
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    aws_access_key_id: Optional[str] = Field(default=None, alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(
        default=None, alias="AWS_SECRET_ACCESS_KEY"
    )
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    aws_s3_bucket: Optional[str] = Field(default=None, alias="AWS_S3_BUCKET")

    # ============================================
    # Security Settings
    # ============================================
    allowed_hosts: List[str] = Field(
        default=["localhost", "127.0.0.1"], alias="ALLOWED_HOSTS"
    )
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS",
    )
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")

    # ============================================
    # Feature Flags
    # ============================================
    enable_registration: bool = Field(default=True, alias="ENABLE_REGISTRATION")
    enable_email_verification: bool = Field(
        default=False, alias="ENABLE_EMAIL_VERIFICATION"
    )
    enable_mfa: bool = Field(default=False, alias="ENABLE_MFA")
    enable_analytics: bool = Field(default=True, alias="ENABLE_ANALYTICS")

    # ============================================
    # Cache Settings
    # ============================================
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    cache_prefix: str = Field(default="cps_pos", alias="CACHE_PREFIX")

    # ============================================
    # Celery Settings
    # ============================================
    celery_broker_url: str = Field(
        default="amqp://guest:guest@localhost:5672//", alias="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1", alias="CELERY_RESULT_BACKEND"
    )
    celery_task_always_eager: bool = Field(
        default=False, alias="CELERY_TASK_ALWAYS_EAGER"
    )

    # ============================================
    # Logging Settings
    # ============================================
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, alias="LOG_FILE")

    # ============================================
    # Sentry Settings
    # ============================================
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    sentry_environment: str = Field(default="development", alias="SENTRY_ENVIRONMENT")

    # ============================================
    # Validators
    # ============================================
    @validator("allowed_hosts", "cors_origins", pre=True)
    def parse_comma_separated(cls, v):
        """Parse comma-separated string to list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.app_env == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
