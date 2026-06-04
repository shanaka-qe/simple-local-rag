# 05 — Build a golden eval dataset

**Goal:** A small set of question / expected-answer pairs to evaluate the RAG
against. All three eval tools (06–08) read from this.

## Steps

- [ ] Create `eval/dataset.yaml` (or `.json`) with ~8–12 cases. Each case:
      - `question`
      - `expected_answer` (or key facts the answer must contain)
      - `expected_context` (a keyword/marker that should appear in retrieved chunks)
- [ ] Base the cases on the sample `.md` files — they contain unique markers
      (e.g. `QUANTUM_MD_MARKER_4729`) that make retrieval checks deterministic.
- [ ] Include a couple of "should not answer" cases (info not in the docs) to test
      that the system doesn't make things up.

## Files

`eval/dataset.yaml`

## Done when

A reusable dataset file exists that the eval tasks can load.

> Keep all data synthetic — no real or private content (this repo is public).
