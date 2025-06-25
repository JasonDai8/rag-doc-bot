import faiss
import numpy as np
import pickle
import os
from typing import List, Tuple, Dict, Any
import uuid
from datetime import datetime

class VectorStore:
    def __init__(self, index_path: str = "vector_store"):
        self.index_path = index_path
        self.index = None
        self.documents = {}  # Store document metadata
        self.chunk_to_doc = {}  # Map chunk IDs to document IDs
        self.chunk_texts = {}  # Map chunk indices to actual text
        self.load_index()
    
    def load_index(self):
        """Load existing FAISS index and metadata"""
        try:
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                with open(f"{self.index_path}.pkl", "rb") as f:
                    data = pickle.load(f)
                    self.documents = data.get("documents", {})
                    self.chunk_to_doc = data.get("chunk_to_doc", {})
                    self.chunk_texts = data.get("chunk_texts", {})
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(1536)  # OpenAI ada-002 embedding dimension
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = faiss.IndexFlatL2(1536)
    
    def save_index(self):
        """Save FAISS index and metadata"""
        try:
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            with open(f"{self.index_path}.pkl", "wb") as f:
                pickle.dump({
                    "documents": self.documents,
                    "chunk_to_doc": self.chunk_to_doc,
                    "chunk_texts": self.chunk_texts
                }, f)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def add_document(self, doc_id: str, filename: str, chunks: List[str], embeddings: List[List[float]]) -> bool:
        """Add document chunks to the vector store"""
        try:
            if not embeddings:
                return False
            
            # Convert embeddings to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Get starting index before adding
            start_idx = self.index.ntotal
            
            # Add to FAISS index
            self.index.add(embeddings_array)
            
            # Store document metadata
            self.documents[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "chunk_count": len(chunks),
                "uploaded_at": datetime.now().isoformat(),
                "chunks": chunks
            }
            
            # Map chunk indices to document ID and store chunk texts
            for i, chunk_text in enumerate(chunks):
                chunk_idx = start_idx + i
                self.chunk_to_doc[chunk_idx] = doc_id
                self.chunk_texts[chunk_idx] = chunk_text
            
            self.save_index()
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            if self.index.ntotal == 0:
                return []
            
            query_array = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx in self.chunk_to_doc and idx in self.chunk_texts:
                    doc_id = self.chunk_to_doc[idx]
                    doc_info = self.documents.get(doc_id, {})
                    results.append({
                        "chunk_index": int(idx),
                        "distance": float(distance),
                        "chunk_text": self.chunk_texts[idx],
                        "document_id": doc_id,
                        "filename": doc_info.get("filename", "Unknown")
                    })
            
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and its chunks from the vector store"""
        try:
            if doc_id not in self.documents:
                return False
            
            # Remove document metadata
            del self.documents[doc_id]
            
            # Remove chunk mappings and texts
            indices_to_remove = [idx for idx, stored_doc_id in self.chunk_to_doc.items() if stored_doc_id == doc_id]
            for idx in indices_to_remove:
                del self.chunk_to_doc[idx]
                if idx in self.chunk_texts:
                    del self.chunk_texts[idx]
            
            self.save_index()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Get list of all documents"""
        return list(self.documents.values())
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        return len(self.documents)
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks"""
        return self.index.ntotal if self.index else 0 