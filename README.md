# Document Chat Service

> **Note:** This is an open-source project that is **NOT ACTIVELY MAINTAINED**. Feel free to fork and use as needed.

A full-stack application for uploading documents and chatting with them using SAP AI Core's Document Grounding Service.

## Features

- **Upload Documents**: Drag-and-drop or browse to upload text documents and PDFs
- **Ask Questions**: Interactive chat interface to ask questions about your documents
- **Semantic Search**: Powered by SAP AI Core's Document Grounding Service
- **Modern UI**: Clean, responsive interface
- **LLM Configuration**: Configurable model selection and temperature settings

## Technology Stack

**Backend:**

- FastAPI
- Python 3.8+
- SAP AI Core SDK

**Frontend:**

- React 18
- Vite
- Axios

## Prerequisites

- Python 3.8+
- Node.js 18+
- SAP AI Core account with:
  - **Document Grounding Service** - For document vectorization and semantic search
  - **LLM (Generative AI Hub)** - For generating responses (e.g., GPT-4, GPT-3.5-turbo)

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your SAP AI Core credentials

# Run server
python3 server.py
```

Backend will be available at http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Optional: Configure environment
cp .env.example .env

# Run development server
npm run dev
```

Frontend will be available at http://localhost:3000

### 3. Using the Start Script

From the project root:

```bash
./start.sh
```

This will start both backend and frontend services.

## Environment Variables

### Backend (.env)

```env
# SAP AI Core credentials (from your service key)
SAP_API_URL=https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com
SAP_AUTH_URL=https://your-tenant.authentication.eu10.hana.ondemand.com
SAP_CLIENT_ID=your-client-id
SAP_CLIENT_SECRET=your-client-secret
SAP_RESOURCE_GROUP=default

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
```

## Project Structure

```
sap-file-search/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── utils/       # Utilities (file parsing, LLM, logging)
│   │   └── prompts/     # Prompt templates
│   ├── requirements.txt
│   └── server.py
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API layer
│   │   ├── hooks/       # Custom hooks
│   │   └── utils/       # Utilities
│   └── package.json
└── start.sh             # Quick start script
```

## Usage

1. **Upload a Document**: Drag and drop or browse to upload a text file or PDF
2. **Configure LLM** (optional): Select model and adjust temperature in settings
3. **Start Chatting**: Type your question and get AI-powered responses based on your document
4. **Upload Another**: Click "New Document" to start a new chat session

## API Documentation

Once the backend is running, visit:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## How It Works

1. User uploads a document through the UI
2. Backend extracts text and creates a collection in SAP Document Grounding Service
3. Document is chunked and vectorized using embedding models
4. User asks questions in the chat interface
5. Backend performs semantic search to find relevant document chunks
6. Retrieved chunks are passed to an LLM as context
7. LLM generates a response based on the document content
8. User sees the AI-generated answer along with source chunks

## Troubleshooting

**Backend Issues:**

- Verify SAP AI Core credentials in `.env`
- Ensure virtual environment is activated
- Check network connectivity to SAP services

**SAP AI Core LLM Issues:**

- Verify that Generative AI Hub is enabled in your SAP AI Core instance
- Ensure the LLM model (e.g., `gpt-4o`, `gpt-35-turbo`) is available in your deployment
- Check that your resource group has access to the LLM service
- Verify authentication token is valid and not expired
- If you see "model not found" errors, check available models in your SAP AI Core dashboard
- Ensure sufficient quota/credits are available for LLM API calls

**SAP AI Core Document Grounding Issues:**

- Verify Document Grounding Service is provisioned and enabled
- Check that the resource group matches your Document Grounding deployment
- Ensure embedding models are available and accessible
- If collection creation fails, verify your API credentials have write permissions
- For "collection not found" errors, check that the collection_id is valid and not expired
- Document Grounding has size limits - ensure documents don't exceed service limits
- If vectorization fails, check document encoding (must be UTF-8)

**Frontend Issues:**

- Ensure backend is running on port 8000
- Check CORS configuration if you see fetch errors
- Delete `node_modules` and run `npm install` again if build fails

**File Upload Issues:**

- Only .txt, .md, and .pdf files are supported
- Files must be UTF-8 encoded
- Maximum file size is 10MB

## Support

This project is **not actively maintained**. For issues or questions:

- Check the API documentation at http://localhost:8000/docs
- Refer to SAP AI Core documentation
- Fork the project and modify as needed
