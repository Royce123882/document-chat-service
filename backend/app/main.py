"""
Main FastAPI application

This module creates and configures the FastAPI application instance,
sets up middleware, configures CORS, and manages application lifecycle events.
"""

from contextlib import asynccontextmanager

from app.api.routes import router
from app.config import get_config
from app.dependencies import get_document_service
from app.utils.logger import get_logger, setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging with colored output for better development experience
setup_logging(level="INFO", use_colors=True)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events (startup and shutdown).

    This context manager handles initialization and cleanup tasks that should
    run once when the application starts and when it shuts down.

    Startup tasks:
        - Initialize the document service singleton
        - Validate SAP AI Core connection

    Shutdown tasks:
        - Log shutdown event (cleanup tasks can be added here)

    Args:
        app: FastAPI application instance

    Yields:
        None

    Raises:
        Exception: If service initialization fails during startup
    """
    # Startup phase
    logger.info("Starting Document Chat Service...")
    try:
        # Initialize document service on startup to validate credentials
        # and establish connection to SAP AI Core
        get_document_service()
        logger.info("Service initialization complete")
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise

    yield

    # Shutdown phase
    logger.info("Shutting down Document Chat Service...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    This factory function:
    1. Loads application configuration from environment variables
    2. Creates FastAPI instance with metadata
    3. Configures CORS middleware for frontend communication
    4. Registers API routes under /api prefix

    Returns:
        FastAPI: Configured application instance ready to serve requests
    """
    config = get_config()

    app = FastAPI(
        title=config.app_name,
        version=config.app_version,
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(router, prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    config = get_config()
    uvicorn.run(
        "app.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
