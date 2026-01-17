import os
import fitz  # PyMuPDF
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Document, Embedding
from app.services.embedding_service import EmbeddingService
import json

class DocumentService:
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))
        os.makedirs(self.upload_dir, exist_ok=True)
        self.embedding_service = EmbeddingService()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                # Extract text with flags to avoid problematic characters
                page_text = page.get_text("text", flags=11)  # flags=11 removes some control chars
                text += page_text
            doc.close()
            
            # Ultra-aggressive text cleaning: Remove ALL problematic characters
            # Google API doesn't accept NUL (0x00) characters
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            
            # Method 1: Remove null bytes using regex
            import re
            text = re.sub(r'\x00+', '', text)  # Remove all null bytes
            text = text.replace('\x00', '').replace('\0', '').replace('\u0000', '')
            text = text.replace(chr(0), '')  # Remove null character
            
            # Method 2: Filter out control characters (keep only printable + newline/tab)
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            
            # Method 3: Replace carriage returns
            text = text.replace('\r', ' ')
            
            # Method 4: UTF-8 encoding/decoding to remove invalid sequences
            text = text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            # Method 5: Normalize whitespace
            text = ' '.join(text.split())
            text = text.strip()
            
            # Final validation: ensure no null bytes
            if '\x00' in text or '\0' in text or chr(0) in text:
                print("WARNING: Text still contains null bytes after cleaning, applying final fix...")
                text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
                text = text.replace('\x00', '').replace('\0', '')
            
            # Validate text is not empty
            if not text or len(text.strip()) == 0:
                raise ValueError("PDF contains no extractable text")
            
            print(f"Extracted {len(text)} characters from PDF (cleaned, no null bytes)")
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def process_document(self, db: Session, file_path: str, filename: str, file_size: int) -> Document:
        """Process uploaded document: extract text, generate embeddings, and store"""
        print(f"Processing document: {filename}")
        
        try:
            # Extract text
            print("Step 1: Extracting text from PDF...")
            text = self.extract_text_from_pdf(file_path)
            print(f"Text extracted: {len(text)} characters")
            
            # Final cleaning before database storage
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            text = text.replace('\x00', '').replace('\0', '').replace('\u0000', '')
            text = text.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Create document record FIRST (so upload succeeds even if embeddings fail)
            print("Step 2: Saving document to database...")
            doc_pages = len(fitz.open(file_path))
            document = Document(
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                content=text,
                file_metadata={"pages": doc_pages}
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            print(f"Document saved with ID: {document.id}")
            
            # Generate embeddings and store (this might fail due to rate limits, but document is already saved)
            try:
                print("Step 3: Generating embeddings...")
                chunks = self._chunk_text(text)
                print(f"Created {len(chunks)} chunks")
                
                embeddings = self.embedding_service.generate_embeddings(chunks)
                print(f"Generated {len(embeddings)} embeddings")
                
                for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    embedding_record = Embedding(
                        document_id=document.id,
                        chunk_text=chunk,
                        embedding_vector=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                        chunk_index=idx
                    )
                    db.add(embedding_record)
                
                db.commit()
                print("Embeddings saved successfully!")
            except Exception as emb_error:
                # Embedding generation failed, but document is already saved
                print(f"WARNING: Embedding generation failed: {str(emb_error)}")
                print("Document uploaded successfully, but embeddings not generated.")
                # Don't raise error - document is saved, embeddings can be generated later
                # Just log the error
                import traceback
                traceback.print_exc()
            
            return document
            
        except Exception as e:
            print(f"ERROR in process_document: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def generate_embeddings_for_document(self, document_id: int, text: str) -> None:
        """Generate embeddings in background without blocking upload."""
        db = SessionLocal()
        try:
            # Final cleaning before embeddings
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='ignore')
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
            text = text.replace('\x00', '').replace('\0', '').replace('\u0000', '')
            text = text.encode('utf-8', errors='ignore').decode('utf-8')

            chunks = self._chunk_text(text)
            if not chunks:
                print(f"No chunks generated for document {document_id}. Skipping embeddings.")
                return

            embeddings = self.embedding_service.generate_embeddings(chunks)
            if not embeddings:
                print(f"No embeddings generated for document {document_id}.")
                return

            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                embedding_record = Embedding(
                    document_id=document_id,
                    chunk_text=chunk,
                    embedding_vector=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                    chunk_index=idx
                )
                db.add(embedding_record)

            db.commit()
            print(f"Embeddings saved for document {document_id}.")
        except Exception as e:
            print(f"Background embedding generation failed for document {document_id}: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    def _chunk_text(self, text: str, chunk_size: int = 3000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap"""
        # Aggressive cleaning before chunking
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        text = text.replace('\x00', '').replace('\0', '').replace('\u0000', '')
        text = text.strip()
        
        # Larger chunks = fewer API calls
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            
            # Aggressive chunk cleaning: remove ALL problematic characters
            if isinstance(chunk, bytes):
                chunk = chunk.decode('utf-8', errors='ignore')
            chunk = ''.join(char for char in chunk if ord(char) >= 32 or char in '\n\t')
            chunk = chunk.replace('\x00', '').replace('\0', '').replace('\u0000', '')
            chunk = chunk.encode('utf-8', errors='ignore').decode('utf-8')
            chunk = chunk.strip()
            
            if chunk and len(chunk) > 10:  # Only add non-empty chunks with minimum length
                # Final validation: ensure no null bytes
                if '\x00' not in chunk and '\0' not in chunk:
                    chunks.append(chunk)
                else:
                    print(f"Warning: Chunk still contains null bytes, skipping...")
            start = end - overlap
        
        # Limit to max 2 chunks to avoid rate limits (safer)
        if len(chunks) > 2:
            print(f"Warning: Limiting chunks from {len(chunks)} to 2 to avoid rate limits")
            chunks = chunks[:2]
        
        if len(chunks) == 0:
            raise ValueError("No valid text chunks could be created from PDF")
        
        print(f"Created {len(chunks)} chunks from document (total {sum(len(c) for c in chunks)} chars)")
        return chunks
    
    def search_documents(self, db: Session, query: str, top_k: int = 5) -> List[Dict]:
        """Extremely robust search that almost always returns results if documents exist"""
        query_lower = query.lower()
        print(f"[DEBUG] Searching for: '{query_lower}'")
        
        # 1. Get all documents
        documents = db.query(Document).filter(Document.content.isnot(None)).all()
        if not documents:
            print("[DEBUG] No documents with content found in DB")
            return []

        # 2. If it's a general question or summary request, just return the latest document
        summary_keywords = ["summarize", "about", "what", "tell", "file", "document", "everything", "context", "who"]
        is_general = any(word in query_lower for word in summary_keywords) or len(query_lower) < 10
        
        if is_general:
            latest_doc = documents[-1] # Get most recent upload
            print(f"[DEBUG] General query detected. Returning latest doc: {latest_doc.filename}")
            return [{
                "document_id": latest_doc.id,
                "chunk_text": latest_doc.content[:4000], # Give a large chunk
                "similarity": 1.0,
                "chunk_index": 0
            }]

        # 3. Keyword matching
        results = []
        query_words = [w for w in query_lower.split() if len(w) > 3]
        
        for doc in documents:
            content_lower = doc.content.lower()
            matches = [w for w in query_words if w in content_lower]
            
            if matches:
                score = len(matches) / len(query_words) if query_words else 0.5
                # Extract context around first match
                idx = content_lower.find(matches[0])
                start = max(0, idx - 500)
                end = min(len(doc.content), idx + 2500)
                
                results.append({
                    "document_id": doc.id,
                    "chunk_text": doc.content[start:end],
                    "similarity": score,
                    "chunk_index": 0
                })
        
        # 4. If still no matches, but documents exist, just return the latest doc as fallback
        if not results:
            latest_doc = documents[-1]
            print(f"[DEBUG] No keyword matches. Falling back to latest doc: {latest_doc.filename}")
            results.append({
                "document_id": latest_doc.id,
                "chunk_text": latest_doc.content[:3000],
                "similarity": 0.1,
                "chunk_index": 0
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import numpy as np
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
