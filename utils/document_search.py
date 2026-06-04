"""
Search utilities for RAG system
"""

import sys
from functools import lru_cache
from pathlib import Path
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import settings


@lru_cache(maxsize=1)
def get_embeddings_model():
    """Load the embedding model once and reuse it across calls."""
    return HuggingFaceEmbeddings(
        model_name=settings.get_embedding_model(),
        model_kwargs={"device": settings.EMBEDDING_DEVICE}
    )


def search_documents(query: str, n_results: int = 3, verbose: bool = False) -> dict:
    """Search the processed documents and return the matching chunks.

    Returns:
        dict: {"query": <the query>, "chunks": <list of matching chunk texts>}
    """
    # Connect to existing ChromaDB
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    collection = client.get_collection(settings.COLLECTION_NAME)

    # Get the (cached) embedding model
    embeddings_model = get_embeddings_model()

    # Convert query to embedding
    formatted_query = settings.format_query(query)
    query_embedding = embeddings_model.embed_query(formatted_query)

    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    chunks = results["documents"][0]

    if verbose:
        print(f"🔍 Searching for: {query}")
        print("📋 Search results:")
        for i, chunk in enumerate(chunks, start=1):
            print(f"  {i}. {chunk[:300]}...")

    return {"query": query, "chunks": chunks}


def get_index_status() -> dict:
    """Report whether the index exists and how many chunks it holds.

    Returns:
        dict: {"exists": bool, "count": int}
    """
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        collection = client.get_collection(settings.COLLECTION_NAME)
        return {"exists": True, "count": collection.count()}
    except Exception:
        return {"exists": False, "count": 0}

