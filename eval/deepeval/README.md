# DeepEval evaluation

Evaluate the local RAG with DeepEval — a **pytest-style** eval framework — fully
local, no API keys.

## The principles (the DeepEval pattern)

DeepEval treats each evaluation like a unit test:

| Step | In `test_rag.py` |
|------|------------------|
| 1. Run the system | `answer_question(question)` → answer + retrieved context |
| 2. Wrap the result | `LLMTestCase(input=…, actual_output=…, retrieval_context=…)` |
| 3. Assert against metrics | `assert_test(test_case, [FaithfulnessMetric(...), AnswerRelevancyMetric(...)])` |
| 4. Run the file | `deepeval test run eval/deepeval/test_rag.py` |

Test cases are written out **explicitly** (the traditional, learnable style) — the
questions are listed in the file, not generated from an external dataset.

## The metrics

| Metric | Question it answers | Needs |
|--------|---------------------|-------|
| `FaithfulnessMetric` | Is the answer supported by the retrieved context (not made up)? | `actual_output` + `retrieval_context` |
| `AnswerRelevancyMetric` | Does the answer actually address the question? | `input` + `actual_output` |

Both are **model-graded**: a judge LLM scores them. We configure that judge **in
code** as a local Ollama model (`OllamaModel(...)`), so the suite is reproducible
for anyone who clones — no API key, no machine-global setup.

## Run it

From the **repo root**:

```bash
# 1. build the index if you haven't already
uv run python -c "from utils import process_documents_folder; process_documents_folder()"

# 2. run the eval suite
uv run deepeval test run eval/deepeval/test_rag.py
```

Tip: add `-k "refund"` to run a single case.

## Reading the results & the local-judge trade-off

Each metric prints a **score** (0–1) and pass/fail against its `threshold` (0.7).

⚠️ Expect some answerable cases to dip **below threshold on answer-relevancy**. A
small local judge is stricter and noisier than a frontier model — e.g. a correct
but terse answer like "30 days" can score ~0.5. This is the lesson, not a bug:

- treat local-judged scores as **directional, not absolute**
- in practice you'd use a stronger judge, **tune the thresholds**, or make the RAG
  answers more complete

## Files

| File | Role |
|------|------|
| `test_rag.py` | the pytest suite: explicit questions → `LLMTestCase` → metric assertions, judged locally |

> The golden dataset (`eval/dataset.yaml`) remains the shared reference; this suite
> lists its answerable questions explicitly for clarity.
