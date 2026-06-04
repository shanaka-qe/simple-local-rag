# 01 — Concepts

← [Guides index](README.md) · next → [Setup](02-setup.md)

## What is RAG?

A language model is great at *writing*, but it doesn't know *your* documents.
**Retrieval-Augmented Generation (RAG)** fixes that in two steps:

```
  RETRIEVAL  →  find the most relevant snippets from your documents
  GENERATION →  an LLM writes an answer using those snippets
```

Think of retrieval as a librarian who fetches the right pages, and generation as
the person who reads those pages and explains them.

## Embeddings — turning meaning into numbers

Computers can't compare meaning the way we do. So we turn every piece of text into
a list of numbers — an **embedding** — that captures its meaning. Similar meaning
produces similar numbers.

```
"refund window"       → [0.12, -0.88, 0.34, ...]  ┐ close together
"how long to return"  → [0.11, -0.85, 0.36, ...]  ┘ = similar meaning
"quantum physics"     → [0.91,  0.40, -0.70, ...]   = far away, unrelated
```

This project uses a **local, free** embedding model (HuggingFace
`mxbai-embed-large-v1`) that runs on your CPU.

## Vector search

"Search" then becomes: embed the question, and find the stored chunks whose
numbers are **closest**. That closeness search is what a **vector database** does.
Here that's **ChromaDB** — local, persistent, using cosine similarity.

## Chunking

Whole documents are too big to embed usefully, so we split them into small
**chunks** (~500 characters) before embedding. Smaller chunks → more precise
retrieval; larger chunks → more context per hit.

## Why "local"?

Everything here runs on your machine: the embedding model, the vector DB, and
(from [task 03](../tasks/03-local-llm-generation.md)) the LLM via **Ollama**. That
means it's private, free, and works offline after the first model download.

## Under the hood

Embeddings come from `mxbai-embed-large-v1` via
`langchain_huggingface.HuggingFaceEmbeddings`, which wraps `sentence-transformers`:

- **Dimensions:** each chunk becomes a 1024-float vector.
- **Asymmetric prompting:** mxbai is trained so *queries* get a prefix and
  *documents* don't. The prefix lives in `config/settings.py`:
  ```python
  QUERY_PROMPT = "Represent this sentence for searching relevant passages:"
  ```
  Documents are embedded as-is; a question is embedded as `f"{QUERY_PROMPT} {query}"`.
  Skipping this prefix measurably hurts retrieval quality.
- **Similarity:** ChromaDB compares vectors with **cosine distance**
  (`metadata={"hnsw:space": "cosine"}`) and indexes them with **HNSW** (approximate
  nearest-neighbour), so search stays fast as the collection grows.

Chunking uses LangChain's `CharacterTextSplitter`: it splits on a separator
(`\n\n` by default), then merges pieces up to `CHUNK_SIZE` characters with
`CHUNK_OVERLAP` characters shared between neighbours. The overlap means an idea
straddling a boundary still appears whole in at least one chunk.

→ Next: [Setup](02-setup.md)
