# AI Planet - No-Code Workflow Builder Architecture

## System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[React.js Frontend]
        Dashboard[Dashboard Component]
        WorkflowBuilder[Workflow Builder]
        ChatInterface[Chat Interface]
        ComponentLib[Component Library]
        
        UI --> Dashboard
        UI --> WorkflowBuilder
        UI --> ChatInterface
        WorkflowBuilder --> ComponentLib
    end
    
    subgraph "Backend API Layer"
        API[FastAPI Backend]
        WorkflowRouter[Workflows Router]
        DocumentRouter[Documents Router]
        ChatRouter[Chat Router]
        ComponentRouter[Components Router]
        
        API --> WorkflowRouter
        API --> DocumentRouter
        API --> ChatRouter
        API --> ComponentRouter
    end
    
    subgraph "Service Layer"
        WorkflowExecutor[Workflow Executor]
        DocumentService[Document Service]
        EmbeddingService[Embedding Service]
        LLMService[LLM Service]
        
        WorkflowExecutor --> DocumentService
        WorkflowExecutor --> LLMService
        DocumentService --> EmbeddingService
    end
    
    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        DocumentsTable[(Documents Table)]
        WorkflowsTable[(Workflows Table)]
        ChatLogsTable[(Chat Logs Table)]
        EmbeddingsTable[(Embeddings Table)]
        
        PostgreSQL --> DocumentsTable
        PostgreSQL --> WorkflowsTable
        PostgreSQL --> ChatLogsTable
        PostgreSQL --> EmbeddingsTable
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API<br/>GPT Models & Embeddings]
        Gemini[Google Gemini API<br/>Gemini Models & Embeddings]
        SerpAPI[SerpAPI<br/>Web Search]
        PyMuPDF[PyMuPDF<br/>PDF Text Extraction]
    end
    
    subgraph "Storage"
        FileStorage[File Storage<br/>PDF Uploads]
    end
    
    %% Frontend to Backend connections
    Dashboard -->|HTTP REST| API
    WorkflowBuilder -->|HTTP REST| API
    ChatInterface -->|HTTP REST| API
    
    %% Backend to Service connections
    WorkflowRouter --> WorkflowExecutor
    DocumentRouter --> DocumentService
    ChatRouter --> WorkflowExecutor
    
    %% Service to Database connections
    DocumentService --> DocumentsTable
    DocumentService --> EmbeddingsTable
    WorkflowExecutor --> WorkflowsTable
    ChatRouter --> ChatLogsTable
    
    %% Service to External Services
    DocumentService --> PyMuPDF
    EmbeddingService --> OpenAI
    EmbeddingService --> Gemini
    LLMService --> OpenAI
    LLMService --> Gemini
    LLMService --> SerpAPI
    
    %% Storage connections
    DocumentService --> FileStorage
    
    %% Styling
    classDef frontend fill:#61dafb,stroke:#20232a,stroke-width:2px
    classDef backend fill:#009688,stroke:#004d40,stroke-width:2px
    classDef service fill:#ff9800,stroke:#e65100,stroke-width:2px
    classDef database fill:#336791,stroke:#1a2332,stroke-width:2px
    classDef external fill:#9c27b0,stroke:#4a148c,stroke-width:2px
    classDef storage fill:#795548,stroke:#3e2723,stroke-width:2px
    
    class UI,Dashboard,WorkflowBuilder,ChatInterface,ComponentLib frontend
    class API,WorkflowRouter,DocumentRouter,ChatRouter,ComponentRouter backend
    class WorkflowExecutor,DocumentService,EmbeddingService,LLMService service
    class PostgreSQL,DocumentsTable,WorkflowsTable,ChatLogsTable,EmbeddingsTable database
    class OpenAI,Gemini,SerpAPI,PyMuPDF external
    class FileStorage storage
```

## Workflow Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant WorkflowExecutor
    participant DocumentService
    participant LLMService
    participant Database
    participant ExternalAPIs

    User->>Frontend: Build Workflow (Drag & Drop Components)
    Frontend->>Backend: Save Workflow (POST /api/workflows)
    Backend->>Database: Store Workflow Definition
    
    User->>Frontend: Upload PDF Document
    Frontend->>Backend: POST /api/documents/upload
    Backend->>DocumentService: Extract Text (PyMuPDF)
    DocumentService->>ExternalAPIs: Generate Embeddings (OpenAI/Gemini)
    ExternalAPIs-->>DocumentService: Embedding Vectors
    DocumentService->>Database: Store Document + Embeddings
    
    User->>Frontend: Enter Query in Chat
    Frontend->>Backend: POST /api/chat/query
    Backend->>WorkflowExecutor: Execute Workflow
    
    WorkflowExecutor->>WorkflowExecutor: Process User Query Node
    WorkflowExecutor->>DocumentService: Search Documents (Knowledge Base)
    DocumentService->>Database: Vector/Keyword Search
    Database-->>DocumentService: Relevant Chunks
    DocumentService-->>WorkflowExecutor: Context
    
    WorkflowExecutor->>LLMService: Generate Response
    LLMService->>ExternalAPIs: Call LLM (OpenAI/Gemini)
    ExternalAPIs-->>LLMService: AI Response
    LLMService-->>WorkflowExecutor: Final Response
    
    WorkflowExecutor->>Database: Save Chat Log
    WorkflowExecutor-->>Backend: Response + Execution Log
    Backend-->>Frontend: JSON Response
    Frontend-->>User: Display in Chat Interface
```

## Component Architecture

