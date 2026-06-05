# promptfoo evaluation

Evaluate the local RAG with promptfoo — fully local, no API keys.

## The principles (anatomy of a promptfoo config)

A promptfoo run has four parts, all declared in `promptfooconfig.yaml`:

| Part | Means |
|------|-------|
| `prompts` | what gets sent to the provider — here just `{{question}}` |
| `providers` | what produces the answer — here our **custom Python provider** running the real RAG |
| `defaultTest` | options shared by every test — including the **judge** for model-graded checks |
| `tests` | a list of cases; each case = `vars` (the inputs) + `assert` (the checks) |

This config uses the **traditional declarative style**: every test case is written
out by hand under `tests:`, so the whole suite is visible in one file.

## Two kinds of assertion

| Type | How it decides pass/fail | Trustworthy? |
|------|--------------------------|--------------|
| `icontains` | deterministic — does the answer contain this substring (case-insensitive)? | exact, never flaky |
| `llm-rubric` | model-graded — the local judge LLM decides if the answer meets the rubric | approximate (a judge's opinion) |

The judge for `llm-rubric` is routed to the **local Ollama model** via
`defaultTest.options.provider` — so grading is free, offline, and needs no key.

## How it fits together

```
 promptfooconfig.yaml ── tests ──► question ──► rag_provider.py ──► answer_question() ──► answer
                                                   │
                          assertions check the answer:
                            • icontains  → contains the key fact?        (deterministic)
                            • llm-rubric → grounded / declines?           (local judge)
```

## Run it

From the **repo root**:

```bash
# 1. build the index if you haven't already
uv run python -c "from utils import process_documents_folder; process_documents_folder()"

# 2. run the evaluation (uses the project venv for the Python provider)
PROMPTFOO_PYTHON="$PWD/.venv/bin/python" npx -y promptfoo@latest eval -c eval/promptfoo/promptfooconfig.yaml

# 3. open the results in a browser
npx -y promptfoo@latest view
```

Tip: add `--filter-first-n 3` to step 2 for a quick partial run.

## What to look for

- **`contains-fact`** (deterministic) should be green for answerable cases.
- **`grounded`** (llm-rubric, local judge) scores whether the answer is supported.
- **`declines-unknown`** on the two unanswerable cases tests honesty — these may
  well **fail** at first, because the RAG prompt doesn't yet tell the model to
  decline. That's the harness doing its job: surfacing a real weakness to fix later.

> Each test runs the model locally, so a full run takes a few minutes on CPU.

## Files

| File | Role |
|------|------|
| `promptfooconfig.yaml` | the whole eval: prompts, provider, judge, and all test cases |
| `rag_provider.py` | custom provider — runs the real RAG so promptfoo evaluates the full pipeline |

> The test cases here are written declaratively. The golden dataset
> (`eval/dataset.yaml`) remains the shared source for the Python eval tools
> (DeepEval, Ragas) added in later tasks.
