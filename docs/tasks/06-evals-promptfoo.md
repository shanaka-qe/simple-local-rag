# 06 — Evals with promptfoo

**Goal:** Learn promptfoo — a YAML-driven eval runner (Node) — against the RAG.
Good first eval tool: simple, mostly deterministic assertions.

## Prerequisites

- Node + `npx` available. Dataset from task 05.

## Steps

- [ ] Create `eval/promptfoo/promptfooconfig.yaml`:
      - provider: `ollama:chat:llama3.1:8b` (local), embeddings provider local too.
      - tests built from `dataset.yaml`.
      - assertions: `contains` (key facts), `is-json` where relevant, and one or
        two `llm-rubric` model-graded checks (judge = the local Ollama model).
- [ ] Run: `npx promptfoo eval` then `npx promptfoo view` to see results.

## Files

`eval/promptfoo/promptfooconfig.yaml`

## Done when

`npx promptfoo eval` runs locally and produces a pass/fail table per case.

> Learning focus: deterministic assertions vs. model-graded assertions, and how a
> local model can act as the judge.
