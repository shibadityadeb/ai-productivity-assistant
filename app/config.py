import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Core Settings
    app_name: str = "AI Productivity Assistant"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Gmail API
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = ""
    gmail_credentials_path: str = "credentials/gmail_token.json"
    
    # Slack API
    slack_bot_token: str = ""
    slack_app_token: str = ""
    slack_signing_secret: str = ""
    
    # Toggl API
    toggl_api_token: str = ""
    toggl_workspace_id: str = ""
    
    # Claude API
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"
    
    # Gemini API
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
