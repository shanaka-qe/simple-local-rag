"""
Configuration for Local RAG Solution
"""

import os
from pathlib import Path


class Settings:
    """Simple settings for RAG system"""
    
    # Embedding model
    EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large-v1"
    EMBEDDING_DEVICE = "cpu"  # Change to "cuda" if you have GPU
    
    # ChromaDB settings
    CHROMA_DIR = "./data/chroma_db"
    COLLECTION_NAME = "documents"
    
    # Document processing
    CHUNK_SIZE = 500  # Smaller chunks for better processing
    CHUNK_OVERLAP = 100
    
    # Local LLM (Ollama)
    OLLAMA_MODEL = "llama3.1:8b"
    OLLAMA_BASE_URL = "http://localhost:11434"
    LLM_TEMPERATURE = 0.5
    LLM_MAX_TOKENS = 512
    
    # RAG prompt template
    RAG_PROMPT = """Answer the question using only the context below. Reply in one
complete sentence that restates the key fact. If the answer is not in the context,
reply exactly: "I don't know based on the provided documents."

Context:
{context}

Question: {question}

Answer:"""
    
    # Query prompt for mxbai embedding
    QUERY_PROMPT = "Represent this sentence for searching relevant passages:"
    
    def __init__(self):
        # Create data directory
        Path("./data").mkdir(exist_ok=True)
        Path("./data/chroma_db").mkdir(exist_ok=True)
        Path("./data/documents").mkdir(exist_ok=True)
    
    def get_embedding_model(self):
        """Get embedding model name"""
        return self.EMBEDDING_MODEL
    
    def format_query(self, query):
        """Format query for mxbai model"""
        return f"{self.QUERY_PROMPT} {query}"
    
    def format_rag_prompt(self, context, question):
        """Format RAG prompt"""
        return self.RAG_PROMPT.format(context=context, question=question)


# Global settings instance
settings = Settings()