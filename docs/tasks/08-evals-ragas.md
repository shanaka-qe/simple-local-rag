# 08 — Evals with Ragas

**Status: ✅ Completed**

**Goal:** Learn Ragas — RAG-specific metrics — wired to local models (LLM judge +
embeddings), so nothing leaves your machine.

## Prerequisites

- RAG callable via `answer_question()` (task 03). Index built.

## Steps

- [x] Add dep: `uv add ragas`.
- [x] Create `eval/ragas/run_ragas.py` with explicit cases (question + `reference`):
      - run each through `answer_question()` to get the answer + contexts,
      - build an `EvaluationDataset` (`user_input`, `response`,
        `retrieved_contexts`, `reference`),
      - wrap the local LLM with `langchain-ollama` `ChatOllama` and the local
        HuggingFace embeddings via Ragas wrappers,
      - evaluate with `LLMContextPrecisionWithReference`, `LLMContextRecall`,
        `Faithfulness`, `ResponseRelevancy`.
- [x] Run: `uv run python eval/ragas/run_ragas.py` — prints aggregate + per-case scores.

## Notes

- Verified end-to-end fully locally. Typical run: faithfulness and context-recall
  high; answer-relevancy lower on terse answers (the local-judge trade-off).
- Ragas is migrating: v1.0 moves to `llm_factory` / `ragas.metrics.collections`.
  This uses the current 0.4.x API and silences the deprecation warnings. See
  `eval/ragas/README.md`.

## Files

`eval/ragas/run_ragas.py`

## Done when

Ragas prints a metrics table computed fully locally.

> Learning focus: how retrieval quality (context precision/recall) is scored
> separately from answer quality (faithfulness/relevancy).
