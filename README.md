# Local RAG Solution

**Author:** Shanaka Fernando  
**LinkedIn:** https://www.linkedin.com/in/shanaka-qe/

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
│   ├── documents/               # Your documents go here (sample files included)
│   └── chroma_db/              # ChromaDB storage (auto-created)
├── main.py                     # Main application
├── pyproject.toml             # Dependencies
└── README.md                   # This file
```

## 📖 Getting Started

**For detailed setup and usage instructions, see [USER_GUIDE.md](USER_GUIDE.md)**

### Quick Start
```bash
# Clone and install
git clone <your-repo-url>
cd local-rag-solution
uv sync

# Add your documents to data/documents/
# Process documents
python utils/document_processor.py

# Test search
python utils/document_search.py

# Run full pipeline
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
