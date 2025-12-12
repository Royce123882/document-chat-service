"""
Document Chat Service Backend Application

A FastAPI-based service that enables semantic search and chat with documents
using SAP AI Core's Document Grounding capabilities. This application provides
endpoints for uploading documents (text/PDF), creating vector collections,
and performing LLM-powered question answering over document content.

Key features:
- Document upload and vectorization (PDF and text files)
- Semantic search using SAP AI Core embeddings
- LLM-powered question answering
- Collection management per document upload
- RESTful API with OpenAPI documentation

Architecture:
- FastAPI for web framework
- SAP AI Core for vector storage and LLM inference
- LangChain for LLM orchestration
- Pydantic for data validation
"""
