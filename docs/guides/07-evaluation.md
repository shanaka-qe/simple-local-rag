# 07 — Evaluation

← [Chat UI](06-chat-ui.md) · [Guides index](README.md) · next → [Reference](08-reference.md)

> **Status: 🚧 planned** — build it with tasks
> [05](../tasks/05-golden-dataset.md) · [06](../tasks/06-evals-promptfoo.md) ·
> [07](../tasks/07-evals-deepeval.md) · [08](../tasks/08-evals-ragas.md).

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

## Under the hood (intended design)

> Built in tasks [05–08](../tasks/05-golden-dataset.md); the planned shapes follow.

### Golden dataset (task 05)

```yaml
- question: "Who leads the quantum computing lab?"
  expected_answer: "Prof. Elena Rodriguez"
  expected_context: "QUANTUM_MD_MARKER_4729"   # must appear in the retrieved chunks
```

The unique markers in the sample docs make `expected_context` a **deterministic**
retrieval check — no judge needed for that part.

### promptfoo (task 06)

YAML config; the provider points at local Ollama; assertions mix deterministic and
model-graded:

```yaml
providers: [ollama:chat:llama3.1:8b]
tests:
  - vars: { question: "Who leads the quantum computing lab?" }
    assert:
      - type: contains
        value: "Elena Rodriguez"
      - type: llm-rubric                 # judged by the same local model
        value: "Answer is grounded in the provided context"
```

Deterministic asserts (`contains`, `is-json`, `equals`) cost nothing and never
flake; `llm-rubric` uses the local model as judge. Run with `npx promptfoo eval`.

### DeepEval (task 07)

pytest-style; judge set to local Ollama (`deepeval set-ollama llama3.1:8b`):

```python
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric

r  = answer_question(case["question"])
tc = LLMTestCase(
    input=case["question"],
    actual_output=r["answer"],
    retrieval_context=r["contexts"],
)
assert_test(tc, [AnswerRelevancyMetric(threshold=0.7),
                 FaithfulnessMetric(threshold=0.7)])
```

### Ragas (task 08)

Metrics over a dataset, with local LLM + embeddings wrappers so nothing leaves
your machine:

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import ChatOllama

judge = LangchainLLMWrapper(ChatOllama(model="llama3.1:8b"))
emb   = LangchainEmbeddingsWrapper(hf_embeddings)   # the same local embeddings
# dataset rows: question, answer, contexts, ground_truth
evaluate(dataset,
         metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
         llm=judge, embeddings=emb)
```

| Metric | Judges | Needs |
|--------|--------|-------|
| `context_precision` / `context_recall` | retrieval | ground-truth + retrieved contexts |
| `faithfulness` | answer vs. contexts | answer + contexts |
| `answer_relevancy` | answer vs. question | answer + embeddings |

All three route their "judge" to the local model — recall the trade-off above:
treat local-judged scores as directional, not absolute.

→ Next: [Reference](08-reference.md)
