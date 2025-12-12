"""
Document processing helpers shared across services.

This module provides utilities for chunking documents, building prompts,
and transforming SAP API responses. These functions are used by the
DocumentChatService to prepare documents for vectorization and format
responses for the frontend.
"""

import re
from typing import Any, Dict, List, Optional

from prompts.document_qa_prompt import DOCUMENT_QA_SYSTEM_PROMPT


def format_document_qa_prompt(chunks: list[dict], query: str) -> str:
    """
    Format the document QA prompt with context chunks and user query.

    Args:
        chunks: List of document chunks with 'content' field
        query: User's question

    Returns:
        Formatted prompt string
    """
    context = "\n\n".join([
        f"[Document chunk {idx + 1}]:\n{chunk['content']}"
        for idx, chunk in enumerate(chunks)
    ])

    return DOCUMENT_QA_SYSTEM_PROMPT.format(
        context=context,
        query=query
    )


def chunk_document(content: str, chunk_size: int = 500) -> List[str]:
    """
    Split document text into manageable chunks for embedding generation.

    Uses a smart chunking strategy that prioritizes semantic boundaries:
    1. First, tries to chunk by paragraphs (preserves context)
    2. Falls back to sentence-based chunking for very long paragraphs

    This approach ensures that embeddings capture coherent semantic units
    rather than arbitrary character cutoffs.

    Args:
        content: Full document text to chunk
        chunk_size: Target size in characters (actual chunks may vary to
            respect paragraph/sentence boundaries)

    Returns:
        List of text chunks, each roughly chunk_size characters

    Example:
        ```python3
        text = "Paragraph 1.\\n\\nParagraph 2.\\n\\nParagraph 3."
        chunks = chunk_document(text, chunk_size=100)
        # Result: ['Paragraph 1.', 'Paragraph 2.', 'Paragraph 3.']
        ```
    """
    # Split on double newlines to identify paragraphs
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

    chunks: List[str] = []
    current_chunk: List[str] = []
    current_size = 0

    # Group paragraphs into chunks, respecting chunk_size limit
    for para in paragraphs:
        para_size = len(para)

        # If adding this paragraph would exceed chunk_size, save current chunk
        if current_size + para_size > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_size = para_size
        else:
            # Still room in current chunk
            current_chunk.append(para)
            current_size += para_size

    # Don't forget the last chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    # Fallback: if document is one giant paragraph, chunk by sentences
    if not chunks:
        chunks = _chunk_by_sentences(content, chunk_size)

    return chunks


def _chunk_by_sentences(content: str, chunk_size: int) -> List[str]:
    """
    Fallback chunking strategy that groups sentences together.

    Used when the document is a single large paragraph with no natural
    paragraph breaks. Splits on sentence boundaries (. ! ?) while preserving
    punctuation so generated answers can quote snippets verbatim.

    Args:
        content: Text content to chunk
        chunk_size: Target chunk size in characters

    Returns:
        List of sentence-based chunks

    Note:
        If no sentence boundaries are found, returns the entire content as
        a single chunk to avoid data loss.
    """
    # Split on sentence-ending punctuation followed by whitespace
    # Regex uses lookbehind to keep punctuation with the sentence
    sentences = re.split(r"(?<=[.!?])\s+", content)

    chunks: List[str] = []
    current_chunk: List[str] = []
    current_size = 0

    # Group sentences into chunks
    for sentence in sentences:
        sentence_size = len(sentence)

        # Start new chunk if adding this sentence would exceed limit
        if current_size + sentence_size > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size

    # Add final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Edge case: if no splits were possible, return entire content
    return chunks if chunks else [content]


def extract_chunks_from_response(result_data: Dict[str, Any], logger=None) -> List[Dict[str, Any]]:
    """
    Transform SAP Document Grounding API response into simplified chunk dictionaries.

    SAP's API returns a deeply nested structure with metadata in a custom format.
    This function flattens the response into simple dicts that are easier to
    work with in the frontend.

    Args:
        result_data: Raw response from SAP's /retrieval/search endpoint
        logger: Optional logger for warnings (e.g., unexpected response structure)

    Returns:
        List of chunk dictionaries with structure:
        ```python3
        {
            "content": str,      # The actual text content
            "score": float,      # Relevance score (0.0-1.0)
            "metadata": dict     # Flattened metadata (chunk_index, name, etc.)
        }
        ```

    Example SAP response structure (simplified):
        ```json
        {
            "results": [{
                "results": [{
                    "dataRepository": {
                        "documents": [{
                            "chunks": [{
                                "content": "...",
                                "searchScores": {"aggregatedScore": {"value": 0.85}},
                                "metadata": [{"key": "name", "value": ["doc.pdf"]}]
                            }]
                        }]
                    }
                }]
            }]
        }
        ```
    """
    # Early return if response structure is unexpected
    if "results" not in result_data:
        if logger:
            logger.warning(
                "No 'results' key in SAP response. Response keys: %s",
                list(result_data.keys()),
            )
        return []

    # Extract raw chunks from nested structure
    raw_chunks = _extract_raw_chunks_from_results(result_data["results"])

    # Transform each chunk into simplified format
    return [_transform_chunk(chunk) for chunk in raw_chunks]


