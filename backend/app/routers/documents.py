from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
import traceback
import fitz  # PyMuPDF
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse
from app.services.document_service import DocumentService
from typing import List
import os

router = APIRouter()
document_service = DocumentService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Upload and process a document"""
    print(f"Upload request received for file: {file.filename}")
    try:
        debug_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "upload_debug.log")
        with open(debug_log, "a", encoding="utf-8") as log_file:
            log_file.write(f"UPLOAD_START: {file.filename}\\n")
    except Exception:
        pass
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique filename to avoid conflicts
    import uuid
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(document_service.upload_dir, unique_filename)
    
    try:
        # Save file first
        print(f"Saving file to: {file_path}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        file_size = len(content)
        print(f"File saved successfully. Size: {file_size} bytes")
        
        # Extract text and save document first
        print("Extracting text and saving document...")
        text = document_service.extract_text_from_pdf(file_path)
        doc_pages = len(fitz.open(file_path))
        document = Document(
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            content=text,
            file_metadata={"pages": doc_pages, "embeddings_status": "pending"}
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        print(f"Document saved successfully. ID: {document.id}")
        
        # Generate embeddings in the background (won't block upload)
        if background_tasks is not None:
            background_tasks.add_task(
                document_service.generate_embeddings_for_document,
                document.id,
                text
            )
        
        # Convert file_metadata to metadata for response
        response_data = {
            "id": document.id,
            "filename": document.filename,
            "file_size": document.file_size,
            "file_metadata": document.file_metadata,
            "created_at": document.created_at
        }
        print("Upload completed successfully!")
        return DocumentResponse(**response_data)
        
    except ValueError as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Document upload error (400): {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_msg = str(e)
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        print(f"Document upload error (500): {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("", response_model=List[DocumentResponse])
async def get_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    documents = db.query(Document).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}

@router.post("/search")
async def search_documents(
    query: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):
    """Search documents using vector similarity"""
    results = document_service.search_documents(db, query, top_k)
    return {"query": query, "results": results}
