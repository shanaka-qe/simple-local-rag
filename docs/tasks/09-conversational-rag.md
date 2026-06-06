# 09 — Conversational RAG (prompt chaining)

**Status: ✅ Completed**

**Goal:** Let the chat handle **follow-up questions** ("how do I claim it?") by
adding a simple two-step **prompt chain** — without over-engineering.

## The problem

Each question was answered independently, so a follow-up like *"how long is it?"*
had no idea what "it" meant. Two things broke: document **search** looked up the
bare phrase, and the LLM had no **memory** of the previous turn.

## The fix — a two-step chain

```
1. condense   follow-up + recent history  ─►  a standalone question
2. answer     retrieve with the standalone question, then generate the answer
```

Step 1 ("condense") is one extra local LLM call that rewrites the follow-up into a
question that stands on its own. Step 2 is the normal retrieve-and-answer.

## Prerequisites

- RAG callable via `answer_question()` (task 03). Index built.

## Steps

- [x] Add a `CONDENSE_PROMPT` template + `format_condense_prompt()` to
      `config/settings.py`.
- [x] Add `condense_question(query, history)` to `utils/rag.py` and give
      `answer_question(query, n_results=3, history=None)` an optional `history`.
      When `history` is present it condenses first; otherwise it behaves exactly
      as the single-turn RAG (so the eval tools are unaffected).
- [x] Pass the recent turns from both interfaces: `app.py` (Streamlit
      `st.session_state`) and `main.py` (the console chat loop). Keep only the
      last few turns to bound the prompt size.

## Notes

- **Backward compatible:** with no `history`, the answer path is identical to
  before — the golden dataset and all three eval tools keep passing.
- **Trade-off:** a follow-up now makes **two** local LLM calls (condense +
  answer), so it is roughly twice as slow on CPU. A small local model also
  occasionally rewrites the standalone question imperfectly — the same
  local-model trade-off seen in the eval tasks.

## Files

`config/settings.py`, `utils/rag.py`, `app.py`, `main.py`

## Done when

A follow-up question in the chat (UI or console) is answered using the context of
the previous turns.

> Learning focus: **prompt chaining** — using the output of one LLM step (a
> rewritten question) as the input to the next (retrieve + answer).
