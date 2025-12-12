# Document Chat Service - Frontend

React frontend for the Document Chat Service with drag-and-drop file upload, LLM configuration, and real-time chat interface.

## Features

- **Drag-and-drop file upload** with visual feedback
- **PDF support** in addition to text files (.txt, .md)
- **Real-time chat interface** with message history
- **LLM configuration** - Select model and adjust temperature
- **Source chunk display** - View relevant document sections used in responses
- **Clean, modern UI** with responsive design
- **File validation** and comprehensive error handling
- **Collection tracking** - Each upload creates a unique collection ID

## Setup

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Configure environment (optional)**

   ```bash
   cp .env.example .env
   # Edit .env if you need to change the API URL
   ```

   Default configuration:

   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

3. **Run development server**

   ```bash
   npm run dev
   ```

   The app will be available at http://localhost:3000

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FileUpload.jsx         # Main file upload component
│   │   ├── FileUpload.css
│   │   ├── ChatInterface.jsx      # Main chat interface
│   │   ├── ChatInterface.css
│   │   ├── LLMSettings.jsx        # LLM configuration panel
│   │   ├── LLMSettings.css
│   │   ├── chat/                  # Chat sub-components
│   │   │   ├── ChatForm.jsx       # Message input form
│   │   │   ├── ChatHeader.jsx     # Chat header with actions
│   │   │   ├── ChunkDisplay.jsx   # Document chunk viewer
│   │   │   ├── Message.jsx        # Individual message component
│   │   │   └── MessageList.jsx    # Message list container
│   │   └── upload/                # Upload sub-components
│   │       └── DropZone.jsx       # Drag-and-drop zone
│   ├── services/
│   │   └── api.js                 # API service layer (Axios)
│   ├── hooks/
│   │   ├── useApiCall.js          # API call hook with loading states
│   │   └── useExpandable.js       # Expandable UI hook
│   ├── utils/
│   │   ├── format.js              # Formatting utilities
│   │   └── validation.js          # Validation utilities
│   ├── App.jsx                    # Main app component
│   ├── App.css
│   ├── main.jsx                   # React entry point
│   └── index.css                  # Global styles
├── index.html
├── vite.config.js
├── eslint.config.json
├── package.json
└── README.md
```

## Usage

1. **Start the backend** server first (see ../backend/README.md)
2. **Start the frontend** development server: `npm run dev`
3. **Open** http://localhost:3000
4. **Upload** a document (.txt, .md, or .pdf)
5. **Configure LLM** settings (optional) - select model and temperature
6. **Start chatting** - Ask questions about your document
7. **View sources** - Expand chunks to see which parts of the document were used
8. **New document** - Click "New Document" to upload another file

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client for API calls
- **CSS** - Modular component styling
- **Custom Hooks** - useApiCall, useExpandable

## Components Overview

### FileUpload

Main upload component with drag-and-drop functionality and file validation.

### ChatInterface

Complete chat experience with message history, LLM settings, and source chunk display.

### LLMSettings

Configuration panel for selecting AI model and adjusting temperature parameter.

### Chat Components

- **ChatForm**: Message input with send button
- **ChatHeader**: Header with document info and "New Document" action
- **ChunkDisplay**: Expandable view of relevant document chunks
- **Message**: Individual message with user/assistant styling
- **MessageList**: Auto-scrolling message container

### Upload Components

- **DropZone**: Drag-and-drop file upload zone with visual feedback

## API Integration

The frontend communicates with the backend via REST API:

```javascript
// Upload document
POST / api / upload;
FormData: {
  (file, chunk_size);
}

// Chat with document
POST / api / chat;
JSON: {
  (collection_id, query, max_chunks, model, temperature);
}

// Delete collection
DELETE / api / collections / { collection_id };
```

See `src/services/api.js` for implementation details.

## Development

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Configuration

### Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000/api`)

### Vite Config

See `vite.config.js` for build and dev server configuration.
