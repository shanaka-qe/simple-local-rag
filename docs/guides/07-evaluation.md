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

You'll run three tools against the same RAG. They overlap on purpose — comparing
them is the point. They also demonstrate **two ways to hold the test cases**:

| Tool | Language | Test-case style | Focus |
|------|----------|-----------------|-------|
| **promptfoo** | Node / YAML | **Explicit** — 12 cases hand-written inline in the config | Deterministic checks (contains X?) + model-graded rubrics |
| **DeepEval** | Python | **Data-driven** — answerable cases loaded from `dataset.csv` | Faithfulness + answer-relevancy in a pytest runner |
| **Ragas** | Python | **Data-driven** — cases loaded from `dataset.csv` | RAG-specific metrics: retrieval vs. answer quality |

The **explicit** vs **data-driven** split is deliberate (see *Two styles, on
purpose* below): one golden dataset (`eval/dataset.csv`) feeds the Python tools,
while promptfoo keeps its suite visible in one file. Same cases, two patterns.

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

### Golden dataset (task 05 — ✅ built: `eval/dataset.csv`)

A flat CSV table — one row per case — that the Python tools read directly with the
standard-library `csv` module:

```csv
id,query,answerable,expected_answer,expected_contains,expected_context
quantum-director,"Who is the research director...?",true,"...Prof. Elena Rodriguez.",Elena Rodriguez,QCR-LAB-9847
nimbus-ceo-salary,"What is the salary of Nimbus Audio's CEO?",false,"The documents do not contain this information.",,
```

The unique markers in the sample docs make `expected_context` a **deterministic**
retrieval check — no judge needed for that part. Anchor it on a string in the
**same chunk** as the fact (the quantum doc's bottom-of-file marker lands in a
different chunk, so the cases use the header's `QCR-LAB-9847` instead). The file
also includes 2 `answerable: false` cases to test that the RAG declines rather
than invents an answer.

**Two styles, on purpose.** DeepEval and Ragas load their cases *from this CSV*
(`csv.DictReader`) — the **data-driven** style: the dataset lives in one file and
the test code stays generic. promptfoo instead writes every case out **inline** in
its YAML config — the **explicit** style: the whole suite is visible in one place.
Seeing both is the lesson; neither is "more correct".

### promptfoo (task 06 — ✅ built: `eval/promptfoo/`)

A **custom Python provider** runs the real RAG (`answer_question`), so promptfoo
evaluates the whole pipeline, not just the bare LLM. Test cases are written
**declaratively** under `tests:` (the traditional promptfoo style), and the judge
is routed to the **local** Ollama model:

```yaml
providers:
  - id: file://rag_provider.py          # returns {output: answer, metadata: {contexts}}
defaultTest:
  options:
    provider:
      text: { id: ollama:chat:llama3.1:8b }   # local judge
tests:
  - description: refund-window
    vars: { query: "What is the refund window in the returns policy?" }
    assert:
      - { type: icontains, value: "30 days" }                        # deterministic
      - type: context-faithfulness                                   # judged vs the chunks
        contextTransform: 'context.metadata.contexts.join("\n\n")'   # feed the judge the context
        threshold: 0     # informational only — does NOT gate (see caveat)
```

Each answerable case mixes a deterministic `icontains` (does the answer contain the
key fact?) with `context-faithfulness` (is the answer supported by the retrieved
chunks?). **Key subtlety:** a plain `llm-rubric` saying "grounded in the documents"
does *not* receive the documents — so it can't truly verify grounding;
`context-faithfulness` + `contextTransform` passes the chunks to the judge (and
requires the question in a `query` var).

⚠️ **Honest caveat — and why `grounded` is `threshold: 0`:** even correctly wired,
promptfoo's `context-faithfulness` scores **noisily** with a local judge — across
correct, grounded answers it ranged ~0.0–0.9, and neither a stronger judge (`phi4`)
nor fuller answers fixed it (Ragas scored the same answers ~1.0 — different
implementation). So we keep it **informational** (`threshold: 0`, never gates) to
*show* the limitation, and use the deterministic `contains-fact` as the real gate.
The lesson: reliable model-graded faithfulness needs a frontier judge; locally,
lean on deterministic checks. Run with `npx promptfoo eval` (see
`eval/promptfoo/README.md`).

### DeepEval (task 07 — ✅ built: `eval/deepeval/test_rag.py`)

pytest-style. The questions are **loaded from the shared `dataset.csv`** (the
data-driven style — only the answerable rows are used here); the judge is a local
Ollama model configured **in code** (`OllamaModel`) and passed to each metric — no
API key, no machine-global `set-ollama`:

```python
import csv
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.models import OllamaModel

JUDGE = OllamaModel(model="llama3.1:8b", base_url="http://localhost:11434")

# load the answerable cases from the shared golden dataset
with open("eval/dataset.csv", newline="") as f:
    QUESTIONS = [r["query"] for r in csv.DictReader(f) if r["answerable"] == "true"]

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
table. Cases are **loaded from the shared `dataset.csv`** (`expected_answer`
becomes the `reference`); local LLM + local embeddings, so nothing leaves your
machine:

```python
from ragas import EvaluationDataset, evaluate
from ragas.metrics import (Faithfulness, ResponseRelevancy,
                           LLMContextPrecisionWithReference, LLMContextRecall)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_ollama import ChatOllama

# each row built from dataset.csv: user_input, response, retrieved_contexts,
# reference (the CSV's expected_answer = ground truth)
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
