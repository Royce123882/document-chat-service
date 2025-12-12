"""
SAP Document Chat Service

This service provides document upload and chat capabilities using SAP AI Core's
Document Grounding Service. Users can upload documents and chat with them without
any configuration needed.
"""

import hashlib
import uuid
from typing import Dict, List, Optional

import requests
from app.utils.document_processing import (
    build_document_payload,
    build_llm_prompt,
    chunk_document,
    extract_chunks_from_response,
)
from app.utils.llm_utils import init_llm_model
from app.utils.logger import get_logger, log_error, log_service_call

logger = get_logger(__name__)


class DocumentChatService:
    """
    A service for document upload and chat using SAP Document Grounding.

    This service handles:
    - Document upload and vectorization
    - Document chunking and embedding
    - Semantic search and chat over documents
    - Collection management per upload
    """

    def __init__(
        self,
        api_url: str,
        auth_url: str,
        client_id: str,
        client_secret: str,
        resource_group: str,
    ):
        """
        Initialize the Document Chat Service.

        Args:
            api_url: SAP AI Core API URL
            auth_url: OAuth2 authentication URL
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            resource_group: AI resource group
        """
        self.api_url = api_url
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_group = resource_group

        # Get access token
        self.access_token = self._fetch_access_token()
        log_service_call(
            logger,
            "DocumentChatService",
            "init",
            "completed",
            {"token_length": len(self.access_token)}
        )

        # Set up headers with AI-Resource-Group for all operations
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "AI-Resource-Group": self.resource_group,
            "Content-Type": "application/json",
        }

        # Store credentials for creating LLM instances on demand
        self.genai_credentials = {
            "clientid": self.client_id,
            "clientsecret": self.client_secret,
            "url": self.auth_url.replace("/oauth/token", ""),
            "serviceurls": {
                "AI_API_URL": self.api_url.replace("/v2", "")
            }
        }

        logger.info(
            "DocumentChatService initialized for resource group '%s'",
            self.resource_group
        )
        # Validate token and permissions
        self._validate_connection()

    def create_collection(self, collection_name: Optional[str] = None, embedding_model: str = "text-embedding-ada-002") -> str:
        """
        Create a new document collection.

        Args:
            collection_name: Optional name for the collection. If not provided,
                           a UUID will be generated.
            embedding_model: Embedding model to use (default: text-embedding-ada-002)
                           Other options: text-embedding-3-small, text-embedding-3-large

        Returns:
            Collection ID

        Raises:
            requests.RequestException: If the API request fails
        """
        if not collection_name:
            collection_name = f"collection_{uuid.uuid4()}"

        # Use the document-grounding endpoint
        # Payload based on official SAP AI Core documentation
        payload = {
            "title": collection_name,
            "embeddingConfig": {
                "modelName": embedding_model
            },
            "metadata": []
        }

        try:
            logger.info("Creating collection '%s'", collection_name)
            response = requests.post(
                f"{self.api_url}/v2/lm/document-grounding/vector/collections",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            # Collection ID is in the location header
            if "location" in response.headers:
                location = response.headers["location"]

                # Extract ID from URL
                # Location format: /v2/lm/document-grounding/vector/collections/{collectionId}
                # or could be: /lm/document-grounding/vector/collections/{collectionId}
                if "/collections/" in location:
                    collection_id = location.split("/collections/")[-1].split("/")[0].split("?")[0]
                else:
                    # Fallback to last segment
                    collection_id = location.split("/")[-1].split("?")[0]

                log_service_call(
                    logger,
                    "DocumentChatService",
                    "create_collection",
                    "completed",
                    {"collection_id": collection_id, "collection_name": collection_name}
                )
                logger.info("Collection created: %s", collection_id)
                return collection_id

            # Try response body as fallback
            collection_data = response.json() if response.text else {}
            collection_id = collection_data.get("id")

            if not collection_id:
                raise ValueError(f"Failed to extract collection ID. Location header: {response.headers.get('location')}, Response: {response.text}")

            log_service_call(
                logger,
                "DocumentChatService",
                "create_collection",
                "completed",
                {"collection_id": collection_id, "collection_name": collection_name}
            )
            return collection_id

        except requests.RequestException as e:
            log_error(logger, e, f"Failed to create collection '{collection_name}'")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
                logger.error(f"Response headers: {dict(e.response.headers)}")
            raise

    def upload_document(
        self,
        collection_id: str,
        content: str,
        document_name: Optional[str] = None,
        metadata: Optional[Dict] = None,
        chunk_size: int = 500,
    ) -> Dict:
        """
        Upload and vectorize a document to a collection.

        Args:
            collection_id: Target collection ID
            content: Document text content
            document_name: Optional document name
            metadata: Optional document metadata
            chunk_size: Size of text chunks (approximate character count)

        Returns:
            Dictionary with upload status:
            {
                "success": bool,
                "collection_id": str,
                "document_name": str,
                "chunks_count": int,
                "upload_response": dict,
                "message": str,
                "error": Optional[str]
            }
        """
        if not document_name:
            # Generate document name from content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            document_name = f"document_{content_hash}"

        chunks = chunk_document(content, chunk_size)

        payload = build_document_payload(
            document_name=document_name,
            chunks=chunks,
            metadata=metadata,
        )

        try:
            logger.info(
                "Uploading document to collection %s with %d chunks",
                collection_id,
                len(chunks)
            )
            response = requests.post(
                f"{self.api_url}/v2/lm/document-grounding/vector/collections/{collection_id}/documents",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            result_data = response.json() if response.text else {}

            return {
                "success": True,
                "collection_id": collection_id,
                "document_name": document_name,
                "chunks_count": len(chunks),
                "upload_response": result_data,
                "message": f"Successfully uploaded document '{document_name}' to collection '{collection_id}'. "
                          f"Document was split into {len(chunks)} chunks and vectorized.",
            }

        except requests.RequestException as e:
            log_error(logger, e, f"Failed to upload document '{document_name}'")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            return {
                "success": False,
                "collection_id": collection_id,
                "document_name": document_name,
                "chunks_count": 0,
                "upload_response": None,
                "message": f"Failed to upload document: {str(e)}",
                "error": str(e),
            }

    def chat_with_documents(
        self,
        collection_id: str,
        query: str,
        max_chunks: int = 5,
        llm_model: str = "gpt-4o",
        llm_temperature: float = 0.7,
        llm_max_tokens: int = 10000,
    ) -> Dict:
        """
        Chat with documents in a collection using semantic search.

        Args:
            collection_id: Collection ID to search
            query: User query/question
            max_chunks: Maximum number of relevant chunks to return
            llm_model: LLM model to use for response generation
            llm_temperature: Temperature for LLM (0.0-2.0)
            llm_max_tokens: Maximum tokens in LLM response

        Returns:
            Dictionary with search results:
            {
                "success": bool,
                "query": str,
                "chunks_found": int,
                "chunks": List[dict],
                "response_text": str,
                "full_response": dict,
                "error": Optional[str]
            }
        """
        payload = {
            "query": query,
            "filters": [
                {
                    "id": str(uuid.uuid4()),
                    "dataRepositories": [collection_id],
                    "dataRepositoryType": "vector",
                    "searchConfiguration": {"maxChunkCount": max_chunks},
                }
            ],
        }

        try:
            logger.info("Searching collection %s", collection_id)
            response = requests.post(
                f"{self.api_url}/v2/lm/document-grounding/retrieval/search",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            result_data = response.json()

            transformed_chunks = extract_chunks_from_response(result_data, logger=logger)

            # Generate LLM response using retrieved chunks as context
            if len(transformed_chunks) > 0:
                prompt = build_llm_prompt(transformed_chunks, query)

                try:
                    # Create LLM instance with user-specified parameters
                    llm = init_llm_model(
                        model=llm_model,
                        temperature=llm_temperature,
                        max_tokens=llm_max_tokens,
                        genai_platform_credentials=self.genai_credentials
                    )
                    llm_response = llm.invoke(prompt)
                    response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
                    logger.info(
                        "Generated response for collection %s using %d chunks with model=%s, temp=%.2f",
                        collection_id,
                        len(transformed_chunks),
                        llm_model,
                        llm_temperature
                    )
                except Exception as e:
                    logger.error(f"LLM generation failed: {e}")
                    response_text = f"Error generating response: {str(e)}"
            else:
                response_text = "No relevant information found in the documents to answer your question."

            return {
                "success": True,
                "query": query,
                "chunks_found": len(transformed_chunks),
                "chunks": transformed_chunks,
                "response_text": response_text,
                "full_response": result_data,
            }

        except requests.RequestException as e:
            log_error(logger, e, "Failed to search documents")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Search error status: {e.response.status_code}")
                logger.error(f"Search error body: {e.response.text}")
            return {
                "success": False,
                "query": query,
                "chunks_found": 0,
                "chunks": [],
                "response_text": f"Failed to search documents: {str(e)}",
                "full_response": None,
                "error": str(e),
            }

    def list_collections(self) -> List[Dict]:
        """
        List all collections in the resource group.

        Returns:
            List of collection metadata
        """
        try:
            response = requests.get(
                f"{self.api_url}/v2/lm/document-grounding/vector/collections",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            return response.json().get("resources", [])

        except requests.RequestException as e:
            log_error(logger, e, "Failed to list collections")
            return []

    def delete_collection(self, collection_id: str) -> bool:
        """
        Delete a collection and all its documents.

        Args:
            collection_id: Collection ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Deleting collection %s", collection_id)
            response = requests.delete(
                f"{self.api_url}/v2/lm/document-grounding/vector/collections/{collection_id}",
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            log_service_call(
                logger,
                "DocumentChatService",
                "delete_collection",
                "completed",
                {"collection_id": collection_id}
            )
            return True

        except requests.RequestException as e:
            log_error(logger, e, f"Failed to delete collection '{collection_id}'")
            return False

    def _fetch_access_token(self) -> str:
        """
        Retrieve an OAuth2 access token using client credentials.

        Returns:
            Access token

        Raises:
            Exception: If token retrieval fails
        """
        url = f"{self.auth_url}/oauth/token"
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()

            token = response.json().get("access_token")
            if not token:
                raise ValueError("No access token in response")

            return token

        except Exception as e:
            log_error(logger, e, "Failed to get access token")
            raise

    def _validate_connection(self) -> None:
        """
        Validate the connection and permissions by attempting to list collections.
        This helps catch authentication/permission issues early.

        Raises:
            Exception: If validation fails with detailed error message
        """
        try:
            response = requests.get(
                f"{self.api_url}/v2/lm/document-grounding/vector/collections",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 403:
                error_msg = (
                    f"403 Forbidden - Permission denied when accessing SAP AI Core.\n"
                    f"This usually means:\n"
                    f"1. Your service key lacks necessary role collections (e.g., 'aicore_admin_editor')\n"
                    f"2. The resource group '{self.resource_group}' doesn't have 'document-grounding: true' label\n"
                    f"3. You're using a free tier account with restrictions\n\n"
                    f"Response: {response.text}\n\n"
                    f"Solutions:\n"
                    f"- Check SAP BTP Cockpit for role collection assignments\n"
                    f"- Ensure your resource group has the label 'document-grounding: true'\n"
                    f"- Verify your service key has proper permissions"
                )
                logger.error(error_msg)
                raise PermissionError(error_msg)

            response.raise_for_status()

        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code != 403:
                logger.error(f"Connection validation failed: {e}")
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