def _extract_raw_chunks_from_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract all chunks from SAP's nested results structure.

    Args:
        results: Top-level results array from SAP response

    Returns:
        Flattened list of raw chunk objects
    """
    raw_chunks = []
    for filter_result in results:
        for repo_result in filter_result.get("results", []):
            data_repo = repo_result.get("dataRepository", {})
            documents = data_repo.get("documents", [])
            for document in documents:
                raw_chunks.extend(document.get("chunks", []))
    return raw_chunks


def _transform_chunk(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a single SAP chunk into simplified format.

    Args:
        chunk: Raw chunk object from SAP API

    Returns:
        Simplified chunk dict with content, score, and flattened metadata
    """
    return {
        "content": chunk.get("content", ""),
        "score": _extract_score(chunk),
        "metadata": _flatten_metadata(chunk.get("metadata", [])),
    }


def _extract_score(chunk: Dict[str, Any]) -> float:
    """
    Extract relevance score from chunk's nested searchScores structure.

    Args:
        chunk: Raw chunk object

    Returns:
        Relevance score (0.0-1.0), defaults to 0.0 if not found
    """
    search_scores = chunk.get("searchScores", {})
    aggregated_score = search_scores.get("aggregatedScore", {})
    return aggregated_score.get("value", 0.0)


def _flatten_metadata(metadata_list: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Convert SAP's metadata format to a simple key-value dict.

    SAP format: [{"key": "foo", "value": ["bar", "baz"]}]
    Output format: {"foo": "bar, baz"}

    Args:
        metadata_list: List of metadata items from SAP

    Returns:
        Flattened dict with string values
    """
    metadata_dict = {}
    for meta_item in metadata_list:
        key = meta_item.get("key", "")
        value = meta_item.get("value", [])

        # Convert value to string representation
        if isinstance(value, list):
            metadata_dict[key] = value[0] if len(value) == 1 else ", ".join(str(v) for v in value)
        else:
            metadata_dict[key] = str(value)

    return metadata_dict


def build_llm_prompt(chunks: List[Dict[str, Any]], query: str) -> str:
    """
    Construct the instruction prompt for LLM answer generation.

    Takes the retrieved document chunks and user query, formats them into
    a prompt that instructs the LLM to answer based on the provided context.

    Args:
        chunks: List of relevant document chunks with content and metadata
        query: User's natural language question

    Returns:
        Formatted prompt string ready for LLM completion

    Note:
        The actual prompt template is defined in prompts/document_qa_prompt.py
        to keep prompt engineering separate from business logic.
    """
    return format_document_qa_prompt(chunks, query)


def build_document_payload(
    document_name: str,
    chunks: List[str],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create SAP-compatible document payload for upload requests.

    SAP's Document Grounding API expects a specific nested JSON structure
    with metadata as key-value arrays. This function encapsulates that
    structure to avoid duplicating it across the codebase.

    Args:
        document_name: Name/identifier for the document
        chunks: List of text chunks to upload
        metadata: Optional additional metadata to attach to the document

    Returns:
        Dictionary in SAP's expected format:
        ```python3
        {
            "documents": [{
                "metadata": [{"key": "...", "value": ["..."]}],
                "chunks": [
                    {"content": "...", "metadata": [...]},
                    ...
                ]
            }]
        }
        ```

    Example:
        ```python3
        payload = build_document_payload(
            document_name="research.pdf",
            chunks=["First chunk", "Second chunk"],
            metadata={"author": "John Doe"}
        )
        ```
    """
    # Build document-level metadata in SAP's format
    metadata_items = [
        {"key": "name", "value": [document_name]},
        {"key": "source", "value": ["user_upload"]},
    ]

    # Add any custom metadata provided by caller
    if metadata:
        metadata_items.extend(
            {"key": key, "value": [str(value)]} for key, value in metadata.items()
        )

    # Build the document structure with chunks
    documents = [
        {
            "metadata": metadata_items,
            "chunks": [
                {
                    "content": chunk,
                    # Each chunk gets its own metadata (chunk index for reference)
                    "metadata": [
                        {"key": "chunk_index", "value": [str(idx)]},
                    ],
                }
                for idx, chunk in enumerate(chunks)
            ],
        }
    ]

    return {"documents": documents}
