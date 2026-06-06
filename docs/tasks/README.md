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

| # | Task | Status | Depends on |
|---|------|--------|-----------|
| 01 | [Simplify the RAG core](01-simplify-rag-core.md) | ✅ done | — |
| 02 | [Make search return results](02-search-returns-results.md) | ✅ done | 01 |
| 03 | [Add local LLM generation](03-local-llm-generation.md) | ✅ done | 02 |
| 04 | [Streamlit chat UI](04-streamlit-chat-ui.md) | ✅ done | 03 |
| 05 | [Build a golden eval dataset](05-golden-dataset.md) | ✅ done | 03 |
| 06 | [Evals with promptfoo](06-evals-promptfoo.md) | ✅ done | 05 |
| 07 | [Evals with DeepEval](07-evals-deepeval.md) | ✅ done | 05 |
| 08 | [Evals with Ragas](08-evals-ragas.md) | ✅ done | 05 |
| 09 | [Conversational RAG (prompt chaining)](09-conversational-rag.md) | ✅ done | 03 |

Tasks 06–08 are independent of each other — pick any order once 05 is done.
Task 09 (multi-turn chat) only needs task 03.
