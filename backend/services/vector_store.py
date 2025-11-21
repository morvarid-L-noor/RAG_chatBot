import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self):
        """Initialize ChromaDB and embedding model"""
        # Get database path from environment or use default
        db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding model (lazy load)
        self._embedding_model = None
    
    @property
    def embedding_model(self):
        """Lazy load embedding model"""
        if self._embedding_model is None:
            print("Loading embedding model... (this may take a moment on first run)")
            self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Embedding model loaded!")
        return self._embedding_model
    
    def _chunk_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
        
        return chunks
    
    async def add_document(self, text: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the vector store
        
        Args:
            text: Document text
            metadata: Optional metadata dictionary
            
        Returns:
            Document ID
        """
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Chunk the text
        chunks = self._chunk_text(text)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks).tolist()
        
        # Prepare metadata for each chunk
        chunk_metadata = []
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            
            chunk_meta = metadata.copy() if metadata else {}
            chunk_meta["chunk_index"] = i
            chunk_meta["doc_id"] = doc_id
            chunk_metadata.append(chunk_meta)
        
        # Add to ChromaDB
        self.collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadata
        )
        
        return doc_id
    
    async def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar documents with diversity across document types
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()[0]
        
        # Get more results than needed to ensure diversity
        search_limit = max(n_results * 2, 20)  # Get at least 2x the requested results
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=search_limit
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            all_results = []
            for i in range(len(results['documents'][0])):
                all_results.append({
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
            
            # Ensure diversity: prioritize results from different document types and sources
            seen_doc_ids = set()
            seen_types = set()
            formatted_results = []
            
            # First pass: add one result from each unique document
            for result in all_results:
                doc_id = result.get("metadata", {}).get("doc_id")
                doc_type = result.get("metadata", {}).get("type")
                
                if doc_id not in seen_doc_ids:
                    formatted_results.append(result)
                    seen_doc_ids.add(doc_id)
                    if doc_type:
                        seen_types.add(doc_type)
                    
                    if len(formatted_results) >= n_results:
                        break
            
            # Second pass: fill remaining slots with best remaining results
            if len(formatted_results) < n_results:
                for result in all_results:
                    if result not in formatted_results:
                        formatted_results.append(result)
                        if len(formatted_results) >= n_results:
                            break
            
            # If still not enough, add remaining results
            if len(formatted_results) < n_results:
                for result in all_results:
                    if result not in formatted_results:
                        formatted_results.append(result)
                        if len(formatted_results) >= n_results:
                            break
        
        return formatted_results
    
    async def list_documents(self) -> List[Dict]:
        """List all unique documents in the store"""
        # Get all items
        all_items = self.collection.get()
        
        # Group by doc_id
        doc_map = {}
        for i, metadata in enumerate(all_items.get('metadatas', [])):
            doc_id = metadata.get('doc_id')
            if doc_id and doc_id not in doc_map:
                doc_map[doc_id] = {
                    "doc_id": doc_id,
                    "source": metadata.get('source', 'Unknown'),
                    "type": metadata.get('type', 'Unknown')
                }
        
        return list(doc_map.values())
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document and all its chunks
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Get all items with this doc_id
        all_items = self.collection.get()
        
        ids_to_delete = []
        for i, metadata in enumerate(all_items.get('metadatas', [])):
            if metadata.get('doc_id') == doc_id:
                ids_to_delete.append(all_items['ids'][i])
        
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            return True
        
        return False

