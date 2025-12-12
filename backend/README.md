# Document Chat Service - Backend

FastAPI backend for the Document Chat Service using SAP AI Core's Document Grounding Service and LLM.

## Setup

1. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your SAP AI Core credentials
   ```

   Required variables:

   ```env
   # SAP AI Core credentials
   SAP_API_URL=https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com
   SAP_AUTH_URL=https://your-tenant.authentication.eu10.hana.ondemand.com
   SAP_CLIENT_ID=your-client-id
   SAP_CLIENT_SECRET=your-client-secret
   SAP_RESOURCE_GROUP=default

   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false

   # CORS Configuration
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

4. **Run the server**

   ```bash
   python3 server.py
   ```

   This will start the FastAPI server with auto-reload enabled on the configured host and port.

## API Endpoints

### Health Check

- `GET /api/` - Health check endpoint

### Document Upload

- `POST /api/upload` - Upload a document and create a collection
  - Form data:
    - `file`: Text file (UTF-8 encoded, .txt, .md) or PDF
    - `chunk_size`: Optional chunk size (default: 500)
  - Returns: Collection details including collection_id

### Chat

- `POST /api/chat` - Ask questions about uploaded documents
  - JSON body:
    ```json
    {
      "collection_id": "string",
      "query": "string",
      "max_chunks": 5,
      "model": "gpt-4o",
      "temperature": 0.7
    }
    ```
  - Returns: AI-generated response with relevant document chunks

### Collection Management

- `DELETE /api/collections/{collection_id}` - Delete a collection and its documents

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # API route handlers
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic request/response models
│   ├── services/
│   │   ├── __init__.py
│   │   └── document_chat_service.py  # SAP AI Core integration
│   └── utils/
│       ├── __init__.py
│       ├── document_processing.py # Document chunking utilities
│       ├── file_parsers.py        # File parsing (text, PDF)
│       ├── llm_utils.py           # LLM integration utilities
│       └── logger.py              # Logging configuration
├── prompts/
│   └── document_qa_prompt.py      # Prompt templates for Q&A
├── .env.example
├── .gitignore
├── requirements.txt
├── server.py                      # Server entry point
└── README.md
```

## Features

- **Document Processing**: Automatic text extraction from .txt, .md, and PDF files
- **SAP AI Core Integration**: Document Grounding Service for semantic search
- **LLM Integration**: Configurable models via SAP Generative AI Hub (GPT-4, GPT-3.5, etc.)
- **Collection Management**: Create and manage document collections
- **Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Type Safety**: Full type hints with Pydantic validation
- **CORS Support**: Configurable CORS for frontend integration

## Development

The API documentation is automatically generated and available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing

```bash
# Run tests (if available)
pytest

# Code formatting
black app/

# Type checking
mypy app/
```

## Environment Variables

See `.env.example` for all available configuration options:

- **SAP AI Core**: API credentials and resource group
- **Server**: Host, port, debug mode
- **CORS**: Allowed origins for cross-origin requests
- **LLM**: Default model and temperature settings (optional)
