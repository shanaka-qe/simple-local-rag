# promptfoo evaluation

Evaluate the local RAG against the golden dataset (`eval/dataset.yaml`) — fully
local, no API keys.

## How it fits together

```
 eval/dataset.yaml ──► generate_tests.py ──► test cases (question + assertions)
                                                   │
 question ──► rag_provider.py ──► answer_question() ──► answer
                                                   │
                          assertions check the answer:
                            • icontains  → does it contain the key fact?  (deterministic)
                            • llm-rubric → is it grounded / does it decline? (judged by local Ollama)
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
- **`declines-unknown`** on the two `answerable: false` cases tests honesty — these
  may well **fail** at first, because the RAG prompt doesn't yet tell the model to
  decline. That's the harness doing its job: surfacing a real weakness to fix later.

> Each test runs the model locally, so a full run takes a few minutes on CPU.
