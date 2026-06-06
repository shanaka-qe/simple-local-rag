# 05 — Local LLM generation

← [Using the RAG](04-using-the-rag.md) · [Guides index](README.md) · next → [Chat UI](06-chat-ui.md)

> **Status: ✅ done** — implemented in [task 03](../tasks/03-local-llm-generation.md).

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

## Under the hood

The module `utils/rag.py` exposes one function:

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
LLM_TEMPERATURE = 0.5
```

The `RAG_PROMPT` template tells the model to answer **only** from the context, in a
**complete sentence**, and to **decline** when the answer isn't there:

```
Answer the question using only the context below. Reply in one complete sentence
that restates the key fact. If the answer is not in the context, reply exactly:
"I don't know based on the provided documents."

Context:
{context}

Question: {question}

Answer:
```

Two reasons this wording matters: (1) "decline if not in the context" makes the RAG
**honest** about gaps instead of inventing answers; (2) a **complete sentence**
("The refund window is 30 days…") states the fact explicitly, which reads better
*and* is easier for faithfulness evals to verify than a bare "30 days".

Returning `contexts` alongside `answer` is deliberate: the UI renders them as
*sources*, and the eval tools score the answer *against* them (faithfulness).

## Multi-turn conversations (prompt chaining)

`answer_question` also takes an optional `history` (the recent chat turns). When
it's given, the function runs a tiny **two-step chain** instead of one step:

```
1. condense   "how long is it?"  +  history  ─►  "how long is the standard warranty?"
2. retrieve + answer   (search with the standalone question, then write the answer)
```

The first step rewrites a vague follow-up into a **standalone question** so the
document search has enough to work with; the second step is the normal retrieve
-and-answer. With no `history` (a single question, or the eval tools), step 1 is
skipped and behaviour is unchanged. Cost: a follow-up makes **two** local LLM
calls instead of one. See [task 09](../tasks/09-conversational-rag.md).

→ Next: [Chat UI](06-chat-ui.md)
