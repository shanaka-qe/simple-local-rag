# Tasks

A small, ordered roadmap for turning this repo into a local RAG system you can
chat with and evaluate. Each task is self-contained — do them in order.

## Project choices

| Area | Choice |
|------|--------|
| Embeddings | HuggingFace `mxbai-embed-large-v1` (local, free, runs on CPU) |
| Vector store | ChromaDB (local, persistent) |
| Generation | Ollama, default model `llama3.1:8b` |
| UI | Streamlit (single page) |
| Ingested files | `.md` only |

## Order

| # | Task | Depends on |
|---|------|-----------|
| 01 | [Simplify the RAG core](01-simplify-rag-core.md) | — |
| 02 | [Make search return results](02-search-returns-results.md) | 01 |
| 03 | [Add local LLM generation](03-local-llm-generation.md) | 02 |
| 04 | [Streamlit chat UI](04-streamlit-chat-ui.md) | 03 |
| 05 | [Build a golden eval dataset](05-golden-dataset.md) | 03 |
| 06 | [Evals with promptfoo](06-evals-promptfoo.md) | 05 |
| 07 | [Evals with DeepEval](07-evals-deepeval.md) | 05 |
| 08 | [Evals with Ragas](08-evals-ragas.md) | 05 |

Tasks 06–08 are independent of each other — pick any order once 05 is done.
