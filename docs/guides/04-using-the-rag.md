# 04 — Using the RAG

← [Codebase tour](03-codebase-tour.md) · [Guides index](README.md) · next → [Local LLM generation](05-generation.md)

## Run it

```bash
uv run python main.py
```

This opens an interactive console:

```
  1) Build / rebuild the index from data/documents
  2) Show index status
  3) Search (show matching chunks, no answer)
  4) Ask a single question
  5) Chat (interactive)
  0) Exit
```

The first time, choose **1** to build the index, then **4** or **5** to ask
questions. Building (option 1) is the only step that wipes and re-embeds — asking
questions just reads the existing index.

> Prefer a browser? See the [Chat UI guide](06-chat-ui.md) — `uv run streamlit run app.py`.

## Use your own documents

1. Drop `.md` files into `data/documents/`.
2. In the console, choose **1** to rebuild the index.
3. Ask away with **4** (single question) or **5** (chat).

## Key settings

Edit `config/settings.py`:

```python
EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large-v1"  # local embedding model
EMBEDDING_DEVICE = "cpu"        # "cuda" if you have a GPU
CHUNK_SIZE = 500                # characters per chunk
CHUNK_OVERLAP = 100             # shared characters between neighbouring chunks
COLLECTION_NAME = "documents"   # name of the ChromaDB collection
```

| Setting | Effect |
|---------|--------|
| `CHUNK_SIZE` ↓ | More precise retrieval, less context per hit |
| `CHUNK_SIZE` ↑ | More context per hit, less precise |
| `CHUNK_OVERLAP` | Shared text between neighbouring chunks, so ideas split across a boundary aren't lost |
| `EMBEDDING_DEVICE` | `"cpu"` everywhere; `"cuda"` only if you have a compatible GPU |

After changing chunking or the embedding model, re-run ingestion to rebuild the DB.

## Under the hood

### Public API (today)

```python
from utils import process_documents_folder, search_documents

process_documents_folder(folder_path="./data/documents",
                         collection_name="documents")   # builds the DB, returns the collection
search_documents(query, n_results=3)                    # -> {"query": ..., "chunks": [...]}
```

### Design rationale

| Choice | Why |
|--------|-----|
| Wipe-and-rebuild on the build step | Keeps the index consistent with `data/documents/` with zero bookkeeping; fine at this scale. Incremental upserts only matter for a large, frequently-changing corpus. |
| Cosine similarity | Standard for text embeddings — compares *direction* (meaning), not magnitude. |
| `chunk_size=500` / `overlap=100` | A practical default: small enough for precise hits, with 20% overlap so boundary-spanning ideas survive. |
| mxbai query prefix | The model is asymmetric — prefixing the query is how it was trained for retrieval. |

### Extending it

- **Swap the embedding model:** change `EMBEDDING_MODEL` in settings.
  ⚠️ Different models output different dimensions — delete `data/chroma_db/` and
  re-ingest, or you'll hit a dimension-mismatch error.
- **Tune retrieval:** raise `n_results` to give the LLM more context (task 03), or
  lower `CHUNK_SIZE` for tighter, more precise matches.

→ Next: [Local LLM generation](05-generation.md)
