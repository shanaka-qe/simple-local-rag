# Guides

A hands-on learning project: build a small **Retrieval-Augmented Generation (RAG)**
system that runs **entirely on your own machine** — local embeddings, a local
vector database, a local LLM — then **evaluate** it with three popular tools.

No cloud accounts, no API keys, no bills. Read these in order, or jump to the
area you care about. Each guide is self-contained.

## Learning path

| # | Guide | What it covers |
|---|-------|----------------|
| 01 | [Concepts](01-concepts.md) | What RAG is, embeddings, and how meaning-based search works |
| 02 | [Setup](02-setup.md) | Prerequisites, install, and the first run |
| 03 | [Codebase tour](03-codebase-tour.md) | The architecture and what each file does |
| 04 | [Using the RAG](04-using-the-rag.md) | Run it on your own docs; key settings |
| 05 | [Local LLM generation](05-generation.md) | Closing the loop: turning chunks into an answer |
| 06 | [Chat UI](06-chat-ui.md) | A single-page app to chat with your documents |
| 07 | [Evaluation](07-evaluation.md) | Measuring quality with promptfoo, DeepEval, Ragas |
| 08 | [Reference](08-reference.md) | Glossary and troubleshooting |

## Status at a glance

This project is built incrementally. Each area has a task file in
[`docs/tasks/`](../tasks/README.md); the guides explain the *why*, the tasks give
the *how*.

| Area | Status | Task |
|------|--------|------|
| Ingestion + embeddings + ChromaDB | ✅ available | — |
| Simplify to `.md` only | 🚧 planned | [01](../tasks/01-simplify-rag-core.md) |
| Search returns data | 🚧 planned | [02](../tasks/02-search-returns-results.md) |
| Local LLM generation | 🚧 planned | [03](../tasks/03-local-llm-generation.md) |
| Streamlit chat UI | 🚧 planned | [04](../tasks/04-streamlit-chat-ui.md) |
| Golden dataset | 🚧 planned | [05](../tasks/05-golden-dataset.md) |
| Evals (promptfoo/DeepEval/Ragas) | 🚧 planned | [06](../tasks/06-evals-promptfoo.md) · [07](../tasks/07-evals-deepeval.md) · [08](../tasks/08-evals-ragas.md) |

Today the project does the **retrieval half** (embed → store → search). Generation,
UI, and evals are what you'll add as you work through the tasks.
