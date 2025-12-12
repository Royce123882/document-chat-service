"""
Helpers for decoding user-uploaded documents.

This module handles parsing and text extraction from various file formats.
Currently supports:
- UTF-8 encoded text files (.txt, .md, etc.)
- PDF files (.pdf)

All parsing errors are raised as ValueError to allow the API layer to
convert them to appropriate HTTP error responses (400 Bad Request).
"""

from io import BytesIO

from pypdf import PdfReader


def extract_text_from_upload(filename: str, content: bytes) -> str:
    """
    Extract text content from an uploaded file.

    Determines file type based on extension and delegates to the appropriate
    parser. Currently supports plain text (UTF-8) and PDF files.

    Args:
        filename: Name of the uploaded file (used to determine type)
        content: Raw bytes of the file content

    Returns:
        str: Extracted text content ready for chunking and vectorization

    Raises:
        ValueError: If file is not UTF-8 text or PDF, if PDF parsing fails,
            or if PDF contains no extractable text (e.g., images only)

    Example:
        ```python3
        content = await file.read()
        text = extract_text_from_upload("document.pdf", content)
        ```
    """
    normalized_name = filename or "untitled"

    # Route to appropriate parser based on file extension
    if normalized_name.lower().endswith('.pdf'):
        return _extract_text_from_pdf(content)

    # Default to text file parsing
    return _decode_text_file(content)


def _decode_text_file(content: bytes) -> str:
    """
    Decode bytes as UTF-8 text.

    This is a private helper that assumes the file is plain text.

    Args:
        content: Raw file bytes

    Returns:
        str: Decoded text content

    Raises:
        ValueError: If content is not valid UTF-8 (e.g., binary file)
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "File must be a text document (UTF-8 encoded) or a PDF file"
        ) from exc


def _extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from a PDF file using pypdf library.

    Reads all pages and concatenates their text content with double newlines
    between pages to preserve document structure.

    Args:
        content: Raw PDF file bytes

    Returns:
        str: Extracted text from all pages

    Raises:
        ValueError: If PDF parsing fails or if PDF contains no text
            (e.g., scanned images without OCR)
    """
    try:
        # Create a PDF reader from the byte stream
        reader = PdfReader(BytesIO(content))

        # Extract text from each page, defaulting to empty string if page is empty
        text_parts = [page.extract_text() or "" for page in reader.pages]

        # Join pages with double newlines to preserve document structure
        extracted = "\n\n".join(text_parts)
    except Exception as exc:
        # Catch all PDF parsing errors (corrupted file, unsupported features, etc.)
        raise ValueError(f"Failed to process PDF file: {exc}") from exc

    # Validate that we actually extracted some text
    if not extracted.strip():
        raise ValueError(
            "PDF file appears to be empty or contains no extractable text. "
            "This may be a scanned PDF that requires OCR."
        )

    return extracted
