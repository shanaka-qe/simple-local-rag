"""
Document processing utility for RAG system
"""

import os
import sys
from pathlib import Path
from typing import List
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import settings


def clear_chroma_db():
    """Delete the existing collection so it can be rebuilt cleanly.

    Uses the ChromaDB client API rather than deleting the directory, so it stays
    consistent in long-running processes (e.g. the Streamlit app) where the client
    is cached in memory.
    """
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    try:
        client.delete_collection(settings.COLLECTION_NAME)
        print("🗑️ Deleted existing collection")
    except Exception:
        print("📁 No existing collection found")


def load_documents_from_folder(folder_path: str) -> List[str]:
    """Load all Markdown documents from a folder"""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder {folder_path} does not exist")
        return documents
    
    # Supported file types
    supported_extensions = ['.md']

    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        documents.append(content)
                        print(f"📄 Loaded: {file_path.name}")
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")
    
    print(f"✅ Loaded {len(documents)} documents from {folder_path}")
    return documents


def chunk_documents(documents: List[str]) -> List[str]:
    """Split documents into chunks"""
    text_splitter = CharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    all_chunks = []
    for doc in documents:
        chunks = text_splitter.split_text(doc)
        all_chunks.extend(chunks)
    
    print(f"✅ Split {len(documents)} documents into {len(all_chunks)} chunks")
    return all_chunks


def create_embeddings_and_save(chunks: List[str], collection_name: str = settings.COLLECTION_NAME):
    """Create embeddings and save to ChromaDB"""
    print("🔄 Creating embeddings...")
    
    # Create ChromaDB client
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)

    # Replace any existing collection so the rebuild is clean
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    # Create collection
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Create embedding model
    embeddings_model = HuggingFaceEmbeddings(
        model_name=settings.get_embedding_model(),
        model_kwargs={"device": settings.EMBEDDING_DEVICE}
    )
    
    # Convert chunks to embeddings
    chunk_embeddings = embeddings_model.embed_documents(chunks)
    
    # Create IDs for chunks
    chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    # Save to ChromaDB
    collection.add(
        documents=chunks,
        embeddings=chunk_embeddings,
        ids=chunk_ids
    )
    
    print(f"✅ Saved {len(chunks)} chunks to ChromaDB")
    print(f"📁 Database location: {settings.CHROMA_DIR}")
    
    return collection


def process_documents_folder(folder_path: str = "./data/documents", collection_name: str = settings.COLLECTION_NAME):
    """Complete pipeline: clear, load, chunk, and save documents"""
    print("🚀 Processing documents from folder...")
    print("=" * 50)
    
    # Step 1: Clear existing ChromaDB
    clear_chroma_db()
    
    # Step 2: Load documents from folder
    documents = load_documents_from_folder(folder_path)
    
    if not documents:
        print("❌ No documents found to process")
        return None
    
    # Step 3: Split into chunks
    chunks = chunk_documents(documents)
    
    # Step 4: Create embeddings and save
    collection = create_embeddings_and_save(chunks, collection_name)
    
    print("🎉 Document processing completed!")
    print(f"📊 Summary:")
    print(f"   - Documents loaded: {len(documents)}")
    print(f"   - Chunks created: {len(chunks)}")
    print(f"   - Collection name: {collection_name}")
    
    return collection
