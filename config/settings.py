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
    COLLECTION_NAME = "rag_documents"
    
    # Document processing
    CHUNK_SIZE = 500  # Smaller chunks for better processing
    CHUNK_OVERLAP = 100
    
    # Local Llama model
    LLM_MODEL_PATH = "./models/llama"  # Path to your Llama model
    LLM_DEVICE = "cpu"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 512
    
    # RAG prompt template
    RAG_PROMPT = """Context: {context}

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
    
    def get_llm_model_path(self):
        """Get LLM model path"""
        return self.LLM_MODEL_PATH
    
    def format_query(self, query):
        """Format query for mxbai model"""
        return f"{self.QUERY_PROMPT} {query}"
    
    def format_rag_prompt(self, context, question):
        """Format RAG prompt"""
        return self.RAG_PROMPT.format(context=context, question=question)


# Global settings instance
settings = Settings()