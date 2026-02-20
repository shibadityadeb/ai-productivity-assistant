from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.config import get_settings
from app.utils.logger import setup_logging, get_logger
from app.api.routes import gmail, slack, toggl, ai
from app.models.schemas import HealthCheckResponse

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Initialize settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered productivity assistant integrating Gmail, Slack, Toggl, and AI APIs",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(gmail.router, prefix="/api")
app.include_router(slack.router, prefix="/api")
app.include_router(toggl.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info(
        "Application starting",
        environment=settings.environment,
        debug=settings.debug
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("Application shutting down")


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint - health check."""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now()
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
