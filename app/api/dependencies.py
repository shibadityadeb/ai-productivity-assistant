from fastapi import Depends
from app.config import get_settings, Settings


async def get_settings_dependency() -> Settings:
    """Dependency for application settings."""
    return get_settings()
