from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from dotenv import load_dotenv
import uvicorn

from services.pdf_extractor import extract_text_from_pdf
from services.url_scraper import scrape_url_content
from services.vector_store import VectorStore
from services.rag_service import RAGService

load_dotenv()

app = FastAPI(title="RAG Chatbot API")

# CORS middleware
# Allow origins from environment variable or default to all for development
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_str == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
vector_store = VectorStore()
rag_service = RAGService(vector_store)

# Request models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class URLRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name
        
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(temp_path)
            
            if not text or len(text.strip()) < 10:
                raise HTTPException(status_code=400, detail="Could not extract meaningful text from PDF")
            
            # Store in vector database
            doc_id = await vector_store.add_document(text, metadata={"source": file.filename, "type": "pdf"})
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return JSONResponse({
            "success": True,
            "message": "PDF processed successfully",
            "doc_id": doc_id,
            "text_length": len(text)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/scrape-url")
async def scrape_url(request: URLRequest):
    """Scrape content from a URL"""
    try:
        # Scrape content from URL
        content = scrape_url_content(request.url)
        
        if not content or len(content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract meaningful content from URL")
        
        # Store in vector database
        doc_id = await vector_store.add_document(content, metadata={"source": request.url, "type": "url"})
        
        return JSONResponse({
            "success": True,
            "message": "URL scraped and processed successfully",
            "doc_id": doc_id,
            "text_length": len(content)
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/chat")
async def chat(message: ChatMessage):
    """Chat endpoint with RAG"""
    try:
        if not message.message or len(message.message.strip()) < 1:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get response from RAG service
        response = await rag_service.query(message.message, session_id=message.session_id)
        
        return JSONResponse({
            "success": True,
            "response": response["answer"],
            "sources": response.get("sources", []),
            "session_id": response.get("session_id")
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/api/documents")
async def get_documents():
    """Get list of all documents in the database"""
    try:
        documents = await vector_store.list_documents()
        return JSONResponse({
            "success": True,
            "documents": documents
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document from the database"""
    try:
        success = await vector_store.delete_document(doc_id)
        if success:
            return JSONResponse({"success": True, "message": "Document deleted"})
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    # Get port from environment variable (Railway provides this) or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

