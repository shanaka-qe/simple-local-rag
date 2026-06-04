# Local RAG Solution

**Author:** Shanaka Fernando · **LinkedIn:** https://www.linkedin.com/in/shanaka-qe/

A hands-on learning project: build a small **Retrieval-Augmented Generation (RAG)**
system that runs **entirely on your own machine** — local embeddings, a local
vector database (ChromaDB), and a local LLM (Ollama) — then **evaluate** it with
promptfoo, DeepEval, and Ragas. No cloud accounts, no API keys, no cost.

## What you'll learn

- How RAG works: retrieval (embeddings + vector search) and generation (a local LLM)
- Running models locally with HuggingFace embeddings and Ollama
- Chatting with your own documents through a simple web UI
- Measuring RAG quality with three different evaluation tools

## Quick start

```bash
uv sync                       # install dependencies
ollama pull llama3.1:8b       # local model (used from the generation step on)
uv run python main.py         # ingest the sample docs and run example searches
```

> The first run downloads the embedding model once (~640 MB); after that it runs
> fully offline.

## Documentation

| | |
|---|---|
| 📖 **User guide** | [`docs/guides/`](docs/guides/README.md) — concepts, setup, codebase tour, and each area explained |
| 🛠️ **Build roadmap** | [`docs/tasks/`](docs/tasks/README.md) — the project built one task at a time |

Start with the [guides index](docs/guides/README.md).

## License

MIT
