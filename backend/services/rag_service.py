import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import requests
import uuid

load_dotenv()

# Try to import Groq SDK, fallback to requests if not available
try:
    from groq import Groq
    GROQ_SDK_AVAILABLE = True
except ImportError:
    GROQ_SDK_AVAILABLE = False

class RAGService:
    def __init__(self, vector_store):
        """Initialize RAG service with vector store"""
        self.vector_store = vector_store
        self.use_groq = os.getenv("USE_GROQ", "true").lower() == "true"
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
        
        # Initialize Groq client if SDK is available and API key is set
        if GROQ_SDK_AVAILABLE and self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Groq client: {e}")
                self.groq_client = None
        else:
            self.groq_client = None
        
        # Groq API endpoint (fallback for direct HTTP calls)
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Hugging Face Inference API endpoint (using a free model)
        self.hf_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3-8b-chat-hf"
    
    def _format_context(self, results: List[Dict]) -> str:
        """Format retrieved chunks into context string"""
        if not results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            text = result.get("text", "")
            source = result.get("metadata", {}).get("source", "Unknown")
            context_parts.append(f"[Source {i}: {source}]\n{text}")
        
        return "\n\n".join(context_parts)
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API for LLM inference"""
        if not self.groq_api_key:
            raise Exception("GROQ_API_KEY not set")
        
        # Use Groq SDK if available (preferred method)
        if GROQ_SDK_AVAILABLE and self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on the provided context. If the context doesn't contain enough information, say so."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    model="llama-3.1-8b-instant",  # Updated to current model name
                    temperature=0.7,
                    max_tokens=1024
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                raise Exception(f"Groq API error: {str(e)}")
        
        # Fallback to direct HTTP request
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on the provided context. If the context doesn't contain enough information, say so."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "llama-3.1-8b-instant",  # Updated to current model name
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        response = requests.post(self.groq_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _call_huggingface(self, prompt: str) -> str:
        """Call Hugging Face Inference API for LLM inference"""
        if not self.hf_api_key:
            raise Exception("HUGGINGFACE_API_KEY not set")
        
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        response = requests.post(self.hf_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list) and len(result) > 0:
            if "generated_text" in result[0]:
                return result[0]["generated_text"]
            elif "summary_text" in result[0]:
                return result[0]["summary_text"]
        
        return str(result)
    
    async def query(self, question: str, session_id: Optional[str] = None) -> Dict:
        """
        Process a query using RAG pipeline
        
        Args:
            question: User's question
            session_id: Optional session ID for conversation tracking
            
        Returns:
            Dictionary with answer, sources, and session_id
        """
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Retrieve relevant chunks - get more results to ensure diversity across document types
        results = await self.vector_store.search(question, n_results=10)
        
        # Format context
        context = self._format_context(results)
        
        # Create prompt
        prompt = f"""Based on the following context, please answer the question. If the context doesn't contain enough information to answer the question, please say so.

Context:
{context}

Question: {question}

Answer:"""
        
        # Get LLM response
        try:
            if self.use_groq and self.groq_api_key:
                answer = self._call_groq(prompt)
            elif self.hf_api_key:
                answer = self._call_huggingface(prompt)
            else:
                # Fallback: return context-based answer
                answer = f"Based on the retrieved context:\n\n{context}\n\nHowever, LLM API is not configured. Please set GROQ_API_KEY or HUGGINGFACE_API_KEY in your .env file."
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages
            if "404" in error_msg or "Not Found" in error_msg:
                if self.use_groq:
                    answer = f"Error: Groq API endpoint or model not found. Please check:\n1. Your GROQ_API_KEY is correct in the .env file\n2. The API key has proper permissions\n\nRetrieved context:\n\n{context[:500]}..." if len(context) > 500 else f"Retrieved context:\n\n{context}"
                else:
                    answer = f"Error: API endpoint not found. Please check your API configuration.\n\nRetrieved context:\n\n{context[:500]}..." if len(context) > 500 else f"Retrieved context:\n\n{context}"
            elif "401" in error_msg or "Unauthorized" in error_msg:
                answer = f"Error: Invalid API key. Please check your GROQ_API_KEY or HUGGINGFACE_API_KEY in the .env file.\n\nRetrieved context:\n\n{context[:500]}..." if len(context) > 500 else f"Retrieved context:\n\n{context}"
            else:
                answer = f"Error generating response: {error_msg}\n\nRetrieved context:\n\n{context[:500]}..." if len(context) > 500 else f"Retrieved context:\n\n{context}"
        
        # Extract sources
        sources = []
        seen_sources = set()
        for result in results:
            source = result.get("metadata", {}).get("source", "Unknown")
            if source not in seen_sources:
                sources.append(source)
                seen_sources.add(source)
        
        return {
            "answer": answer,
            "sources": sources,
            "session_id": session_id
        }

