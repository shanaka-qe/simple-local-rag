# 08 — Evals with Ragas

**Goal:** Learn Ragas — RAG-specific metrics — wired to local models (LLM judge +
embeddings), so nothing leaves your machine.

## Prerequisites

- Dataset from task 05. RAG callable via `answer_question()` (task 03).

## Steps

- [ ] Add dep: `uv add ragas datasets`.
- [ ] Create `eval/ragas/run_ragas.py`:
      - build a dataset of `question`, `answer`, `contexts`, `ground_truth`
        (from task 05 + `answer_question()`),
      - wrap the local LLM with `langchain-ollama` `ChatOllama`,
      - wrap embeddings with the local HuggingFace embeddings,
      - evaluate with `faithfulness`, `answer_relevancy`, `context_precision`,
        `context_recall`.
- [ ] Run: `uv run python eval/ragas/run_ragas.py` and print the scores table.

## Files

`eval/ragas/run_ragas.py`

## Done when

Ragas prints a metrics table computed fully locally.

> Learning focus: how retrieval quality (context precision/recall) is scored
> separately from answer quality (faithfulness/relevancy).
