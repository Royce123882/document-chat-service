"""
LLM and embedding model initialization utilities.

This module provides functions for initializing language models and embedding
models from SAP's GenAI Hub. It handles:
- Proxy client setup with authentication
- LLM model initialization (GPT-4, etc.)
- Embedding model initialization (text-embedding-ada-002, etc.)

All models are initialized through SAP's proxy client which handles routing
requests to the appropriate backend (OpenAI, Azure OpenAI, etc.) based on
the model configuration in SAP AI Core.
"""

import json
import os
from typing import Any, Dict

from app.utils.logger import get_logger, log_service_call
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model as init_embedding_model_genai_hub
from gen_ai_hub.proxy.langchain.init_models import (
    init_llm,
)
from langchain_core.language_models.chat_models import BaseChatModel

logger = get_logger(__name__)


def init_proxy_client(genai_platform_credentials: Dict = None) -> Any:
    """Initialize a proxy client for API requests.

    The helper prefers credentials passed in by the caller so production
    deployments can read secrets from environment variables/secret stores. When
    omitted, we fall back to ``app/secrets/genai-credentials.json`` which is
    meant strictly for local development and is git-ignored.

    Args:
        genai_platform_credentials: Optional credentials dict. If not provided,
            loads from ``app/secrets/genai-credentials.json`` relative to this
            module.

    Returns:
        A proxy client configured with authentication and base URLs.
    """
    if genai_platform_credentials is None:
        # Load credentials from file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(script_dir, "..", "secrets", "genai-credentials.json")

        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                "GenAI credentials not provided and app/secrets/genai-credentials.json"
                " was not found. Supply genai_platform_credentials explicitly"
                " when running outside local development."
            )

        with open(credentials_path, 'r') as f:
            genai_platform_credentials = json.load(f)

    client_id = genai_platform_credentials["clientid"]
    client_secret = genai_platform_credentials["clientsecret"]
    auth_url = f"{genai_platform_credentials['url']}/oauth/token"
    base_url = f"{genai_platform_credentials['serviceurls']['AI_API_URL']}/v2"

    proxy_client = get_proxy_client(
        proxy_version="gen-ai-hub",
        base_url=base_url,
        auth_url=auth_url,
        client_id=client_id,
        client_secret=client_secret,
    )

    log_service_call(
        logger,
        "LLMUtils",
        "init_proxy_client",
        "completed",
        {"base_url": base_url}
    )

    return proxy_client


def init_llm_model(
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 3000,
    genai_platform_credentials: Dict = None
) -> BaseChatModel:
    """
    Initialize a language model from SAP GenAI Hub.

    Creates a LangChain-compatible chat model that routes requests through
    SAP's proxy to the configured backend (e.g., OpenAI, Azure OpenAI).

    Args:
        model: Model identifier (e.g., "gpt-4o", "gpt-4", "gpt-3.5-turbo")
        temperature: Controls randomness in responses:
            - 0.0 = deterministic (same input -> same output)
            - 1.0 = balanced creativity
            - 2.0 = maximum randomness
        max_tokens: Maximum tokens in the model's response
        genai_platform_credentials: Optional credentials dict. If not provided,
            loads from app/secrets/genai-credentials.json

    Returns:
        Initialized LangChain chat model ready for use

    Example:
        ```python3
        llm = init_llm_model("gpt-4o", temperature=0.7, max_tokens=1000)
        response = llm.invoke("What is the capital of France?")
        print(response.content)
        ```
    """
    proxy_client = init_proxy_client(genai_platform_credentials)

    llm = init_llm(
        model,
        proxy_client=proxy_client,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    log_service_call(
        logger,
        "LLMUtils",
        "init_llm_model",
        "completed",
        {"model": model, "temperature": temperature, "max_tokens": max_tokens}
    )

    return llm


def init_embedding_model(embeddings_model: str, genai_platform_credentials: Dict = None):
    """
    Initialize an embeddings model from SAP GenAI Hub.

    Creates a LangChain-compatible embeddings model for generating vector
    representations of text. Used for semantic search and similarity matching.

    Args:
        embeddings_model: Model identifier (e.g., "text-embedding-ada-002",
            "text-embedding-3-small", "text-embedding-3-large")
        genai_platform_credentials: Optional credentials dict. If not provided,
            loads from app/secrets/genai-credentials.json

    Returns:
        Initialized LangChain embeddings model

    Example:
        ```python3
        embeddings = init_embedding_model("text-embedding-ada-002")
        vectors = embeddings.embed_documents(["Hello world", "Goodbye world"])
        ```
    """
    proxy_client = init_proxy_client(genai_platform_credentials)

    embeddings = init_embedding_model_genai_hub(
        embeddings_model,
        proxy_client=proxy_client,
    )

    log_service_call(
        logger,
        "LLMUtils",
        "init_embedding_model",
        "completed",
        {"model": embeddings_model}
    )

    return embeddings
