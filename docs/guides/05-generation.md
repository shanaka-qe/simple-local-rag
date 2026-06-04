# 05 — Local LLM generation

← [Using the RAG](04-using-the-rag.md) · [Guides index](README.md) · next → [Chat UI](06-chat-ui.md)

> **Status: 🚧 planned** — build it with [task 03](../tasks/03-local-llm-generation.md).

## What this area adds

So far the system *retrieves* chunks but doesn't *answer*. This area closes the
RAG loop by sending the retrieved chunks plus the question to a **local LLM**
(via Ollama) and getting back a written answer.

```
  question ─► retrieve chunks ─► build prompt ─► local LLM ─► answer
                                  (context +        (Ollama)
                                   question)
```

## How it works

1. **Retrieve** the most relevant chunks for the question (the existing search).
2. **Build a prompt** by inserting those chunks as *context* into a template:

   ```
   Context: {the retrieved chunks}
   Question: {the user's question}
   Answer:
   ```

3. **Generate** — the local model reads the context and writes an answer.
4. **Return** both the `answer` and the `contexts` it used (so the UI can show
   sources and the eval tools can score faithfulness).

## Why local

The model runs on your machine through **Ollama** — private, free, offline. The
default is `llama3.1:8b`; you can swap in any model you've pulled.

## What you'll learn

- How "context" is actually fed to a model (it's just text in the prompt).
- Why returning `{answer, contexts}` matters: the UI and every eval tool need it.
- The difference between *retrieval* quality and *answer* quality.

## Under the hood (intended design)

> The code lands in [task 03](../tasks/03-local-llm-generation.md); this is the
> planned shape, kept in step with that task.

A new module `utils/rag.py` exposes one function:

```python
def answer_question(query: str, n_results: int = 3) -> dict:
    """Returns {"answer": str, "contexts": list[str]}."""
```

Flow:

```python
from langchain_ollama import OllamaLLM

result   = search_documents(query, n_results)      # task 02 -> {"query", "chunks"}
contexts = result["chunks"]
prompt   = settings.format_rag_prompt(
    context="\n\n".join(contexts),
    question=query,
)
llm = OllamaLLM(model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=settings.LLM_TEMPERATURE)
answer = llm.invoke(prompt)
return {"answer": answer, "contexts": contexts}
```

New settings in `config/settings.py`:

```python
OLLAMA_MODEL    = "llama3.1:8b"
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_TEMPERATURE = 0.7
```

The existing `RAG_PROMPT` template is reused as-is:

```
Context: {context}

Question: {question}

Answer:
```

Returning `contexts` alongside `answer` is deliberate: the UI renders them as
*sources*, and the eval tools score the answer *against* them (faithfulness).

→ Next: [Chat UI](06-chat-ui.md)
