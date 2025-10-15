# User Guide - Local RAG Solution

This guide will walk you through setting up and using the Local RAG Solution step by step.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.13+** installed on your system
- **uv package manager** installed
- **Git** for cloning the repository

### Installing uv (if not already installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd local-rag-solution
```

### Step 2: Install Dependencies

```bash
# Install all required packages
uv sync
```

### Step 3: Prepare Your Documents

1. **Navigate to the documents folder:**
   ```bash
   cd data/documents
   ```

2. **Remove sample files (optional):**
   ```bash
   rm sample-*
   ```

3. **Add your own documents:**
   - Copy your PDF, TXT, or MD files to `data/documents/`
   - Supported formats: `.pdf`, `.txt`, `.md`

### Step 4: Process Documents

```bash
# Process all documents and create embeddings
python utils/document_processor.py
```

**What happens:**
- Documents are loaded and text is extracted
- Text is split into chunks (500 characters each)
- Embeddings are created using mxbai-embed-large-v1
- Everything is saved to ChromaDB

### Step 5: Test Search

```bash
# Test search functionality
python utils/document_search.py
```

### Step 6: Run Complete Pipeline

```bash
# Run the full RAG system
python main.py
```

## 🔧 Configuration

### Basic Settings

Edit `config/settings.py` to customize your setup:

```python
# Embedding model (default: mxbai-embed-large-v1)
EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large-v1"

# Document processing
CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 100       # Overlap between chunks

# Search settings
COLLECTION_NAME = "documents"
```

### Advanced Configuration

```python
# Device settings
EMBEDDING_DEVICE = "cpu"  # Change to "cuda" if you have GPU

# LLM settings (for future use)
LLM_MODEL_PATH = "./models/llama"
LLM_DEVICE = "cpu"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 512
```

## 📚 Usage Examples

### Basic Document Processing

```python
from utils import process_documents_folder

# Process documents from data/documents folder
collection = process_documents_folder()
```

### Search Documents

```python
from utils.document_search import search_documents

# Basic search
results = search_documents("What is machine learning?", n_results=3)

# Search with more results
results = search_documents("How to use Python?", n_results=5)
```

### Get Database Information

```python
from utils.document_search import get_collection_info

# Get statistics
info = get_collection_info()
print(f"Total chunks: {info['count']}")
```

### Clear Database

```python
from utils import clear_chroma_db

# Clear existing database
clear_chroma_db()
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors
```
ModuleNotFoundError: No module named 'config'
```
**Solution:** Make sure you're running from the project root directory.

#### 2. ChromaDB Dimension Mismatch
```
InvalidArgumentError: Collection expecting embedding with dimension of 1024, got 384
```
**Solution:** Clear the database and reprocess:
```bash
rm -rf data/chroma_db/
python utils/document_processor.py
```

#### 3. PDF Processing Issues
```
Error loading PDF: [filename]
```
**Solution:** 
- Ensure the PDF is not password-protected
- Try a different PDF file
- Check if the file is corrupted

#### 4. Memory Issues
```
CUDA out of memory
```
**Solution:** Change device to CPU in `config/settings.py`:
```python
EMBEDDING_DEVICE = "cpu"
```

### Performance Tips

1. **For large documents:** Increase `CHUNK_SIZE` to 1000
2. **For better search:** Decrease `CHUNK_SIZE` to 300
3. **For GPU acceleration:** Set `EMBEDDING_DEVICE = "cuda"`
4. **For faster processing:** Use smaller `CHUNK_OVERLAP`

## 📊 Understanding the Output

### Document Processing Output

```
🚀 Processing documents from folder...
==================================================
🗑️ Deleted existing ChromaDB
📄 Loaded PDF: document1.pdf
📄 Loaded: document2.txt
✅ Split 5 documents into 150 chunks
🔄 Creating embeddings...
✅ Saved 150 chunks to ChromaDB
📁 Database location: ./data/chroma_db/
🎉 Document processing completed!
```

### Search Output

```
🔍 Searching for: What is machine learning?
📋 Search results:
  1. Machine learning is a subset of artificial intelligence...
  2. ML algorithms can learn from data automatically...
```

## 🔄 Workflow

### Typical Workflow

1. **Add documents** to `data/documents/`
2. **Process documents** with `python utils/document_processor.py`
3. **Test search** with `python utils/document_search.py`
4. **Run full pipeline** with `python main.py`
5. **Integrate with your application** using the API

### Development Workflow

1. **Make changes** to your documents
2. **Clear database** with `clear_chroma_db()`
3. **Reprocess documents** with `process_documents_folder()`
4. **Test changes** with search functions

## 🚀 Next Steps

After setting up the basic system:

1. **Add Llama Model Integration**
2. **Build a Web Interface**
3. **Implement Advanced Search Features**
4. **Scale to Large Document Collections**

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error messages carefully
3. Ensure all dependencies are installed correctly
4. Verify your document formats are supported

## 📝 Notes

- **First run:** May take longer due to model downloads
- **Subsequent runs:** Much faster with cached models
- **Storage:** ChromaDB files are stored in `data/chroma_db/`
- **Documents:** Keep your source documents in `data/documents/`
