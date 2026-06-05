# Ragas evaluation

Evaluate the local RAG with Ragas — **RAG-specific metrics** that separate
*retrieval* quality from *answer* quality — fully local, no API keys.

## The principles (the Ragas pattern)

Ragas isn't pytest or YAML. You build a dataset, run `evaluate(...)`, and read a
scores table:

| Step | In `run_ragas.py` |
|------|-------------------|
| 1. Run the system | `answer_question(question)` → answer + retrieved context |
| 2. Build a sample | `{user_input, response, retrieved_contexts, reference}` |
| 3. Assemble the dataset | `EvaluationDataset.from_list([...])` |
| 4. Evaluate | `evaluate(dataset, metrics, llm=<local>, embeddings=<local>)` |

`reference` is the **ground-truth answer** the retrieval metrics are scored
against. The judge LLM (`ChatOllama`) and embeddings (our local mxbai model) are
both local, so nothing leaves the machine.

## The metrics — retrieval vs. answer

| Metric | Measures | Layer |
|--------|----------|-------|
| `LLMContextPrecisionWithReference` | Were the *right* chunks ranked highly? | **retrieval** |
| `LLMContextRecall` | Did retrieval fetch *enough* of the needed info? | **retrieval** |
| `Faithfulness` | Does the answer stick to the retrieved context? | **answer** |
| `ResponseRelevancy` | Does the answer actually address the question? | **answer** |

This separation is Ragas's whole point: a low **context** score means fix
*retrieval*; a low **faithfulness** means the model is drifting from its sources.

## Run it

From the **repo root**:

```bash
# 1. build the index if you haven't already
uv run python -c "from utils import process_documents_folder; process_documents_folder()"

# 2. run the evaluation (a few minutes on CPU)
uv run python eval/ragas/run_ragas.py
```

It prints the aggregate scores and a per-case table.

## Reading the results & the local-judge trade-off

Typical local run: high `faithfulness` and `context_recall`, with
`answer_relevancy` lower (~0.5–0.9) on terse answers — the same small-local-judge
strictness seen in DeepEval. Treat scores as **directional**, not absolute; a
stronger judge or fuller answers raise them.

## A note on API churn (a real lesson)

Ragas is migrating: v1.0 will move from `LangchainLLMWrapper` + `ragas.metrics`
to `llm_factory` + `ragas.metrics.collections`. This repo uses the current,
widely-documented 0.4.x API and silences the deprecation warnings. When you read
Ragas tutorials, check which API version they target — the LLM-eval ecosystem
moves fast.

## Files

| File | Role |
|------|------|
| `run_ragas.py` | builds the dataset from explicit cases, evaluates with local LLM + embeddings, prints the scores |
