from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import workflows, documents, chat, components

# Create database tables (only if database is available)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not create database tables: {e}")
    print("Please ensure PostgreSQL is running on port 5432")

app = FastAPI(
    title="AI Planet - No-Code Workflow Builder",
    description="A No-Code/Low-Code web application for building intelligent workflows",
    version="1.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(components.router, prefix="/api/components", tags=["components"])

@app.get("/")
async def root():
    return {"message": "AI Planet API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
