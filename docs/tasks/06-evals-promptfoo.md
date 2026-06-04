# 06 — Evals with promptfoo

**Status: ✅ Completed**

**Goal:** Learn promptfoo — a YAML-driven eval runner (Node) — against the RAG.
Good first eval tool: simple, mostly deterministic assertions.

## Prerequisites

- Node + `npx` available. Dataset from task 05. Index built.

## Steps

- [x] Add a custom Python provider (`eval/promptfoo/rag_provider.py`) so promptfoo
      evaluates the real RAG (`answer_question`), not just the bare LLM.
- [x] Generate tests from the golden dataset (`generate_tests.py`) — single source
      of truth, no duplicated test file.
- [x] `promptfooconfig.yaml`: custom provider + `llm-rubric` grader routed to the
      local Ollama model (`defaultTest.options.provider.text`).
- [x] Assertions: `icontains` (key facts, deterministic) + `llm-rubric` (grounded /
      declines, judged locally).
- [x] Run from repo root:
      `PROMPTFOO_PYTHON="$PWD/.venv/bin/python" npx -y promptfoo@latest eval -c eval/promptfoo/promptfooconfig.yaml`
      then `npx -y promptfoo@latest view`.

## Notes

- Verified end-to-end on a subset: deterministic checks pass and the local Ollama
  grader runs (no API key, no network).
- See `eval/promptfoo/README.md` for the full run instructions.

## Files

`eval/promptfoo/promptfooconfig.yaml`

## Done when

`npx promptfoo eval` runs locally and produces a pass/fail table per case.

> Learning focus: deterministic assertions vs. model-graded assertions, and how a
> local model can act as the judge.
