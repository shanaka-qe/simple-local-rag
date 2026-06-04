# 03 — Codebase tour

← [Setup](02-setup.md) · [Guides index](README.md) · next → [Using the RAG](04-using-the-rag.md)

## Architecture

```
  data/documents/*.md
        │  load
        ▼
     chunk (≈500 chars)
        │  embed  (HuggingFace mxbai — local, free)
        ▼
     ChromaDB  (local, persistent, cosine similarity)
        │
   question ──embed──► search ──► top matching chunks
        │                               │
        │                       prompt template
        ▼                               ▼
   Streamlit chat UI ◄──── answer ◄── local LLM (Ollama)
                                        │
            evaluation ─────────────────┘
            promptfoo · DeepEval · Ragas
```

Everything in this diagram runs locally.

## Folder layout

```
local-rag-solution/
├── main.py                      # interactive console (build index, search, ask, chat)
├── app.py                       # Streamlit web UI (browser chat)
├── config/
│   └── settings.py              # all settings in one place
├── utils/
│   ├── document_processor.py    # load → chunk → embed → store (builds the DB)
│   ├── document_search.py       # turn a question into a search over the DB
│   └── rag.py                   # retrieve + generate an answer (full RAG)
├── data/
│   ├── documents/               # put your .md files here
│   └── chroma_db/               # the vector database (auto-created, git-ignored)
└── docs/
    ├── guides/                  # these guides
    └── tasks/                   # the build roadmap
```

## What each file does

| File | Plain-English job |
|------|-------------------|
| `config/settings.py` | One place for every setting: embedding model, chunk size (500) / overlap (100), where ChromaDB lives, the collection name, prompt templates. |
| `utils/document_processor.py` | The ingestion pipeline: read files → split into chunks → create embeddings → save to ChromaDB. Rebuilds the collection each time you build the index. |
| `utils/document_search.py` | Takes a question, embeds it, asks ChromaDB for the closest chunks. |
| `utils/rag.py` | The full RAG: retrieve chunks, build the prompt, call the local LLM, return `{answer, contexts}`. |
| `main.py` | Interactive console: build the index, search, ask a question, or chat. |
| `app.py` | Streamlit web UI: a browser chat page over the same RAG. |

> The `utils/*.py` files are libraries imported by `main.py`. Running them directly
> does nothing on their own — use `main.py`.

## Under the hood

### Ingestion — `utils/document_processor.py`

`process_documents_folder()` orchestrates four steps:

1. **`clear_chroma_db()`** — deletes the existing collection via the ChromaDB
   client API so the index rebuilds cleanly (no stale or duplicate chunks). Using
   the API rather than removing files keeps it safe in long-running processes like
   the Streamlit app, where the client is cached in memory.
2. **`load_documents_from_folder(folder)`** — walks the folder with
   `Path.rglob('*')` and reads `.md` files into a list of strings.
3. **`chunk_documents(docs)`** — runs each document through
   `CharacterTextSplitter(chunk_size=500, chunk_overlap=100)` and flattens the
   result into one list of chunk strings.
4. **`create_embeddings_and_save(chunks)`** — the core:
   ```python
   client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
   collection = client.create_collection(name, metadata={"hnsw:space": "cosine"})
   embeddings_model = HuggingFaceEmbeddings(model_name=..., model_kwargs={"device": "cpu"})
   vectors = embeddings_model.embed_documents(chunks)   # list[list[float]], each len 1024
   collection.add(documents=chunks, embeddings=vectors, ids=[f"chunk_{i}" for i, _ in enumerate(chunks)])
   ```

### What ChromaDB stores

For each chunk the collection holds three aligned things: an **id**
(`chunk_0`, `chunk_1`, …), the **document** (the chunk text), and its **embedding**
(the 1024-float vector). Metadata is empty in this project.

### Search — `utils/document_search.py`

```python
client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
collection = client.get_collection(settings.COLLECTION_NAME)
q  = settings.format_query(query)                # prepends the mxbai query prefix
qv = embeddings_model.embed_query(q)             # 1024-float vector
results = collection.query(query_embeddings=[qv], n_results=n)
```

`results` is a dict of parallel lists, batched per query. The useful keys:

| Key | Shape | Meaning |
|-----|-------|---------|
| `results["documents"][0]` | `list[str]` | the matched chunk texts, best first |
| `results["distances"][0]` | `list[float]` | cosine distance (smaller = closer) |
| `results["ids"][0]` | `list[str]` | the chunk ids |

> `search_documents()` returns these as `{"query", "chunks"}`
> (see [task 02](../tasks/02-search-returns-results.md)); pass `verbose=True` to
> also print them.

→ Next: [Using the RAG](04-using-the-rag.md)
