"""
🔧 Core Configuration Module
Centralized configuration management for Aether Multi-Agent Bot
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """📋 Application Settings"""
    
    # 🤖 Telegram Bot Configuration
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    alert_bot_token: str = Field(..., env="ALERT_BOT_TOKEN")
    alert_chat_id: str = Field(..., env="ALERT_CHAT_ID")
    allowed_users: List[int] = Field(default_factory=list, env="ALLOWED_USERS")
    
    # 🧠 AI Model API Keys
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    mistral_api_key: str = Field(..., env="MISTRAL_API_KEY")
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    
    # 🚦 Rate Limiting
    rate_limit: int = Field(default=10, env="RATE_LIMIT")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # 💾 Redis Configuration
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    redis_pass: str = Field(..., env="REDIS_PASS")
    redis_db: int = Field(default=0, env="REDIS_DB")
    
    # 📊 Monitoring Configuration
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    grafana_port: int = Field(default=3000, env="GRAFANA_PORT")
    grafana_password: str = Field(..., env="GRAFANA_PASSWORD")
    
    # 🌐 Application Configuration
    app_port: int = Field(default=8080, env="APP_PORT")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    debug: bool = Field(default=False, env="DEBUG")
    
    # 🔒 Security & Audit
    audit_log: str = Field(default="audit.log", env="AUDIT_LOG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(..., min_length=32, env="SECRET_KEY")
    
    # 🧠 Session Management
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")
    max_sessions: int = Field(default=100, env="MAX_SESSIONS")
    session_memory_limit: int = Field(default=1000, env="SESSION_MEMORY_LIMIT")
    
    # 🤖 AI Model Configuration
    default_model: str = Field(default="claude", env="DEFAULT_MODEL")
    model_timeout: int = Field(default=30, env="MODEL_TIMEOUT")
    max_tokens: int = Field(default=4000, env="MAX_TOKENS")
    temperature: float = Field(default=0.7, env="TEMPERATURE")
    
    # 🏥 Health Check Configuration
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(default=10, env="HEALTH_CHECK_TIMEOUT")
    
    # 🚨 Alert Configuration
    alert_webhook_url: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")
    alert_email: Optional[str] = Field(default=None, env="ALERT_EMAIL")
    
    # 🔧 Development Configuration
    dev_mode: bool = Field(default=False, env="DEV_MODE")
    test_mode: bool = Field(default=False, env="TEST_MODE")
    mock_ai: bool = Field(default=False, env="MOCK_AI")
    
    # 📁 File Storage
    upload_dir: str = Field(default="uploads/", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    
    # 🚩 Feature Flags
    enable_monitoring: bool = Field(default=True, env="ENABLE_MONITORING")
    enable_alerts: bool = Field(default=True, env="ENABLE_ALERTS")
    enable_audit: bool = Field(default=True, env="ENABLE_AUDIT")
    enable_cache: bool = Field(default=True, env="ENABLE_CACHE")
    enable_sessions: bool = Field(default=True, env="ENABLE_SESSIONS")
    
    # ⚡ Performance Configuration
    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    max_connections: int = Field(default=1000, env="MAX_CONNECTIONS")
    keepalive_timeout: int = Field(default=65, env="KEEPALIVE_TIMEOUT")
    
    # 💾 Backup Configuration
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_interval: int = Field(default=86400, env="BACKUP_INTERVAL")  # 24 hours
    backup_retention: int = Field(default=7, env="BACKUP_RETENTION")  # days
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __post_init__(self):
        """🔧 Post-initialization setup"""
        # Parse allowed_users from comma-separated string
        if isinstance(self.allowed_users, str):
            self.allowed_users = [int(uid.strip()) for uid in self.allowed_users.split(",") if uid.strip()]
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """✅ Validate configuration"""
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        
        if not self.allowed_users:
            raise ValueError("ALLOWED_USERS must contain at least one Telegram ID")
        
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        
        if self.default_model not in ["claude", "mistral", "groq", "gemini"]:
            raise ValueError(f"Invalid DEFAULT_MODEL: {self.default_model}")


@lru_cache()
def get_settings() -> Settings:
    """🔍 Get cached settings instance"""
    return Settings()


# 🌍 Environment-specific configurations
class DevelopmentSettings(Settings):
    """🛠️ Development environment settings"""
    debug: bool = True
    log_level: str = "DEBUG"
    mock_ai: bool = True
    enable_monitoring: bool = False
    enable_alerts: bool = False


class TestingSettings(Settings):
    """🧪 Testing environment settings"""
    test_mode: bool = True
    mock_ai: bool = True
    redis_db: int = 1  # Separate database for tests
    audit_log: str = "test_audit.log"


class ProductionSettings(Settings):
    """🚀 Production environment settings"""
    debug: bool = False
    log_level: str = "INFO"
    mock_ai: bool = False
    enable_monitoring: bool = True
    enable_alerts: bool = True
    enable_audit: bool = True


def get_environment_settings() -> Settings:
    """🔍 Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return ProductionSettings()


# 🎯 Configuration constants
class ConfigConstants:
    """📋 Configuration constants"""
    
    # 🤖 AI Model Settings
    AI_MODELS = {
        "claude": {
            "name": "Claude",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 30,
        },
        "mistral": {
            "name": "Mistral",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 20,
        },
        "groq": {
            "name": "Groq",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 10,
        },
        "gemini": {
            "name": "Gemini",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 30,
        },
    }
    
    # 📊 Monitoring Metrics
    METRICS = {
        "bot_requests_total": "Total number of bot requests",
        "bot_response_time": "Bot response time in seconds",
        "bot_errors_total": "Total number of bot errors",
        "active_sessions": "Number of active sessions",
        "ai_requests_total": "Total number of AI requests",
        "ai_response_time": "AI response time in seconds",
        "redis_connections": "Number of Redis connections",
        "memory_usage": "Memory usage in bytes",
        "cpu_usage": "CPU usage percentage",
    }
    
    # 🚨 Alert Levels
    ALERT_LEVELS = {
        "info": "Information",
        "warning": "Warning", 
        "error": "Error",
        "critical": "Critical",
    }
    
    # 🔐 Security Settings
    SECURITY = {
        "max_login_attempts": 3,
        "login_lockout_time": 300,  # 5 minutes
        "session_timeout": 3600,    # 1 hour
        "max_session_memory": 1000,  # 1KB per session
        "rate_limit_burst": 10,
        "rate_limit_period": 60,    # 1 minute
    }


# 🌍 Global settings instance
settings = get_settings()
