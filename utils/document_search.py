"""
Search utilities for RAG system
"""

import sys
from pathlib import Path
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import settings


def search_documents(query: str, n_results: int = 3):
    """Search in processed documents"""
    print(f"🔍 Searching for: {query}")
    
    # Connect to existing ChromaDB
    client = chromadb.PersistentClient(path="./data/chroma_db")
    collection = client.get_collection("documents")
    
    # Create embedding model
    embeddings_model = HuggingFaceEmbeddings(
        model_name=settings.get_embedding_model(),
        model_kwargs={"device": settings.EMBEDDING_DEVICE}
    )
    
    # Convert query to embedding
    formatted_query = settings.format_query(query)
    query_embedding = embeddings_model.embed_query(formatted_query)
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    print("📋 Search results:")
    for i, doc in enumerate(results['documents'][0]):
        print(f"  {i+1}. {doc[:300]}...")
    
    return results
        
