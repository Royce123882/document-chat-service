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

from typing import Any, Dict

from app.utils.logger import get_logger, log_service_call
from gen_ai_hub.proxy.core.proxy_clients import get_proxy_client
from gen_ai_hub.proxy.langchain.init_models import init_embedding_model as init_embedding_model_genai_hub
from gen_ai_hub.proxy.langchain.init_models import (
    init_llm,
)
from langchain_core.language_models.chat_models import BaseChatModel

logger = get_logger(__name__)


def init_proxy_client(genai_hub_credentials: Dict) -> Any:
    """Initialize a proxy client for API requests.

    Args:
        genai_hub_credentials: Credentials dict loaded from environment variables.
            Must contain: clientid, clientsecret, url, and serviceurls.AI_API_URL

    Returns:
        A proxy client configured with authentication and base URLs.
    """
    client_id = genai_hub_credentials["clientid"]
    client_secret = genai_hub_credentials["clientsecret"]
    auth_url = f"{genai_hub_credentials['url']}/oauth/token"
    base_url = f"{genai_hub_credentials['serviceurls']['AI_API_URL']}/v2"

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
    genai_hub_credentials: Dict,
    temperature: float = 0.0,
    max_tokens: int = 3000
) -> BaseChatModel:
    """
    Initialize a language model from SAP GenAI Hub.

    Creates a LangChain-compatible chat model that routes requests through
    SAP's proxy to the configured backend (e.g., OpenAI, Azure OpenAI).

    Args:
        model: Model identifier (e.g., "gpt-4o", "gpt-4", "gpt-3.5-turbo")
        genai_hub_credentials: Credentials dict loaded from environment variables.
            Must contain: clientid, clientsecret, url, and serviceurls.AI_API_URL
        temperature: Controls randomness in responses:
            - 0.0 = deterministic (same input -> same output)
            - 1.0 = balanced creativity
            - 2.0 = maximum randomness
        max_tokens: Maximum tokens in the model's response

    Returns:
        Initialized LangChain chat model ready for use

    Example:
        ```python3
        credentials = {...}  # Load from .env
        llm = init_llm_model("gpt-4o", credentials, temperature=0.7, max_tokens=1000)
        response = llm.invoke("What is the capital of France?")
        print(response.content)
        ```
    """
    proxy_client = init_proxy_client(genai_hub_credentials)

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


def init_embedding_model(embeddings_model: str, genai_hub_credentials: Dict):
    """
    Initialize an embeddings model from SAP GenAI Hub.

    Creates a LangChain-compatible embeddings model for generating vector
    representations of text. Used for semantic search and similarity matching.

    Args:
        embeddings_model: Model identifier (e.g., "text-embedding-ada-002",
            "text-embedding-3-small", "text-embedding-3-large")
        genai_hub_credentials: Credentials dict loaded from environment variables.
            Must contain: clientid, clientsecret, url, and serviceurls.AI_API_URL

    Returns:
        Initialized LangChain embeddings model

    Example:
        ```python3
        embeddings = init_embedding_model("text-embedding-ada-002")
        vectors = embeddings.embed_documents(["Hello world", "Goodbye world"])
        ```
    """
    proxy_client = init_proxy_client(genai_hub_credentials)

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
