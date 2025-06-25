from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
import os
import openai
from dotenv import load_dotenv

from embedding import EmbeddingManager
from vector_store import VectorStore
from document_handler import DocumentHandler

load_dotenv()

app = FastAPI(title="RAG Document Bot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
embedding_manager = EmbeddingManager()
vector_store = VectorStore()
document_handler = DocumentHandler()

# Pydantic models
class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    answer: str
    sources: List[dict]

class DocumentResponse(BaseModel):
    id: str
    filename: str
    chunk_count: int
    uploaded_at: str

@app.get("/")
def root():
    return {"message": "RAG Document Bot API", "version": "1.0.0"}

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        allowed_extensions = ['pdf', 'docx', 'txt']
        file_extension = file.filename.lower().split('.')[-1]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process document
        chunks = document_handler.process_document(file_content, file.filename)
        if not chunks:
            raise HTTPException(status_code=400, detail="Failed to extract text from document")
        
        # Generate embeddings
        embeddings = embedding_manager.get_embeddings(chunks)
        if not embeddings:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings")
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Add to vector store
        success = vector_store.add_document(doc_id, file.filename, chunks, embeddings)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to store document")
        
        return {
            "message": "Document uploaded successfully",
            "document_id": doc_id,
            "filename": file.filename,
            "chunk_count": len(chunks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/ask")
async def ask_question(request: AskRequest):
    """Ask a question and get an answer using RAG"""
    try:
        # Generate query embedding
        query_embedding = embedding_manager.get_embedding(request.query)
        if not query_embedding:
            raise HTTPException(status_code=500, detail="Failed to generate query embedding")
        
        # Search for relevant chunks
        search_results = vector_store.search(query_embedding, k=5)
        if not search_results:
            return {
                "answer": "I don't have any documents to search through. Please upload some documents first.",
                "sources": []
            }
        
        # Prepare context from search results
        context = "\n\n".join([result["chunk_text"] for result in search_results])
        
        # Generate answer using OpenAI
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on the provided context. Only use information from the context to answer questions. If the context doesn't contain enough information to answer the question, say so."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {request.query}\n\nAnswer based on the context above:"
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            # Prepare sources
            sources = []
            for result in search_results:
                sources.append({
                    "filename": result["filename"],
                    "chunk_text": result["chunk_text"][:200] + "..." if len(result["chunk_text"]) > 200 else result["chunk_text"],
                    "relevance_score": 1.0 - result["distance"]  # Convert distance to similarity score
                })
            
            return {
                "answer": answer,
                "sources": sources
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate answer: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/documents")
async def get_documents():
    """Get list of uploaded documents"""
    try:
        documents = vector_store.get_documents()
        return {
            "documents": documents,
            "total_documents": vector_store.get_document_count(),
            "total_chunks": vector_store.get_chunk_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its vectors"""
    try:
        success = vector_store.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)