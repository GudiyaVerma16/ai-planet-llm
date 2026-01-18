# 📚 Complete Source Code Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Backend Documentation](#backend-documentation)
5. [Frontend Documentation](#frontend-documentation)
6. [API Reference](#api-reference)
7. [Database Schema](#database-schema)
8. [Configuration](#configuration)
9. [Deployment](#deployment)
10. [Code Flow Examples](#code-flow-examples)

---

## Project Overview

**AI Planet** is a No-Code/Low-Code web application that enables users to visually create and interact with intelligent workflows. Users can build workflows by connecting components that handle user input, extract knowledge from documents, interact with language models, and return answers through a chat interface.

### Key Features
- **Visual Workflow Builder**: Drag-and-drop interface using React Flow
- **Document Processing**: PDF text extraction and embedding generation
- **Vector Search**: Semantic search using embeddings stored in PostgreSQL
- **Multiple LLM Support**: OpenAI GPT and Google Gemini
- **Web Search Integration**: Optional SerpAPI and Brave Search
- **Workflow Execution**: Dynamic workflow execution based on user-defined connections
- **Chat Interface**: Interactive chat for querying workflows

### Tech Stack
- **Frontend**: React.js, Vite, React Flow, Axios
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **AI/ML**: OpenAI API, Google Gemini API, PyMuPDF
- **Deployment**: Docker, Render

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │ Workflow     │  │   Chat        │     │
│  │              │  │ Builder      │  │  Interface    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────┬───────────────────────────────────┘
                            │ HTTP/REST API
┌───────────────────────────▼───────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Routers    │  │   Services   │  │   Models     │       │
│  │              │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└───────┬───────────────┬───────────────┬───────────────┬───────┘
        │               │               │               │
┌───────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌───▼──────┐
│  PostgreSQL  │  │   OpenAI   │  │  Gemini   │  │ SerpAPI  │
│   Database   │  │    API     │  │    API    │  │   API    │
└──────────────┘  └────────────┘  └───────────┘  └──────────┘
```

### Component Flow

```
User Query → Knowledge Base → LLM Engine → Output
    │             │              │            │
    │             │              │            │
    └─────────────┴──────────────┴────────────┘
                  │
            (Optional Context)
```

---

## Directory Structure

```
Ai-planet/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── database.py             # Database configuration & session management
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   ├── routers/                # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── workflows.py        # Workflow CRUD operations
│   │   │   ├── documents.py        # Document upload & management
│   │   │   ├── chat.py             # Chat query execution
│   │   │   └── components.py       # Component type definitions
│   │   └── services/               # Business logic layer
│   │       ├── document_service.py      # Document processing & search
│   │       ├── embedding_service.py     # Embedding generation
│   │       ├── llm_service.py           # LLM interactions
│   │       └── workflow_executor.py     # Workflow execution engine
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Backend container definition
│   └── .env                        # Environment variables (not in git)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx           # Main dashboard view
│   │   │   ├── WorkflowBuilder.jsx     # Visual workflow builder
│   │   │   ├── ComponentLibrary.jsx    # Component drag-drop panel
│   │   │   ├── ChatInterface.jsx        # Chat UI component
│   │   │   ├── CreateStackModal.jsx     # Stack creation modal
│   │   │   └── *.css                    # Component styles
│   │   ├── App.jsx                 # Root component & routing
│   │   ├── main.jsx                # React entry point
│   │   ├── config.js               # API configuration
│   │   └── *.css                    # Global styles
│   ├── package.json                # Node.js dependencies
│   ├── vite.config.js              # Vite build configuration
│   └── Dockerfile                  # Frontend container definition
│
├── docker-compose.yml              # Multi-container orchestration
├── render.yaml                     # Render deployment configuration
├── README.md                       # Project overview & setup
└── DESIGN_DOCUMENTATION.md         # Design decisions & architecture
```

---

## Backend Documentation

### 1. Application Entry Point (`app/main.py`)

**Purpose**: Initializes FastAPI application, configures CORS, and registers routers.

**Key Components**:
- **FastAPI App**: Main application instance with metadata
- **CORS Middleware**: Handles cross-origin requests (configurable via `ALLOWED_ORIGINS`)
- **Database Initialization**: Auto-creates tables on startup
- **Router Registration**: Mounts all API routers under `/api` prefix

**Code Structure**:
```python
app = FastAPI(
    title="AI Planet - No-Code Workflow Builder",
    description="A No-Code/Low-Code web application for building intelligent workflows",
    version="1.0.0",
    redirect_slashes=False
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, ...)

# Router registration
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(components.router, prefix="/api/components", tags=["components"])
```

### 2. Database Layer (`app/database.py`)

**Purpose**: Manages database connection and session lifecycle.

**Key Components**:
- **Database URL**: Read from `DATABASE_URL` environment variable
- **SQLAlchemy Engine**: Connection pool management
- **Session Factory**: Creates database sessions for requests
- **Base Class**: Base class for all ORM models

**Session Management**:
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. Data Models (`app/models.py`)

**Purpose**: Defines database schema using SQLAlchemy ORM.

#### Workflow Model
```python
class Workflow(Base):
    id: int (Primary Key)
    name: str (Optional)
    description: str (Optional)
    nodes: JSON (React Flow nodes)
    edges: JSON (React Flow edges)
    created_at: DateTime
    updated_at: DateTime
    chat_logs: Relationship (One-to-Many with ChatLog)
```

#### Document Model
```python
class Document(Base):
    id: int (Primary Key)
    filename: str
    file_path: str
    file_size: int
    content: Text (Extracted text)
    file_metadata: JSON (Pages, embeddings_status, etc.)
    created_at: DateTime
    embeddings: Relationship (One-to-Many with Embedding)
```

#### Embedding Model
```python
class Embedding(Base):
    id: int (Primary Key)
    document_id: int (Foreign Key → Document.id)
    chunk_text: Text
    embedding_vector: JSON (Array of floats)
    chunk_index: int
    created_at: DateTime
    document: Relationship (Many-to-One with Document)
```

#### ChatLog Model
```python
class ChatLog(Base):
    id: int (Primary Key)
    workflow_id: int (Foreign Key → Workflow.id, Optional)
    query: Text
    response: Text
    execution_log: JSON (Workflow execution details)
    created_at: DateTime
    workflow: Relationship (Many-to-One with Workflow)
```

### 4. API Schemas (`app/schemas.py`)

**Purpose**: Pydantic models for request/response validation and serialization.

**Key Schemas**:
- `WorkflowCreate`: Input schema for creating workflows
- `WorkflowResponse`: Output schema for workflow data
- `DocumentResponse`: Output schema for document metadata
- `ChatQuery`: Input schema for chat queries
- `ChatResponse`: Output schema for chat responses
- `ChatLogResponse`: Output schema for chat log history

### 5. API Routers

#### 5.1 Workflows Router (`app/routers/workflows.py`)

**Endpoints**:
- `POST /api/workflows` - Create a new workflow
- `GET /api/workflows` - Get all workflows
- `GET /api/workflows/{id}` - Get specific workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow

**Key Logic**:
- Stores workflow as JSON (nodes and edges from React Flow)
- Validates workflow structure
- Supports CRUD operations

#### 5.2 Documents Router (`app/routers/documents.py`)

**Endpoints**:
- `POST /api/documents/upload` - Upload and process PDF
- `GET /api/documents` - List all documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/documents/search` - Search documents

**Key Logic**:
- **Upload Flow**:
  1. Validates PDF file
  2. Generates unique filename (UUID)
  3. Saves file to disk
  4. Extracts text using PyMuPDF
  5. Creates document record
  6. Triggers background embedding generation
  7. Returns immediately (non-blocking)

- **Background Processing**:
  - Embedding generation runs asynchronously
  - Prevents upload timeout
  - Updates `embeddings_status` in metadata

#### 5.3 Chat Router (`app/routers/chat.py`)

**Endpoints**:
- `POST /api/chat/query` - Execute workflow query
- `GET /api/chat/logs` - Get chat history
- `GET /api/chat/logs/{id}` - Get specific chat log

**Key Logic**:
- Receives workflow definition (nodes + edges) and query
- Executes workflow using `WorkflowExecutor`
- Saves chat log with execution details
- Handles rate limit errors gracefully

#### 5.4 Components Router (`app/routers/components.py`)

**Endpoints**:
- `GET /api/components/types` - Get available component types

**Returns**: List of component definitions with configuration options

### 6. Service Layer

#### 6.1 Document Service (`app/services/document_service.py`)

**Responsibilities**:
- PDF text extraction using PyMuPDF
- Text chunking for embedding generation
- Document search (vector similarity + keyword fallback)
- Embedding storage and retrieval

**Key Methods**:
- `extract_text_from_pdf(file_path)`: Extracts text from PDF
- `_chunk_text(text, max_chunks=2)`: Splits text into chunks
- `generate_embeddings_for_document(doc_id, text)`: Generates and stores embeddings
- `search_documents(db, query, top_k=5)`: Searches documents using embeddings

**Search Algorithm**:
1. Try vector similarity search using embeddings
2. If no embeddings found, fallback to keyword search
3. For general queries ("summarize", "what about"), return latest document chunk
4. Returns relevant text chunks for LLM context

#### 6.2 Embedding Service (`app/services/embedding_service.py`)

**Responsibilities**:
- Generate embeddings using OpenAI or Google Gemini
- Handle rate limits and retries
- Clean text (remove NUL bytes, special characters)
- Model fallback for unavailable models

**Key Methods**:
- `generate_embeddings(text, model="openai")`: Main embedding generation
- `_generate_openai_embeddings(text)`: OpenAI embedding generation
- `_generate_google_embeddings(text, fast_mode=False)`: Google Gemini embedding generation

**Model Mapping**:
- Maps legacy model names to current API versions
- Handles `gemini-1.5-flash` → `gemini-2.0-flash` or `gemini-2.5-flash`
- Implements fast fallback for rate limit errors

**Error Handling**:
- Aggressive text cleaning (removes problematic characters)
- Rate limit retries with exponential backoff
- Graceful degradation on API failures

#### 6.3 LLM Service (`app/services/llm_service.py`)

**Responsibilities**:
- Generate responses using OpenAI GPT or Google Gemini
- Build prompts with context
- Optional web search integration (SerpAPI/Brave)
- Handle model selection and fallback

**Key Methods**:
- `generate_response(query, context=None, provider="gemini", model=None, custom_prompt=None, use_web_search=False)`: Main LLM interaction
- `_generate_openai_response(...)`: OpenAI GPT generation
- `_generate_gemini_response(...)`: Google Gemini generation
- `_build_prompt(query, context, custom_prompt)`: Prompt construction
- `_perform_web_search(query, provider="serpapi")`: Web search integration

**Prompt Building**:
- Replaces `{context}` and `{query}` placeholders in custom prompts
- Appends context if placeholders missing
- Includes web search results if enabled

**Model Fallback**:
- Tries multiple Gemini models in sequence
- Stops immediately on rate limit errors
- Maps legacy model names to current versions

#### 6.4 Workflow Executor (`app/services/workflow_executor.py`)

**Responsibilities**:
- Execute workflows based on node connections
- Traverse workflow graph
- Process each component in order
- Build execution log

**Key Methods**:
- `execute_workflow(query, nodes, edges)`: Main execution method

**Execution Algorithm**:
1. **Build Graph**: Create node map and edge adjacency list
2. **Find Entry Point**: Locate User Query component
3. **Traverse Graph**: Process nodes in topological order
4. **Component Processing**:
   - **User Query**: Extract query from input
   - **Knowledge Base**: Search documents, return context
   - **LLM Engine**: Generate response using query + context
   - **Output**: Format final response
5. **Build Log**: Track execution status for each node
6. **Return Result**: Response + execution log

**Data Flow**:
```
User Query → {query: "..."}
    ↓
Knowledge Base → {context: "..."}
    ↓
LLM Engine → {response: "..."}
    ↓
Output → Final response
```

---

## Frontend Documentation

### 1. Application Structure (`src/App.jsx`)

**Purpose**: Root component managing application state and routing.

**State Management**:
- `currentView`: 'dashboard' | 'workflow'
- `currentWorkflow`: Selected workflow object
- `showChat`: Chat modal visibility
- `stackName` / `stackDescription`: New stack creation
- `refreshDashboard`: Trigger dashboard refresh

**Key Handlers**:
- `handleSelectStack`: Navigate to workflow builder with existing workflow
- `handleCreateNewStack`: Create new workflow
- `handleWorkflowBuilt`: After workflow save, keep it for chat
- `handleBackToDashboard`: Return to dashboard

### 2. Configuration (`src/config.js`)

**Purpose**: Centralized API configuration with environment variable support.

**Implementation**:
```javascript
const envApiUrl = import.meta.env.VITE_API_BASE_URL

const getApiBaseUrl = () => {
  // Use environment variable if set
  if (envApiUrl && envApiUrl.trim() !== '') {
    return envApiUrl.trim()
  }
  
  // Auto-detect backend URL on Render
  if (window.location.hostname.includes('onrender.com')) {
    // Try to construct backend URL from frontend URL
    // ...
  }
  
  // Default to localhost for development
  return 'http://localhost:8001/api'
}

export const API_BASE_URL = getApiBaseUrl()
```

**Usage**: All components import `API_BASE_URL` from this file.

### 3. Components

#### 3.1 Dashboard (`src/components/Dashboard.jsx`)

**Purpose**: Main landing page showing all saved workflows (stacks).

**Features**:
- List all workflows as cards
- Create new stack button
- Edit existing stack
- Delete stack functionality
- Empty state for new users

**API Calls**:
- `GET /api/workflows` - Fetch all workflows
- `DELETE /api/workflows/{id}` - Delete workflow

#### 3.2 Workflow Builder (`src/components/WorkflowBuilder.jsx`)

**Purpose**: Visual workflow builder using React Flow.

**Key Features**:
- **React Flow Canvas**: Drag-and-drop nodes, connect with edges
- **Component Library**: Side panel with draggable components
- **Node Configuration**: Inline configuration for each component
- **File Upload**: Direct PDF upload in Knowledge Base node
- **Save Workflow**: Validates and saves to backend

**Component Types**:
1. **User Query Node**: Entry point for queries
2. **Knowledge Base Node**: Document upload and selection
3. **LLM Engine Node**: Model selection, prompt configuration, web search toggle
4. **Output Node**: Final response display

**React Flow Integration**:
- Uses `useNodesState` and `useEdgesState` hooks
- Custom node components with handles
- Edge validation
- Zoom and pan controls

**API Calls**:
- `POST /api/documents/upload` - Upload PDF
- `GET /api/documents` - List documents
- `GET /api/components/types` - Get component definitions
- `POST /api/workflows` - Create workflow
- `PUT /api/workflows/{id}` - Update workflow

#### 3.3 Component Library (`src/components/ComponentLibrary.jsx`)

**Purpose**: Side panel for dragging components onto canvas.

**Features**:
- List of available components
- Drag handlers for React Flow
- Visual component previews

#### 3.4 Chat Interface (`src/components/ChatInterface.jsx`)

**Purpose**: Chat UI for interacting with workflows.

**Features**:
- Message history display
- Input field with send button
- Execution log expansion
- Loading states
- Error handling

**API Calls**:
- `POST /api/chat/query` - Execute workflow query

**Message Flow**:
1. User types query
2. Sends to backend with workflow definition
3. Displays response
4. Shows execution log (expandable)

#### 3.5 Create Stack Modal (`src/components/CreateStackModal.jsx`)

**Purpose**: Modal for creating new workflow with name and description.

**Features**:
- Name input
- Description textarea
- Create/Cancel buttons

---

## API Reference

### Base URL
- **Local**: `http://localhost:8001/api`
- **Production**: `https://your-backend-url.onrender.com/api`

### Authentication
Currently no authentication required (can be added for production).

### Workflows API

#### Create Workflow
```http
POST /api/workflows
Content-Type: application/json

{
  "name": "My Workflow",
  "description": "Description",
  "nodes": [...],
  "edges": [...]
}
```

**Response**: `WorkflowResponse`

#### Get All Workflows
```http
GET /api/workflows
```

**Response**: `List[WorkflowResponse]`

#### Get Workflow
```http
GET /api/workflows/{id}
```

**Response**: `WorkflowResponse`

#### Update Workflow
```http
PUT /api/workflows/{id}
Content-Type: application/json

{
  "name": "Updated Name",
  "nodes": [...],
  "edges": [...]
}
```

**Response**: `WorkflowResponse`

#### Delete Workflow
```http
DELETE /api/workflows/{id}
```

**Response**: `{"message": "Workflow deleted successfully"}`

### Documents API

#### Upload Document
```http
POST /api/documents/upload
Content-Type: multipart/form-data

file: <PDF file>
```

**Response**: `DocumentResponse`

**Note**: Embedding generation runs in background. Check `file_metadata.embeddings_status`.

#### Get All Documents
```http
GET /api/documents
```

**Response**: `List[DocumentResponse]`

#### Get Document
```http
GET /api/documents/{id}
```

**Response**: `DocumentResponse`

#### Delete Document
```http
DELETE /api/documents/{id}
```

**Response**: `{"message": "Document deleted successfully"}`

#### Search Documents
```http
POST /api/documents/search?query=your query&top_k=5
```

**Response**: `{"query": "...", "results": [...]}`

### Chat API

#### Execute Query
```http
POST /api/chat/query
Content-Type: application/json

{
  "workflow_id": 1,
  "query": "What is this file about?",
  "nodes": [...],
  "edges": [...]
}
```

**Response**: `ChatResponse`
```json
{
  "response": "Generated response...",
  "execution_log": [
    {
      "node_id": "...",
      "node_type": "userQuery",
      "status": "completed",
      "output": "..."
    },
    ...
  ]
}
```

#### Get Chat Logs
```http
GET /api/chat/logs?workflow_id=1&limit=50
```

**Response**: `List[ChatLogResponse]`

#### Get Chat Log
```http
GET /api/chat/logs/{id}
```

**Response**: `ChatLogResponse`

### Components API

#### Get Component Types
```http
GET /api/components/types
```

**Response**: `List[ComponentType]`

---

## Database Schema

### Tables

#### workflows
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR | NULLABLE | Workflow name |
| description | TEXT | NULLABLE | Workflow description |
| nodes | JSON | NOT NULL | React Flow nodes |
| edges | JSON | NOT NULL | React Flow edges |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NULLABLE | Update timestamp |

#### documents
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| filename | VARCHAR | NOT NULL | Original filename |
| file_path | VARCHAR | NOT NULL | Server file path |
| file_size | INTEGER | NOT NULL | File size in bytes |
| content | TEXT | NULLABLE | Extracted text |
| file_metadata | JSON | NULLABLE | Metadata (pages, status) |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

#### embeddings
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| document_id | INTEGER | FOREIGN KEY | Reference to documents.id |
| chunk_text | TEXT | NOT NULL | Text chunk |
| embedding_vector | JSON | NOT NULL | Embedding array |
| chunk_index | INTEGER | NOT NULL | Chunk order |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

#### chat_logs
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| workflow_id | INTEGER | FOREIGN KEY, NULLABLE | Reference to workflows.id |
| query | TEXT | NOT NULL | User query |
| response | TEXT | NOT NULL | LLM response |
| execution_log | JSON | NULLABLE | Execution details |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

### Relationships
- `Workflow` → `ChatLog` (One-to-Many)
- `Document` → `Embedding` (One-to-Many)

---

## Configuration

### Backend Environment Variables

**File**: `backend/.env`

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIzaSy...
SERPAPI_KEY=...
BRAVE_API_KEY=...

# Server
HOST=0.0.0.0
PORT=8000

# CORS (Production)
ALLOWED_ORIGINS=https://your-frontend.onrender.com,http://localhost:3000

# File Uploads
UPLOAD_DIR=/app/uploads
```

### Frontend Environment Variables

**File**: `frontend/.env` (or Render environment variables)

```env
# API Base URL
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

**Note**: Vite environment variables must be prefixed with `VITE_` and are embedded at build time.

### Vite Configuration (`frontend/vite.config.js`)

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  preview: {
    port: parseInt(process.env.PORT) || 3000,
    host: '0.0.0.0',
    strictPort: false,
    allowedHosts: [
      '.onrender.com' // Allow Render domains
    ]
  }
})
```

---

## Deployment

### Docker Deployment

**Build and Run**:
```bash
docker-compose up --build
```

**Services**:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Database: `localhost:5432`

### Render Deployment

**Configuration File**: `render.yaml`

**Services**:
1. **PostgreSQL Database**: Managed database service
2. **Backend Web Service**: Python/FastAPI service
3. **Frontend Web Service**: Node.js/Vite service

**Environment Variables** (Set in Render Dashboard):
- Backend: `DATABASE_URL`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`, etc.
- Frontend: `VITE_API_BASE_URL`

**Build Commands**:
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install && npm run build`

**Start Commands**:
- Backend: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Frontend: `npm run preview` or `npx vite preview --host 0.0.0.0 --port $PORT`

---

## Code Flow Examples

### Example 1: Document Upload Flow

```
1. User uploads PDF in WorkflowBuilder
   ↓
2. Frontend: POST /api/documents/upload (multipart/form-data)
   ↓
3. Backend: documents.py router receives file
   ↓
4. Save file to disk with UUID filename
   ↓
5. Extract text using PyMuPDF
   ↓
6. Create Document record in database
   ↓
7. Return DocumentResponse immediately
   ↓
8. Background task: Generate embeddings
   ↓
9. Embedding service: Generate embeddings for chunks
   ↓
10. Store embeddings in database
```

### Example 2: Workflow Execution Flow

```
1. User sends query in ChatInterface
   ↓
2. Frontend: POST /api/chat/query
   {
     "query": "What is this file about?",
     "nodes": [...],
     "edges": [...]
   }
   ↓
3. Backend: chat.py router receives request
   ↓
4. WorkflowExecutor.execute_workflow()
   ↓
5. Find User Query node → Extract query
   ↓
6. Find Knowledge Base node → Search documents
   ↓
7. DocumentService.search_documents()
   - Generate query embedding
   - Vector similarity search
   - Return relevant chunks
   ↓
8. Find LLM Engine node → Generate response
   ↓
9. LLMService.generate_response()
   - Build prompt with context
   - Call OpenAI/Gemini API
   - Return response
   ↓
10. Find Output node → Format response
   ↓
11. Return ChatResponse with execution log
   ↓
12. Save ChatLog to database
```

### Example 3: Embedding Generation Flow

```
1. Background task triggered after document upload
   ↓
2. DocumentService.generate_embeddings_for_document()
   ↓
3. Chunk text (max 2 chunks for rate limit avoidance)
   ↓
4. For each chunk:
   ↓
5. EmbeddingService.generate_embeddings()
   ↓
6. Try OpenAI or Google Gemini API
   ↓
7. Clean text (remove NUL bytes, special chars)
   ↓
8. Generate embedding vector
   ↓
9. Store in Embedding table
   ↓
10. Update document metadata (embeddings_status: "completed")
```

---

## Key Algorithms

### 1. Vector Similarity Search

**Implementation**: Cosine similarity using PostgreSQL JSON arrays

**Algorithm**:
1. Generate query embedding
2. Retrieve all document embeddings
3. Calculate cosine similarity for each
4. Sort by similarity score
5. Return top K results

**Fallback**: If no embeddings found, use keyword search

### 2. Workflow Graph Traversal

**Algorithm**: Depth-First Search (DFS) with cycle detection

**Steps**:
1. Build adjacency list from edges
2. Find entry node (User Query)
3. Traverse graph following edges
4. Process each node in order
5. Pass data between nodes via edges
6. Track visited nodes to prevent cycles

### 3. Text Chunking

**Strategy**: Fixed-size chunks with overlap

**Parameters**:
- Max chunks: 2 (to avoid rate limits)
- Chunk size: ~2000 characters
- Overlap: None (simple splitting)

**Future Improvement**: Semantic chunking using sentence boundaries

---

## Error Handling

### Backend Error Handling

**Rate Limits**:
- Retry with exponential backoff
- Graceful degradation (return pending status)
- User-friendly error messages

**API Failures**:
- Model fallback (try alternative models)
- Text-based search fallback
- Error logging with traceback

**File Upload Errors**:
- Validation before processing
- Cleanup on failure
- Detailed error messages

### Frontend Error Handling

**API Errors**:
- Toast notifications for user feedback
- Console logging for debugging
- Graceful UI state management

**Network Errors**:
- Retry logic for failed requests
- Offline state handling
- Error boundaries for React errors

---

## Performance Considerations

### Backend Optimizations

1. **Background Tasks**: Embedding generation doesn't block uploads
2. **Chunk Limiting**: Max 2 chunks per document to avoid rate limits
3. **Database Indexing**: Primary keys and foreign keys indexed
4. **Connection Pooling**: SQLAlchemy connection pool

### Frontend Optimizations

1. **Code Splitting**: Vite automatically splits code
2. **Lazy Loading**: Components loaded on demand
3. **Memoization**: React hooks prevent unnecessary re-renders
4. **Debouncing**: Input debouncing for search queries

---

## Security Considerations

### Current Implementation

1. **CORS**: Configurable allowed origins
2. **File Validation**: PDF file type validation
3. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
4. **XSS**: React automatically escapes content

### Production Recommendations

1. **Authentication**: Add JWT or OAuth
2. **Rate Limiting**: Implement API rate limiting
3. **File Size Limits**: Enforce maximum file sizes
4. **Input Sanitization**: Sanitize user inputs
5. **HTTPS**: Always use HTTPS in production
6. **API Key Security**: Store keys in secure vaults
7. **Database Security**: Use connection encryption

---

## Testing

### Backend Testing (Future)

```python
# Example test structure
def test_workflow_creation():
    # Test workflow CRUD operations
    pass

def test_document_upload():
    # Test PDF upload and processing
    pass

def test_workflow_execution():
    # Test workflow execution flow
    pass
```

### Frontend Testing (Future)

```javascript
// Example test structure
describe('WorkflowBuilder', () => {
  it('should create a workflow', () => {
    // Test workflow creation
  })
  
  it('should upload a document', () => {
    // Test document upload
  })
})
```

---

## Future Enhancements

### Planned Features

1. **User Authentication**: Login/signup system
2. **Workflow Templates**: Pre-built workflow templates
3. **Real-time Collaboration**: Multiple users editing workflows
4. **Advanced Chunking**: Semantic chunking for better context
5. **More LLM Providers**: Anthropic Claude, Cohere, etc.
6. **Workflow Versioning**: Version control for workflows
7. **Analytics Dashboard**: Usage statistics and metrics
8. **Export/Import**: Export workflows as JSON/YAML

### Technical Improvements

1. **Caching**: Redis for embedding cache
2. **Queue System**: Celery for background tasks
3. **Monitoring**: Prometheus + Grafana
4. **Logging**: Structured logging with ELK stack
5. **Testing**: Comprehensive unit and integration tests
6. **Documentation**: API documentation with Swagger/OpenAPI

---

## Troubleshooting

### Common Issues

#### Backend Not Starting
- Check PostgreSQL is running
- Verify DATABASE_URL is correct
- Check port 8000 is available

#### Frontend Not Connecting to Backend
- Verify VITE_API_BASE_URL is set
- Check CORS settings
- Ensure backend is running

#### Document Upload Failing
- Check file is valid PDF
- Verify upload directory exists
- Check file size limits

#### Embeddings Not Generating
- Check API keys are valid
- Verify rate limits not exceeded
- Check background task logs

#### Workflow Execution Errors
- Verify workflow has valid connections
- Check all required components are present
- Review execution log for details

---

## Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

### Code Style

- **Backend**: Follow PEP 8 (Python style guide)
- **Frontend**: Follow ESLint rules
- **Commits**: Use conventional commit messages

---

## License

This project is part of a full-stack engineering assignment.

---

## Contact & Support

For issues, questions, or contributions, please refer to the project repository.

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintained By**: AI Planet Development Team