```mermaid
graph LR
    subgraph "Core Components"
        UQ[User Query<br/>Component]
        KB[Knowledge Base<br/>Component]
        LLM[LLM Engine<br/>Component]
        OUT[Output<br/>Component]
    end
    
    subgraph "User Query Flow"
        UQ -->|Query| KB
        UQ -->|Query| LLM
    end
    
    subgraph "Knowledge Base Flow"
        KB -->|Context| LLM
        KB -->|Context| OUT
    end
    
    subgraph "LLM Engine Flow"
        LLM -->|Response| OUT
    end
    
    subgraph "Output Flow"
        OUT -->|Display| User[User Interface]
    end
    
    style UQ fill:#e3f2fd
    style KB fill:#f3e5f5
    style LLM fill:#fff3e0
    style OUT fill:#e8f5e9
```

## Data Flow Diagram

```mermaid
flowchart TD
    Start([User Action]) --> Upload{Action Type?}
    
    Upload -->|Upload PDF| PDF[PDF File]
    PDF --> Extract[Extract Text<br/>PyMuPDF]
    Extract --> Clean[Clean Text<br/>Remove NUL bytes]
    Clean --> Chunk[Chunk Text<br/>3000 chars/chunk]
    Chunk --> Embed[Generate Embeddings<br/>OpenAI/Gemini]
    Embed --> Store[Store in PostgreSQL<br/>Documents + Embeddings]
    
    Upload -->|Build Workflow| Build[Create Workflow]
    Build --> Validate[Validate Workflow]
    Validate --> Save[Save to Database]
    
    Upload -->|Chat Query| Query[User Query]
    Query --> Execute[Execute Workflow]
    Execute --> Search[Search Knowledge Base]
    Search --> Vector{Vector Search<br/>Available?}
    Vector -->|Yes| VectorRes[Vector Results]
    Vector -->|No| Keyword[Keyword Search<br/>Fallback]
    Keyword --> KeywordRes[Keyword Results]
    VectorRes --> Context[Prepare Context]
    KeywordRes --> Context
    Context --> LLM[Call LLM<br/>OpenAI/Gemini]
    LLM --> Response[Generate Response]
    Response --> Log[Save Chat Log]
    Log --> Display[Display to User]
    
    style Start fill:#4caf50
    style Display fill:#4caf50
    style Store fill:#2196f3
    style Save fill:#2196f3
    style Log fill:#2196f3
```

## Technology Stack Overview

```mermaid
mindmap
  root((AI Planet<br/>Workflow Builder))
    Frontend
      React.js
      React Flow
      Vite
      Axios
    Backend
      FastAPI
      Python 3.13
      SQLAlchemy
      Pydantic
    Database
      PostgreSQL
      Vector Storage
      Document Metadata
    External APIs
      OpenAI
        GPT Models
        Embeddings
      Google Gemini
        Gemini Models
        Embeddings
      SerpAPI
        Web Search
    Tools
      PyMuPDF
        PDF Extraction
      Docker
        Containerization
```

---

## Architecture Components Description

### **Frontend Layer (React.js)**
- **Dashboard**: Displays saved workflows/stacks
- **Workflow Builder**: Visual canvas for building workflows using React Flow
- **Chat Interface**: Interactive chat for querying workflows
- **Component Library**: Sidebar with draggable components

### **Backend Layer (FastAPI)**
- **Workflows Router**: CRUD operations for workflows
- **Documents Router**: PDF upload and document management
- **Chat Router**: Query execution and chat history
- **Components Router**: Component type definitions

### **Service Layer**
- **Workflow Executor**: Orchestrates workflow execution based on node connections
- **Document Service**: Handles PDF processing, text extraction, and search
- **Embedding Service**: Generates embeddings using OpenAI/Gemini
- **LLM Service**: Manages LLM interactions with fallback mechanisms

### **Data Layer (PostgreSQL)**
- **Documents Table**: Stores document metadata and content
- **Workflows Table**: Stores workflow definitions (nodes, edges)
- **Chat Logs Table**: Stores conversation history
- **Embeddings Table**: Stores vector embeddings for semantic search

### **External Services**
- **OpenAI API**: GPT models and text embeddings
- **Google Gemini API**: Gemini models and embeddings
- **SerpAPI**: Web search functionality
- **PyMuPDF**: PDF text extraction

---

## Key Features

1. **No-Code Workflow Builder**: Visual drag-and-drop interface
2. **Intelligent Document Processing**: PDF extraction with embedding generation
3. **Multi-LLM Support**: OpenAI and Google Gemini with automatic fallback
4. **Fail-Safe Search**: Vector search with keyword fallback
5. **Real-time Execution Logs**: Detailed workflow execution tracking
6. **Chat History Persistence**: All conversations saved in database

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        
        subgraph "Frontend Container"
            FE[React App<br/>Port 3000/5173]
        end
        
        subgraph "Backend Container"
            BE[FastAPI<br/>Port 8001]
        end
        
        subgraph "Database Container"
            DB[(PostgreSQL<br/>Port 5432)]
        end
        
        LB --> FE
        FE --> BE
        BE --> DB
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
        Gemini[Google Gemini API]
        SerpAPI[SerpAPI]
    end
    
    BE --> OpenAI
    BE --> Gemini
    BE --> SerpAPI
    
    style FE fill:#61dafb
    style BE fill:#009688
    style DB fill:#336791
```

---

*This architecture diagram represents the complete system design of the AI Planet No-Code Workflow Builder application.*
