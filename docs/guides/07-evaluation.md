# 07 — Evaluation

← [Chat UI](06-chat-ui.md) · [Guides index](README.md) · next → [Reference](08-reference.md)

> **Status: ✅ built** — golden dataset ([05](../tasks/05-golden-dataset.md)),
> promptfoo ([06](../tasks/06-evals-promptfoo.md)), DeepEval
> ([07](../tasks/07-evals-deepeval.md)), and Ragas
> ([08](../tasks/08-evals-ragas.md)).

## Why evaluate a RAG?

A RAG can sound confident and still be wrong — it might retrieve the wrong chunks,
or write an answer the context doesn't support. Evaluation measures quality
**repeatably**, so you can tell whether a change made things better or worse.

Two different things get measured:

| Question | Measures |
|----------|----------|
| Did we fetch the *right* chunks? | **retrieval** quality |
| Does the answer stick to those chunks? | **answer** quality (faithfulness) |

## The golden dataset

Everything starts with a small set of fixed cases —
[task 05](../tasks/05-golden-dataset.md) — each with a question, the expected
answer (or key facts), and a marker the retrieved context should contain. This is
the yardstick all three tools measure against.

## Three tools, same RAG

You'll run three tools against the same system and dataset. They overlap on
purpose — comparing them is the point.

| Tool | Language | Style | Focus |
|------|----------|-------|-------|
| **promptfoo** | Node / YAML | Config-driven assertions | Deterministic checks (contains X? valid JSON?) + model-graded rubrics |
| **DeepEval** | Python | pytest-style | Metric assertions (faithfulness, answer-relevancy) in a test runner |
| **Ragas** | Python | Metrics over a dataset | RAG-specific metrics separating retrieval vs. answer quality |

## The local-judge trade-off

Metric scores that need a "judge" use your **local** model as the judge. That keeps
everything free and private — but a small local model is slower and less reliable
than a frontier judge. Noticing that trade-off is itself part of the lesson: treat
local-judged scores as directional, not absolute.

## What you'll learn

- The difference between deterministic checks and model-graded metrics.
- How retrieval quality and answer quality are scored separately.
- The practical cost/quality/privacy trade-offs of judging locally.

## Under the hood

> All four eval pieces are **✅ built** below: golden dataset (05), promptfoo (06),
> DeepEval (07), and Ragas (08).

### Golden dataset (task 05 — ✅ built: `eval/dataset.yaml`)

```yaml
cases:
  - id: quantum-director
    question: "Who is the research director of the Quantum Computing Research Laboratory?"
    answerable: true
    expected_answer: "The research director is Prof. Elena Rodriguez."
    expected_contains: ["Elena Rodriguez"]      # deterministic answer check
    expected_context: "QCR-LAB-9847"            # must appear in the retrieved chunks
```

The unique markers in the sample docs make `expected_context` a **deterministic**
retrieval check — no judge needed for that part. Anchor it on a string in the
**same chunk** as the fact (the quantum doc's bottom-of-file marker lands in a
different chunk, so the cases use the header's `QCR-LAB-9847` instead). The file
also includes 2 `answerable: false` cases to test that the RAG declines rather
than invents an answer.

### promptfoo (task 06 — ✅ built: `eval/promptfoo/`)

A **custom Python provider** runs the real RAG (`answer_question`), so promptfoo
evaluates the whole pipeline, not just the bare LLM. Test cases are written
**declaratively** under `tests:` (the traditional promptfoo style), and the
`llm-rubric` judge is routed to the **local** Ollama model:

```yaml
providers:
  - id: file://rag_provider.py          # runs the real RAG (retrieve + generate)
defaultTest:
  options:
    provider:
      text: { id: ollama:chat:llama3.1:8b }   # local judge for llm-rubric
tests:
  - description: refund-window
    vars: { question: "What is the refund window in the returns policy?" }
    assert:
      - { type: icontains, value: "30 days" }              # deterministic
      - { type: llm-rubric, value: "grounded; says 30 days" }  # local judge
```

Each test mixes a deterministic `icontains` (does the answer contain the key
fact?) with a model-graded `llm-rubric` (is it grounded / does it decline?).
Deterministic asserts never flake; `llm-rubric` uses the local model as judge.
Run with `npx promptfoo eval` (see `eval/promptfoo/README.md`).

### DeepEval (task 07 — ✅ built: `eval/deepeval/test_rag.py`)

pytest-style. Test cases are written out explicitly; the judge is a local Ollama
model configured **in code** (`OllamaModel`) and passed to each metric — no API
key, no machine-global `set-ollama`:

```python
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.models import OllamaModel

JUDGE = OllamaModel(model="llama3.1:8b", base_url="http://localhost:11434")

@pytest.mark.parametrize("question", QUESTIONS)
def test_rag(question):
    r = answer_question(question)
    tc = LLMTestCase(input=question, actual_output=r["answer"],
                     retrieval_context=r["contexts"])
    assert_test(tc, [FaithfulnessMetric(threshold=0.7, model=JUDGE),
                     AnswerRelevancyMetric(threshold=0.7, model=JUDGE)])
```

Run with `uv run deepeval test run eval/deepeval/test_rag.py`. Expect answer
-relevancy to sometimes dip below threshold with a small local judge — the
local-judge trade-off (see the local-judge note above).

### Ragas (task 08 — ✅ built: `eval/ragas/run_ragas.py`)

Not pytest or YAML — you build a dataset, run `evaluate(...)`, and read a scores
table. Local LLM + local embeddings, so nothing leaves your machine:

```python
from ragas import EvaluationDataset, evaluate
from ragas.metrics import (Faithfulness, ResponseRelevancy,
                           LLMContextPrecisionWithReference, LLMContextRecall)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import ChatOllama

# rows: user_input, response, retrieved_contexts, reference (ground truth)
dataset = EvaluationDataset.from_list([...])
judge   = LangchainLLMWrapper(ChatOllama(model="llama3.1:8b"))
emb     = LangchainEmbeddingsWrapper(local_embeddings)
evaluate(dataset,
         metrics=[LLMContextPrecisionWithReference(), LLMContextRecall(),
                  Faithfulness(), ResponseRelevancy()],
         llm=judge, embeddings=emb)
```

| Metric | Judges | Layer |
|--------|--------|-------|
| `LLMContextPrecisionWithReference` / `LLMContextRecall` | were the right/enough chunks retrieved? | **retrieval** |
| `Faithfulness` | answer supported by the contexts? | **answer** |
| `ResponseRelevancy` | answer addresses the question? | **answer** |

Ragas's value is this split: a low **retrieval** score vs. a low **answer** score
point you at different fixes. (Ragas is migrating its API in v1.0 — see
`eval/ragas/README.md`.)

All three route their "judge" to the local model — recall the trade-off above:
treat local-judged scores as directional, not absolute.

→ Next: [Reference](08-reference.md)
