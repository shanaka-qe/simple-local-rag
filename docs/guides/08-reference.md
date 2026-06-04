# 08 — Reference

← [Evaluation](07-evaluation.md) · [Guides index](README.md)

## Glossary

| Term | Meaning |
|------|---------|
| **RAG** | Retrieval-Augmented Generation — retrieve relevant text, then generate an answer from it. |
| **Embedding** | A list of numbers representing the meaning of a piece of text. |
| **Vector database** | A store that finds items by closeness of meaning (here, ChromaDB). |
| **Chunk** | A small slice of a document that gets embedded and stored. |
| **Cosine similarity** | The measure of "closeness" between two embeddings used here. |
| **LLM** | Large Language Model — writes answers; run locally via Ollama. |
| **Ollama** | A tool that runs LLMs locally on your machine. |
| **Faithfulness** | Does the answer stick to the retrieved context (vs. making things up)? |
| **Context precision / recall** | Did retrieval fetch the *right* chunks, and *enough* of them? |
| **Golden dataset** | A fixed set of test cases used to measure quality repeatably. |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'config'` | Run from the project root, e.g. `uv run python main.py`. |
| ChromaDB dimension mismatch | Delete `data/chroma_db/` and re-run ingestion (the embedding shape changed). |
| First run is slow | The embedding model downloads once (~640 MB); later runs are offline. |
| Generation / UI commands "don't work yet" | Those land in tasks 03–04 — see the [status table](README.md#status-at-a-glance). |
| Ollama errors (task 03+) | Make sure `ollama serve` is running and the model is pulled (`ollama pull llama3.1:8b`). |

## Configuration reference

All settings live in `config/settings.py`.

| Setting | Default | Purpose |
|---------|---------|---------|
| `EMBEDDING_MODEL` | `mixedbread-ai/mxbai-embed-large-v1` | Local embedding model (1024-dim) |
| `EMBEDDING_DEVICE` | `cpu` | `cuda` only with a compatible GPU |
| `CHROMA_DIR` | `./data/chroma_db` | Where the vector DB is stored |
| `COLLECTION_NAME` | `documents` | ChromaDB collection name |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Shared characters between neighbouring chunks |
| `QUERY_PROMPT` | mxbai search prefix | Prepended to queries before embedding |
| `RAG_PROMPT` | context/question template | Prompt sent to the LLM (task 03+) |
| `OLLAMA_MODEL` | `llama3.1:8b` | Local generation model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server |
| `LLM_TEMPERATURE` | `0.7` | Sampling temperature |

## Function reference

| Function | Returns | Status |
|----------|---------|--------|
| `process_documents_folder(folder_path, collection_name)` | the ChromaDB collection | ✅ |
| `search_documents(query, n_results)` | `{"query", "chunks"}` | ✅ [task 02](../tasks/02-search-returns-results.md) |
| `answer_question(query, n_results)` | `{"answer", "contexts"}` | ✅ [task 03](../tasks/03-local-llm-generation.md) |

## Where to go next

- The build roadmap: [`docs/tasks/`](../tasks/README.md)
- Start building: [task 01 — Simplify the RAG core](../tasks/01-simplify-rag-core.md)
