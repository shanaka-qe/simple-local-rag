# promptfoo evaluation

Evaluate the local RAG with promptfoo — fully local, no API keys.

## The principles (anatomy of a promptfoo config)

A promptfoo run has four parts, all declared in `promptfooconfig.yaml`:

| Part | Means |
|------|-------|
| `prompts` | what gets sent to the provider — here just `{{query}}` |
| `providers` | what produces the answer — here our **custom Python provider** running the real RAG |
| `defaultTest` | options shared by every test — including the **judge** for model-graded checks |
| `tests` | a list of cases; each case = `vars` (the inputs) + `assert` (the checks) |

This config uses the **traditional declarative style**: every test case is written
out by hand under `tests:`, so the whole suite is visible in one file.

## Three kinds of assertion

| Type | How it decides pass/fail | Trustworthy? |
|------|--------------------------|--------------|
| `icontains` | deterministic — does the answer contain this substring (case-insensitive)? | exact, never flaky |
| `context-faithfulness` | model-graded — is the answer supported by the **retrieved chunks**? | approximate; needs the context |
| `llm-rubric` | model-graded — free-form judgement (used for the "should decline" checks) | approximate (a judge's opinion) |

Model-graded checks are judged by the **local Ollama model** via
`defaultTest.options.provider` — free, offline, no key.

**Giving the judge the context (important):** `context-faithfulness` must see the
retrieved chunks to do its job. Our provider returns them in `metadata.contexts`,
and we pass them to the judge with `contextTransform`:

```yaml
- type: context-faithfulness
  contextTransform: 'context.metadata.contexts.join("\n\n")'  # provider metadata -> judge
  threshold: 0.7
```

`context-faithfulness` also requires the question to live in a `query` var — that's
why the cases use `vars.query` (not `question`). A plain `llm-rubric` saying
"grounded in the documents" does **not** receive the documents, so it can't really
verify grounding — use `context-faithfulness` for that.

## How it fits together

```
 promptfooconfig.yaml ── tests ──► query ──► rag_provider.py ──► answer + contexts(metadata)
                                                   │
                          assertions check the answer:
                            • icontains            → contains the key fact?            (deterministic)
                            • context-faithfulness → supported by the retrieved chunks? (local judge + context)
                            • llm-rubric           → did it decline?                    (local judge)
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

- **`contains-fact`** (deterministic) should be green for answerable cases — this
  is the reliable gate.
- **`grounded`** (`context-faithfulness`, local judge) scores whether the answer is
  supported by the retrieved chunks. ⚠️ Treat it as **directional**: on very terse
  factual answers (e.g. `"$28.4 million USD"`) it often scores low even though the
  fact *is* in the context — and this persists even with a stronger judge
  (tested with `phi4`). Promptfoo's claim-based faithfulness is simply unreliable on
  bare-fact answers (Ragas's faithfulness scored the same answers 1.0 — different
  implementation). The fix is real but partial: the judge now *sees* the context;
  reliability of the score is a separate, model-dependent limitation.
- **`declines-unknown`** on the two unanswerable cases tests honesty — these may
  well **fail**, because the RAG prompt doesn't tell the model to decline. The
  harness surfacing a real weakness.

**Takeaway:** for hard facts, trust the deterministic `contains-fact`. Use
model-graded faithfulness as a directional signal, not a hard gate — or raise
answer completeness / judge quality if you need it to be reliable.

> Each test runs the model locally, so a full run takes a few minutes on CPU.

## Files

| File | Role |
|------|------|
| `promptfooconfig.yaml` | the whole eval: prompts, provider, judge, and all test cases |
| `rag_provider.py` | custom provider — runs the real RAG so promptfoo evaluates the full pipeline |

> The test cases here are written declaratively. The golden dataset
> (`eval/dataset.yaml`) remains the shared source for the Python eval tools
> (DeepEval, Ragas) added in later tasks.
