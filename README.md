# AI Planet - No-Code Workflow Builder

A full-stack No-Code/Low-Code web application that enables users to visually create and interact with intelligent workflows. Users can configure a flow of components that handle user input, extract knowledge from documents, interact with language models, and return answers through a chat interface.

## 🎯 Features

- **Visual Workflow Builder**: Drag-and-drop interface using React Flow
- **Four Core Components**:
  - **User Query**: Entry point for user queries
  - **Knowledge Base**: Document upload, text extraction, and vector search
  - **LLM Engine**: Integration with OpenAI GPT and Google Gemini
  - **Output**: Chat interface for displaying responses
- **Document Processing**: PDF text extraction and embedding generation
- **Vector Search**: Semantic search using embeddings stored in PostgreSQL
- **Multiple LLM Support**: OpenAI GPT and Google Gemini
- **Web Search Integration**: Optional SerpAPI and Brave Search integration
- **Workflow Execution**: Dynamic workflow execution based on user-defined connections
- **Chat Interface**: Interactive chat for querying workflows

## 🛠️ Tech Stack

### Frontend
- **React.js** with Vite
- **React Flow** for workflow visualization
- **Axios** for API calls
- **React Hot Toast** for notifications

### Backend
- **FastAPI** for REST API
- **PostgreSQL** for database
- **SQLAlchemy** for ORM
- **PyMuPDF** for PDF text extraction
- **OpenAI** for embeddings and LLM
- **Google Generative AI** for Gemini support
- **SerpAPI/Brave Search** for web search

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- PostgreSQL (if running without Docker)
- API Keys:
  - OpenAI API Key
  - Google API Key (for Gemini)
  - SerpAPI Key (optional, for web search)
  - Brave API Key (optional, alternative to SerpAPI)

## 📚 Additional Documentation

- **IMPLEMENTATION-STATUS.md** - Detailed implementation status report

## 🚀 Quick Start with Docker (Recommended)

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Run setup script** (optional, creates .env file):
   ```bash
   # Linux/Mac
   chmod +x setup.sh && ./setup.sh
   
   # Windows
   setup.bat
   ```

3. **Create environment file** (if not done by setup script):
   ```bash
   cp backend/.env.example backend/.env
   ```

4. **Edit `backend/.env`** and add your API keys:
   ```env
   DATABASE_URL=postgresql://postgres:postgres@db:5432/aiplanet
   OPENAI_API_KEY=your_openai_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   SERPAPI_API_KEY=your_serpapi_key_here
   BRAVE_API_KEY=your_brave_api_key_here
   ```

5. **Start all services** (Docker will install all dependencies automatically):
   ```bash
   docker-compose up --build
   ```

6. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🏃 Local Development (Without Docker)

### Option 1: Automatic Installation

Run the installation script:
```bash
# Linux/Mac
chmod +x install.sh && ./install.sh

# Windows
install.bat
```

### Option 2: Manual Installation

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Start PostgreSQL** (if not using Docker):
   ```bash
   # Using Docker
   docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=aiplanet -p 5432:5432 postgres:15
   ```

6. **Run database migrations** (tables are auto-created on first run):
   ```bash
   # The application will create tables automatically
   ```

7. **Start the backend server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend should be running on http://localhost:8000

## 📁 Project Structure

