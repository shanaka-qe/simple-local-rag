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

- **`contains-fact`** (deterministic) — the **gate**. Green for every answerable
  case; exact and never flaky.
- **`declines-unknown`** (`llm-rubric`) — the **gate** for the two unanswerable
  cases. Passes because the RAG prompt now tells the model to reply *"I don't know
  based on the provided documents"* when the answer isn't in the context.
- **`grounded`** (`context-faithfulness`) — **informational only** (`threshold: 0`),
  so it never fails the suite. The score is still computed and shown.
  ⚠️ **Do not trust this score with a local judge.** Across correct, grounded
  answers it ranges wildly (e.g. ~0.0 to ~0.9) — promptfoo's claim-based
  faithfulness needs a frontier judge; a local 8–14B model can't grade it reliably
  (tested with both `llama3.1:8b` and `phi4`, and with fuller answers). Ragas
  scored the same answers ~1.0 — different implementation. We keep it as a visible
  signal to *show* this limitation, not to gate on it.

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
