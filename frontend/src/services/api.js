import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * @typedef {Object} UploadResponse
 * @property {string} collection_id Backend-generated SAP collection identifier
 * @property {string} document_name Original file name or generated fallback
 * @property {number} chunks_count Number of chunks created during ingestion
 * @property {string} [message] Human readable status from the backend
 */

/**
 * @typedef {Object} ChatChunk
 * @property {string} content Chunk text returned by SAP search
 * @property {number} score Relevance score (0-1)
 * @property {Object} [metadata] Additional metadata such as chunk_index
 */

/**
 * @typedef {Object} ChatResponse
 * @property {string} collection_id Identifier the response belongs to
 * @property {string} query Server-normalized query string
 * @property {string} response Natural language answer produced by the LLM
 * @property {ChatChunk[]} chunks Supporting chunks for UI display
 * @property {number} chunks_found Total matches surfaced by semantic search
 */

export const documentService = {
  /**
   * Upload a document file.
   * @param {File} file - The file to upload.
   * @param {number} chunkSize - Chunk size for document processing.
   * @returns {Promise<UploadResponse>} Upload response payload.
   */
  uploadDocument: async (file, chunkSize = 500) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("chunk_size", chunkSize);

    const response = await api.post("/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  /**
   * Send a chat query.
   * @param {string} collectionId - Collection ID the conversation targets.
   * @param {string} query - User query as typed in the UI.
   * @param {number} maxChunks - Maximum chunks to retrieve for context.
   * @param {string} llmModel - LLM model to use for response generation.
   * @param {number} llmTemperature - Temperature for LLM (0.0-2.0).
   * @param {number} llmMaxTokens - Maximum tokens in LLM response.
   * @returns {Promise<ChatResponse>} Chat response with answer + chunk data.
   */
  sendChatQuery: async (
    collectionId,
    query,
    maxChunks = 5,
    llmModel = "gpt-4o",
    llmTemperature = 0.7,
    llmMaxTokens = 10000,
  ) => {
    const response = await api.post("/chat", {
      collection_id: collectionId,
      query,
      max_chunks: maxChunks,
      llm_model: llmModel,
      llm_temperature: llmTemperature,
      llm_max_tokens: llmMaxTokens,
    });
    return response.data;
  },

  /**
   * Health check for quickly verifying backend availability.
   * @returns {Promise<{status: string, service: string, version: string}>}
   */
  healthCheck: async () => {
    const response = await api.get("/");
    return response.data;
  },
};

export default api;
