# 07 — Evals with DeepEval

**Goal:** Learn DeepEval — a pytest-style eval framework — using a local Ollama
model as the judge (no paid API).

## Prerequisites

- Dataset from task 05. RAG callable via `answer_question()` (task 03).

## Steps

- [ ] Add dep: `uv add deepeval`.
- [ ] Point DeepEval's judge at local Ollama: `deepeval set-ollama llama3.1:8b`.
- [ ] Create `eval/deepeval/test_rag.py`:
      - load `dataset.yaml`, run each question through `answer_question()`,
      - build `LLMTestCase(input, actual_output, retrieval_context)`,
      - assert with `AnswerRelevancyMetric` and `FaithfulnessMetric`.
- [ ] Run: `uv run deepeval test run eval/deepeval/test_rag.py`.

## Files

`eval/deepeval/test_rag.py`

## Done when

The test run produces metric scores per case using the local judge.

> Learning focus: faithfulness vs. answer-relevancy, and the trade-off of using a
> small local model as the judge (slower, less reliable than a frontier judge).
