# Local RAG Solution

Author: Shanaka Fernando
LinkedIn: https://www.linkedin.com/in/shanaka-qe/

A simple, local Retrieval-Augmented Generation (RAG) system built with LangChain, ChromaDB, and local Llama models. This project demonstrates how to create a complete RAG pipeline for document processing and intelligent search.

## 🚀 Features

- **Local Document Processing**: Supports PDF, TXT, and Markdown files
- **Advanced Embeddings**: Uses mxbai-embed-large-v1 for high-quality vector representations
- **Persistent Storage**: ChromaDB for local vector database storage
- **Intelligent Search**: Semantic search with similarity scoring
- **Modular Design**: Clean, organized codebase with utility functions
- **No Docker Required**: Everything runs locally with Python

## 📁 Project Structure

```
local-rag-solution/
├── config/
│   └── settings.py              # Configuration settings
├── utils/
│   ├── __init__.py              # Package initialization
│   ├── document_processor.py    # Document processing utilities
│   └── document_search.py       # Search utilities
├── data/
│   ├── documents/               # Your documents go here
│   └── chroma_db/              # ChromaDB storage (auto-created)
├── main.py                     # Main application
├── pyproject.toml             # Dependencies
└── README.md                   # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- uv package manager

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd local-rag-solution

# Install dependencies
uv sync

# Create documents directory
mkdir -p data/documents
```

## 📚 Usage

### 1. Add Your Documents
Place your documents in the `data/documents/` folder:
```bash
data/documents/
├── your-document.pdf
├── notes.txt
└── research.md
```

**Supported formats**: PDF, TXT, MD

### 2. Process Documents
```bash
# Process all documents and create embeddings
python utils/document_processor.py
```

### 3. Search Documents
```bash
# Test search functionality
python utils/document_search.py
```

### 4. Run Complete Pipeline
```bash
# Run the full RAG system
python main.py
```

## 🔧 Configuration

Edit `config/settings.py` to customize:

```python
# Embedding model
EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large-v1"

# Document processing
CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 100       # Overlap between chunks

# Search settings
COLLECTION_NAME = "documents"
```

## 🔍 API Reference

### Document Processing
```python
from utils import process_documents_folder, clear_chroma_db

# Process documents from folder
collection = process_documents_folder()

# Clear existing database
clear_chroma_db()
```

### Search Functions
```python
from utils.document_search import search_documents

# Basic search
results = search_documents("What is machine learning?", n_results=3)

# Search with metadata
results = search_with_metadata("How to use Python?", n_results=2)
```

### Database Info
```python
from utils.document_search import get_collection_info

# Get database statistics
info = get_collection_info()
print(f"Total chunks: {info['count']}")
```

## 🧠 How It Works

### 1. Document Processing
- **Load documents** from `data/documents/` folder
- **Extract text** from PDFs using PyMuPDFLoader
- **Split into chunks** using CharacterTextSplitter
- **Create embeddings** using mxbai-embed-large-v1
- **Store in ChromaDB** for fast retrieval

### 2. Search Process
- **Convert query** to embedding using same model
- **Search ChromaDB** for similar chunks
- **Return ranked results** with similarity scores

### 3. RAG Pipeline
```
Documents → Chunks → Embeddings → ChromaDB → Search → Results
```

## 📊 Performance

- **Embedding Model**: mxbai-embed-large-v1 (1024 dimensions)
- **Vector Database**: ChromaDB with HNSW indexing
- **Search Speed**: Sub-second retrieval
- **Storage**: Local disk persistence

## 🔧 Dependencies

- **langchain**: Framework for LLM applications
- **chromadb**: Vector database
- **sentence-transformers**: Embedding models
- **pymupdf**: PDF processing
- **transformers**: Hugging Face models
- **torch**: PyTorch backend

## 🚀 Next Steps

1. **Add Llama Model**: Integrate local Llama model for text generation
2. **Web Interface**: Build a simple web UI for document search
3. **Advanced Search**: Implement query expansion and re-ranking
4. **Batch Processing**: Handle large document collections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **LangChain** for the RAG framework
- **ChromaDB** for vector storage
- **Hugging Face** for embedding models
- **Mixedbread AI** for mxbai embeddings
