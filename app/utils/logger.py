import logging
import sys
from pathlib import Path
import structlog
from app.config import get_settings


def setup_logging():
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Set log level
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer() if settings.log_format == "json" 
            else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


def get_logger(name: str = __name__):
    """Get a logger instance."""
    return structlog.get_logger(name)
