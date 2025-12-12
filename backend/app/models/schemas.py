"""
Pydantic schemas for request/response models

This module defines all data models used for API request validation and
response serialization. Pydantic provides automatic validation, serialization,
and OpenAPI schema generation.

Models are organized by their purpose:
- Request models: Validate incoming API requests
- Response models: Structure outgoing API responses
- Shared models: Reusable components (e.g., DocumentChunk)
"""

from typing import Optional

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """
    Response model returned after successful document upload.

    This response provides the client with all information needed to
    start querying the uploaded document.

    Attributes:
        collection_id: Unique identifier for the SAP vector collection.
            Used in subsequent chat requests.
        document_name: Name of the uploaded document (filename or generated)
        chunks_count: Number of text chunks created from the document.
            Higher counts indicate larger or more detailed documents.
        message: Optional human-readable message about the upload status
    """
    collection_id: str = Field(
        ...,
        description="SAP collection ID for subsequent queries",
        example="my_document_a1b2c3d4"
    )
    document_name: str = Field(
        ...,
        description="Name of the uploaded document",
        example="research_paper.pdf"
    )
    chunks_count: int = Field(
        ...,
        description="Number of text chunks created",
        example=42
    )
    message: Optional[str] = Field(
        default=None,
        description="Status message from the backend",
        example="Successfully uploaded document 'research_paper.pdf' to collection 'my_document_a1b2c3d4'. Document was split into 42 chunks and vectorized."
    )


class ChatRequest(BaseModel):
    """
    Request model for asking questions about uploaded documents.

    The client sends this to the /api/chat endpoint to perform semantic
    search and generate an answer using the specified LLM configuration.

    Attributes:
        collection_id: ID of the collection to search (from upload response)
        query: Natural language question about the document
        max_chunks: How many relevant chunks to retrieve (1-20).
            More chunks = more context but slower response.
        llm_model: Which LLM model to use for answer generation
        llm_temperature: Controls randomness (0.0 = deterministic, 2.0 = creative)
        llm_max_tokens: Maximum length of the generated answer
    """
    collection_id: str = Field(
        ...,
        description="Collection identifier from upload",
        example="my_document_a1b2c3d4"
    )
    query: str = Field(
        ...,
        min_length=1,
        description="Natural language question",
        example="What are the main findings of this research?"
    )
    max_chunks: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum relevant chunks to retrieve (1-20)"
    )
    llm_model: str = Field(
        default="gpt-4o",
        description="LLM model name",
        example="gpt-4o"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for response generation (0.0-2.0)"
    )
    llm_max_tokens: int = Field(
        default=10000,
        description="Maximum tokens in LLM response"
    )


class DocumentChunk(BaseModel):
    """
    A single chunk of document text with relevance score.

    Represents one segment of the original document that was found to be
    semantically relevant to the user's query.

    Attributes:
        content: The actual text content of this chunk
        score: Semantic similarity score (higher = more relevant)
        metadata: Additional information like chunk_index, document name, etc.
    """
    content: str = Field(
        ...,
        description="Text content of the chunk",
        example="The study found that machine learning models perform better with larger datasets."
    )
    score: float = Field(
        ...,
        description="Relevance score (higher = more relevant)",
        example=0.87
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata (chunk_index, name, etc.)",
        example={"chunk_index": "5", "name": "research_paper.pdf"}
    )


class ChatResponse(BaseModel):
    """
    Response model returned after processing a chat query.

    Contains the generated answer along with supporting evidence from
    the document chunks that were used to generate it.

    Attributes:
        collection_id: Echo of the requested collection ID
        query: Echo of the user's question
        response: Generated answer from the LLM
        chunks: List of relevant document chunks used for the answer
        chunks_found: Total number of relevant chunks retrieved
    """
    collection_id: str = Field(
        ...,
        description="Collection ID that was queried"
    )
    query: str = Field(
        ...,
        description="Original user query"
    )
    response: str = Field(
        ...,
        description="Generated answer from LLM",
        example="According to the research, the main findings indicate that..."
    )
    chunks: list[DocumentChunk] = Field(
        ...,
        description="Supporting document chunks with scores"
    )
    chunks_found: int = Field(
        ...,
        description="Number of chunks retrieved",
        example=5
    )


class HealthResponse(BaseModel):
    """
    Simple health check response for monitoring.

    Used by uptime monitors, load balancers, and Kubernetes probes
    to verify the service is running.

    Attributes:
        status: Current service status (healthy/unhealthy)
        service: Service name
        version: Application version number
    """
    status: str = Field(
        ...,
        description="Service health status",
        example="healthy"
    )
    service: str = Field(
        ...,
        description="Service name",
        example="Document Chat Service API"
    )
    version: str = Field(
        ...,
        description="API version",
        example="1.0.0"
    )


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    All API errors return this consistent structure to help clients
    handle errors gracefully.

    Attributes:
        error: Short error type or message
        detail: Optional detailed explanation for debugging
    """
    error: str = Field(
        ...,
        description="Error message",
        example="Collection not found"
    )
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error information",
        example="The collection ID 'xyz123' does not exist or has been deleted"
    )
