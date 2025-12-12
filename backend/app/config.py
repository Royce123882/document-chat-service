"""
Application configuration

This module manages all application configuration using environment variables.
Configuration is loaded from a .env file and provides sensible defaults for
development environments.

Configuration categories:
- App settings: Application metadata and debug mode
- SAP AI Core settings: Credentials and endpoints for SAP services
- Server settings: Host and port configuration
- CORS settings: Allowed origins for cross-origin requests
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file in the backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """
    Application configuration loaded from environment variables.

    All settings can be overridden via environment variables. The .env file
    provides a convenient way to manage configuration in development.

    Attributes:
        app_name: Application name displayed in API docs
        app_version: Semantic version number
        debug: Enable debug mode (verbose logging, auto-reload)

        sap_api_url: SAP AI Core API base URL
        sap_auth_url: OAuth2 token endpoint URL
        sap_client_id: OAuth2 client ID from service key
        sap_client_secret: OAuth2 client secret from service key
        sap_resource_group: SAP AI Core resource group name

        host: Server bind address (0.0.0.0 = all interfaces)
        port: Server port number

        cors_origins: Comma-separated list of allowed CORS origins
    """

    # App settings
    app_name: str = "Document Chat Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # SAP AI Core settings - loaded from service key
    sap_api_url: str = os.getenv("SAP_API_URL", "")
    sap_auth_url: str = os.getenv("SAP_AUTH_URL", "")
    sap_client_id: str = os.getenv("SAP_CLIENT_ID", "")
    sap_client_secret: str = os.getenv("SAP_CLIENT_SECRET", "")
    sap_resource_group: str = os.getenv("SAP_RESOURCE_GROUP", "")

    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # CORS settings - allows frontend to make API calls
    cors_origins: list[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173"
    ).split(",")


@lru_cache()
def get_config() -> Config:
    """
    Get cached configuration instance.

    Uses functools.lru_cache to ensure configuration is only loaded once
    and shared across the application. This improves performance and ensures
    consistency.

    Returns:
        Config: Singleton configuration instance
    """
    return Config()
