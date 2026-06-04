# 04 — Streamlit chat UI

**Goal:** A single-page web UI to chat with your documents.

## Steps

- [ ] Add dep: `uv add streamlit`.
- [ ] Create `app.py` with a Streamlit chat interface:
      - a text input for the question,
      - calls `answer_question()` (task 03),
      - shows the answer, and the retrieved chunks in an expander ("sources").
- [ ] Keep chat history in `st.session_state` so the conversation stays on screen.
- [ ] Run with `uv run streamlit run app.py`.

## Files

`app.py`, `pyproject.toml`

## Done when

You can open the browser page, type a question, and see an answer with its sources.

> Keep it minimal — one file, no extra styling needed.
