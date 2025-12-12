"""
Dependency injection for FastAPI

This module provides dependency injection functions used by FastAPI routes.
Dependencies are cached to ensure singleton behavior and efficient resource usage.

FastAPI's dependency injection system automatically calls these functions and
provides their return values to route handlers via the Depends() parameter.
"""

import logging
from functools import lru_cache

from app.config import get_config
from app.services.document_chat_service import DocumentChatService

logger = logging.getLogger(__name__)


@lru_cache()
def get_document_service() -> DocumentChatService:
    """
    Get or create a singleton DocumentChatService instance.

    This function is decorated with lru_cache to ensure only one instance
    of the DocumentChatService is created and shared across all requests.
    This is important because:
    1. The service maintains an OAuth2 access token
    2. Creating multiple instances would waste resources
    3. Connection validation only needs to happen once

    The service is initialized with SAP AI Core credentials from the
    application configuration (loaded from environment variables).

    Returns:
        DocumentChatService: Initialized and validated service instance

    Raises:
        RuntimeError: If service initialization fails (e.g., invalid credentials,
            network issues, or missing permissions)

    Example:
        In a FastAPI route:
        ```python3
        @router.post("/upload")
        async def upload_document(
            file: UploadFile,
            service: DocumentChatService = Depends(get_document_service)
        ):
            result = service.upload_document(...)
        ```
    """
    config = get_config()

    try:
        service = DocumentChatService(
            api_url=config.sap_api_url,
            auth_url=config.sap_auth_url,
            client_id=config.sap_client_id,
            client_secret=config.sap_client_secret,
            resource_group=config.sap_resource_group
        )
        logger.info("Document service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize document service: {e}")
        raise RuntimeError(f"Service initialization failed: {e}")
