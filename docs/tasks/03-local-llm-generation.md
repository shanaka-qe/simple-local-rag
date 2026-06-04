# 03 — Add local LLM generation

**Goal:** Complete the RAG loop — take the retrieved chunks, send them to a local
Ollama model with the question, and return a written answer.

## Prerequisites

- Ollama running locally (`ollama serve`) with `llama3.1:8b` pulled.

## Steps

- [ ] Add deps: `uv add langchain-ollama ollama`.
- [ ] Add Ollama settings to `config/settings.py`
      (`OLLAMA_MODEL = "llama3.1:8b"`, `OLLAMA_BASE_URL`, temperature).
- [ ] Add a small `utils/rag.py` with an `answer_question(query)` that:
      1. retrieves chunks (task 02), 2. fills the `RAG_PROMPT` template with the
      chunks as context, 3. calls the Ollama model, 4. returns
      `{"answer": str, "contexts": list[str]}`.
- [ ] Export `answer_question` from `utils/__init__.py`.
- [ ] Update `main.py` to print a real answer for each test question.

## Files

`config/settings.py`, `utils/rag.py`, `utils/__init__.py`, `main.py`, `pyproject.toml`

## Done when

`answer_question("Who is Prof. Elena Rodriguez?")` returns a sensible answer plus
the contexts it used.

> Tip: a clean Ollama-via-LangChain wrapper already exists in the sibling
> `simple-local-chat-client` repo — reuse that pattern instead of writing from scratch.
