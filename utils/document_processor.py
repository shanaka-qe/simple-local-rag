"""
Document processing utility for RAG system
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, PyMuPDFLoader

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import settings


def clear_chroma_db():
    """Completely delete existing ChromaDB to avoid conflicts"""
    chroma_path = Path("./data/chroma_db")
    
    if chroma_path.exists():
        shutil.rmtree(chroma_path)
        print("🗑️ Deleted existing ChromaDB")
    else:
        print("📁 No existing ChromaDB found")


def load_pdf_file(file_path: Path) -> str:
    """Load and extract text from PDF file with fallback methods"""
    full_text = ""
    
    # Try PyMuPDFLoader first (more robust)
    try:
        print(f"🔄 Trying PyMuPDFLoader for {file_path.name}...")
        loader = PyMuPDFLoader(str(file_path))
        pages = loader.load()
        
        # Combine all pages into one text
        for page in pages:
            full_text += page.page_content + "\n"
        
        if full_text.strip():
            print(f"✅ PyMuPDFLoader successful: {len(full_text)} characters")
            return full_text.strip()
    except Exception as e:
        print(f"⚠️ PyMuPDFLoader failed: {e}")
    
    # Fallback to PyPDFLoader
    try:
        print(f"🔄 Trying PyPDFLoader for {file_path.name}...")
        loader = PyPDFLoader(str(file_path))
        pages = loader.load()
        
        # Combine all pages into one text
        for page in pages:
            full_text += page.page_content + "\n"
        
        if full_text.strip():
            print(f"✅ PyPDFLoader successful: {len(full_text)} characters")
            return full_text.strip()
    except Exception as e:
        print(f"❌ PyPDFLoader also failed: {e}")
    
    print(f"❌ Could not extract text from {file_path.name}")
    return ""


def load_documents_from_folder(folder_path: str) -> List[str]:
    """Load all documents from a folder (PDF, TXT, MD)"""
    documents = []
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Folder {folder_path} does not exist")
        return documents
    
    # Supported file types
    supported_extensions = ['.pdf', '.txt', '.md']
    
    for file_path in folder.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                if file_path.suffix.lower() == '.pdf':
                    # Handle PDF files
                    content = load_pdf_file(file_path)
                    if content:
                        documents.append(content)
                        print(f"📄 Loaded PDF: {file_path.name}")
                else:
                    # Handle text files (.txt, .md)
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


def create_embeddings_and_save(chunks: List[str], collection_name: str = "documents"):
    """Create embeddings and save to ChromaDB"""
    print("🔄 Creating embeddings...")
    
    # Create ChromaDB client
    client = chromadb.PersistentClient(path="./data/chroma_db")
    
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
    print(f"📁 Database location: ./data/chroma_db/")
    
    return collection


def process_documents_folder(folder_path: str = "./data/documents", collection_name: str = "documents"):
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
