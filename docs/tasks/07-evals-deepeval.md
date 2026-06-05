# 07 — Evals with DeepEval

**Status: ✅ Completed**

**Goal:** Learn DeepEval — a pytest-style eval framework — using a local Ollama
model as the judge (no paid API).

## Prerequisites

- RAG callable via `answer_question()` (task 03). Index built.

## Steps

- [x] Add dep: `uv add deepeval`.
- [x] Configure the judge as a local Ollama model **in code**
      (`OllamaModel(model="llama3.1:8b", ...)` passed to each metric) — reproducible,
      no machine-global `set-ollama` needed.
- [x] Create `eval/deepeval/test_rag.py` the traditional pytest way:
      explicit questions → `answer_question()` → `LLMTestCase(input, actual_output,
      retrieval_context)` → `assert_test(...)`.
- [x] Metrics: `FaithfulnessMetric` and `AnswerRelevancyMetric` (threshold 0.7).
- [x] Run: `uv run deepeval test run eval/deepeval/test_rag.py`.

## Notes

- Verified end-to-end: `deepeval test run` executes the suite and both metrics are
  judged by the local Ollama model (no API key, no network).
- Faithfulness passes; **answer-relevancy can dip below 0.7** for terse answers
  with a small local judge — the local-judge trade-off (treat scores as
  directional; tune thresholds). See `eval/deepeval/README.md`.

## Files

`eval/deepeval/test_rag.py`

## Done when

The test run produces metric scores per case using the local judge.

> Learning focus: faithfulness vs. answer-relevancy, and the trade-off of using a
> small local model as the judge (slower, less reliable than a frontier judge).
