# 06 — Chat UI

← [Local LLM generation](05-generation.md) · [Guides index](README.md) · next → [Evaluation](07-evaluation.md)

> **Status: ✅ done** — implemented in `app.py` ([task 04](../tasks/04-streamlit-chat-ui.md)).

## What this area adds

A single-page web app to chat with your documents, instead of editing `main.py`
to change the question. Built with **Streamlit** — one small Python file.

```
  ┌─────────────────────────────────────┐
  │  Ask a question:  [______________]   │
  │                                      │
  │  Answer:                             │
  │    ...the model's answer...          │
  │                                      │
  │  ▸ Sources (retrieved chunks)        │
  └─────────────────────────────────────┘
```

## How it works

- A text box takes your question.
- It calls the RAG answer function from [task 03](../tasks/03-local-llm-generation.md).
- It shows the answer, with the retrieved chunks tucked into an expandable
  "sources" section.
- Chat history stays on screen during the session.

## Run it

```bash
uv run streamlit run app.py
```

## What you'll learn

- How to wrap a Python pipeline in a usable interface with very little code.
- Why showing **sources** matters for trust — you can see *what* the answer used.

## Under the hood

`app.py` outline (the real file also adds a sidebar with index status and a
build/rebuild button):

```python
import streamlit as st
from utils.rag import answer_question

st.title("Chat with your docs")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:                 # replay history each rerun
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": q})
    result = answer_question(q)
    with st.chat_message("assistant"):
        st.markdown(result["answer"])
        with st.expander("Sources"):
            for c in result["contexts"]:
                st.markdown(c)
    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
```

Technical notes:

- **`st.session_state`** persists the conversation across Streamlit's
  rerun-on-every-interaction model (the whole script re-executes on each input).
- The embedding model is loaded **once** and reused via an `lru_cache` in
  `utils/document_search.py`, so the UI stays responsive without reloading it on
  every interaction.
- The **sidebar** shows index status and a **Build / rebuild** button; the build
  and answer calls are wrapped so a failure shows a friendly message, not a traceback.
- `uv run streamlit run app.py` serves the page at `http://localhost:8501`.

→ Next: [Evaluation](07-evaluation.md)