```
Ai-planet/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py           # Database configuration
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── schemas.py            # Pydantic schemas
│   │   ├── routers/              # API routes
│   │   │   ├── workflows.py
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   └── components.py
│   │   └── services/             # Business logic
│   │       ├── document_service.py
│   │       ├── embedding_service.py
│   │       ├── llm_service.py
│   │       └── workflow_executor.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorkflowBuilder.jsx
│   │   │   ├── ComponentLibrary.jsx
│   │   │   ├── ComponentConfigPanel.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   └── DocumentUpload.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

## 🎮 Usage Guide

### Building a Workflow

1. **Upload Documents**:
   - Click on the document upload area in the component library
   - Upload PDF files that will be used as knowledge base

2. **Add Components**:
   - Drag components from the library panel to the canvas
   - Available components:
     - **User Query**: Entry point (required)
     - **Knowledge Base**: Document search (optional)
     - **LLM Engine**: AI response generation (required)
     - **Output**: Display results (required)

3. **Connect Components**:
   - Click and drag from a component's output to another component's input
   - Typical flow: User Query → Knowledge Base → LLM Engine → Output

4. **Configure Components**:
   - Click on a component to open the configuration panel
   - Configure:
     - **Knowledge Base**: Select documents and set top_k
     - **LLM Engine**: Choose provider (OpenAI/Gemini), model, custom prompt, web search

5. **Build Stack**:
   - Click "Build Stack" button to validate and save the workflow

### Chatting with Your Workflow

1. **Open Chat Interface**:
   - Click "Chat with Stack" button after building a workflow

2. **Ask Questions**:
   - Type your question in the chat input
   - The system will execute the workflow and return a response

3. **View Execution Logs**:
   - Expand "Execution Log" in chat messages to see workflow execution details

## 🔌 API Endpoints

### Workflows
- `POST /api/workflows` - Create a workflow
- `GET /api/workflows` - Get all workflows
- `GET /api/workflows/{id}` - Get a specific workflow
- `PUT /api/workflows/{id}` - Update a workflow
- `DELETE /api/workflows/{id}` - Delete a workflow

### Documents
- `POST /api/documents/upload` - Upload a document
- `GET /api/documents` - Get all documents
- `GET /api/documents/{id}` - Get a specific document
- `DELETE /api/documents/{id}` - Delete a document
- `POST /api/documents/search` - Search documents

### Chat
- `POST /api/chat/query` - Execute workflow and get response
- `GET /api/chat/logs` - Get chat logs
- `GET /api/chat/logs/{id}` - Get a specific chat log

### Components
- `GET /api/components/types` - Get available component types

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest  # If tests are added
```

### Frontend Testing
```bash
cd frontend
npm test  # If tests are added
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/aiplanet
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
SERPAPI_API_KEY=your_key_here
BRAVE_API_KEY=your_key_here
HOST=0.0.0.0
PORT=8000
```

## 🔧 Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database credentials

### API Key Issues
- Ensure all required API keys are set in .env
- Check API key validity and quotas

### Frontend Not Connecting to Backend
- Verify backend is running on port 8000
- Check CORS settings in backend/main.py
- Verify API_BASE_URL in frontend components

### Document Upload Issues
- Ensure uploads directory exists and has write permissions
- Check file size limits
- Verify PDF file format

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database**: Use managed PostgreSQL service
3. **File Storage**: Consider cloud storage for documents
4. **API Keys**: Rotate keys regularly
5. **HTTPS**: Enable SSL/TLS
6. **Rate Limiting**: Implement rate limiting for API endpoints
7. **Monitoring**: Set up logging and monitoring

### Kubernetes Deployment (Optional)

Kubernetes manifests can be created for production deployment. Refer to Kubernetes documentation for setting up:
- Deployments
- Services
- ConfigMaps
- Secrets
- PersistentVolumes

## 📊 Architecture Diagram

```
┌─────────────┐
│   Frontend  │
│   (React)   │
└──────┬──────┘
       │
       │ HTTP/REST
       │
┌──────▼──────┐
│   Backend   │
│  (FastAPI)  │
└──────┬──────┘
       │
       ├──────────┬──────────┬──────────┐
       │          │          │          │
┌──────▼──┐  ┌───▼────┐  ┌───▼────┐  ┌─▼──────┐
│PostgreSQL│  │ OpenAI │  │ Gemini │  │SerpAPI│
│          │  │        │  │        │  │       │
└──────────┘  └────────┘  └────────┘  └───────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of a full-stack engineering assignment.

## 👥 Authors

Developed as part of the AI Planet assignment.

## 🙏 Acknowledgments

- React Flow for workflow visualization
- FastAPI for the excellent Python framework
- OpenAI and Google for LLM APIs
