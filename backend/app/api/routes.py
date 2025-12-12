"""
API route handlers

This module defines all HTTP endpoints for the Document Chat Service.
Routes are organized using FastAPI's APIRouter for clean separation of concerns.

Endpoints:
    GET  /api/           - Health check
    POST /api/upload     - Upload and vectorize a document
    POST /api/chat       - Query a document collection
    DELETE /api/collections/{id} - Delete a collection
"""

import uuid

from app.dependencies import get_document_service
from app.models.schemas import ChatRequest, ChatResponse, DocumentChunk, HealthResponse, UploadResponse
from app.services.document_chat_service import DocumentChatService
from app.utils.file_parsers import extract_text_from_upload
from app.utils.logger import get_logger
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns a simple JSON response indicating service status. This endpoint
    is designed to be fast and lightweight for frequent polling by monitoring
    systems, Kubernetes probes, and uptime checkers.

    Returns:
        HealthResponse: Service status, name, and version

    Example response:
        ```json
        {
            "status": "healthy",
            "service": "Document Chat Service API",
            "version": "1.0.0"
        }
        ```
    """
    return HealthResponse(
        status="healthy",
        service="Document Chat Service API",
        version="1.0.0"
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Form(500),
    doc_service: DocumentChatService = Depends(get_document_service)
):
    """Create a fresh collection and ingest the uploaded file.

    The backend always spins up a dedicated SAP Document Grounding collection per
    upload so chat sessions have an isolated vector store. Text files are read as
    UTF-8; PDFs are parsed page by page via ``pypdf``. Non-text content, empty
    PDFs, or processing errors surface as ``400`` responses so the UI can guide
    users before we talk to SAP services.

    Args:
        file: Multipart payload containing a UTF-8 text document or PDF.
        chunk_size: Optional chunk size hint for downstream chunking logic.
        doc_service: Injected ``DocumentChatService`` that owns SAP RPC calls.

    Returns:
        UploadResponse: IDs and metadata for the newly created collection.
    """
    try:
        # Step 1: Read the uploaded file content
        # FastAPI's UploadFile provides the raw bytes, which we read once
        # to avoid multiple file reads
        content = await file.read()

        # Step 2: Extract text from the file (handles both text and PDF files)
        filename = file.filename or "untitled"
        try:
            text_content = extract_text_from_upload(filename, content)
        except ValueError as file_error:
            # Surface file parsing errors (invalid encoding, empty PDF, etc.) as 400
            # so the client knows it's a file content issue, not a server error
            raise HTTPException(status_code=400, detail=str(file_error))

        # Step 3: Create a dedicated SAP vector collection for this document
        # Each upload gets its own isolated collection to keep vectors scoped
        # and prevent cross-document interference in search results
        sanitized_name = filename.replace(' ', '_').lower() or "document"
        # Include random suffix to ensure uniqueness even with duplicate filenames
        collection_name = f"{sanitized_name[:32]}_{uuid.uuid4().hex[:8]}"
        collection_id = doc_service.create_collection(
            collection_name=collection_name
        )

        # Step 4: Upload the text content to SAP Document Grounding
        # This chunks the document, generates embeddings, and stores in the collection
        result = doc_service.upload_document(
            collection_id=collection_id,
            content=text_content,
            document_name=filename,
            chunk_size=chunk_size
        )

        # Step 5: Check if upload succeeded
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Failed to upload document")
            )

        # Step 6: Return success response with collection details
        return UploadResponse(
            collection_id=collection_id,
            document_name=result.get("document_name", filename),
            chunks_count=result.get("chunks_count", 0),
            message=result.get("message")
        )

    except HTTPException:
        # Re-raise HTTP exceptions (400, 500) without modification
        raise
    except Exception as e:
        # Catch any unexpected errors and return as 500
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    doc_service: DocumentChatService = Depends(get_document_service)
):
    """Run semantic search against a collection and format the answer.

    The ``DocumentChatService`` performs both the SAP vector search and LLM
    answer synthesis. We convert the opaque ``chunks`` payload coming back into
    typed ``DocumentChunk`` objects so the OpenAPI schema documents the contract
    that the frontend consumes.

    Args:
        request: User payload containing ``collection_id``, ``query``, and
            optional ``max_chunks`` limit.
        doc_service: Injected ``DocumentChatService`` used to talk to SAP APIs.

    Returns:
        ChatResponse: Answer text plus the supporting chunk metadata.
    """
    try:
        # Step 1: Perform semantic search and generate LLM response
        # This does two things:
        # a) Searches the vector collection for relevant chunks
        # b) Uses the retrieved chunks as context to generate an answer with the LLM
        result = doc_service.chat_with_documents(
            collection_id=request.collection_id,
            query=request.query,
            max_chunks=request.max_chunks,
            llm_model=request.llm_model,
            llm_temperature=request.llm_temperature,
            llm_max_tokens=request.llm_max_tokens
        )

        # Step 2: Validate the search succeeded
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to search documents")
            )

        # Step 3: Convert raw chunk dictionaries to Pydantic models
        # This provides type safety and proper OpenAPI schema documentation
        chunks = [
            DocumentChunk(
                content=chunk.get("content", ""),
                score=chunk.get("score", 0.0),
                metadata=chunk.get("metadata")
            )
            for chunk in result.get("chunks", [])
        ]

        # Step 4: Return structured response with answer and supporting chunks
        return ChatResponse(
            collection_id=request.collection_id,
            query=result.get("query", request.query),
            response=result.get("response_text", ""),
            chunks=chunks,
            chunks_found=result.get("chunks_found", 0)
        )

    except ValueError as e:
        # ValueError is raised when collection doesn't exist
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: str,
    doc_service: DocumentChatService = Depends(get_document_service)
):
    """
    Delete a vector collection and all its documents from SAP AI Core.

    This endpoint should be called when the user is done with a document
    to free up resources and prevent accumulation of unused collections.

    Args:
        collection_id: Unique identifier of the collection to delete
        doc_service: Injected DocumentChatService (auto-injected by FastAPI)

    Returns:
        dict: Success message confirming deletion

    Raises:
        HTTPException 404: If collection doesn't exist or couldn't be deleted

    Example:
        DELETE /api/collections/my_document_a1b2c3d4
    """
    # Attempt to delete the collection from SAP AI Core
    success = doc_service.delete_collection(collection_id)

    if not success:
        # Return 404 if collection wasn't found or deletion failed
        raise HTTPException(
            status_code=404,
            detail="Collection not found or could not be deleted"
        )

    return {"message": "Collection deleted successfully"}
