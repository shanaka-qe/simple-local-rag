# 05 — Build a golden eval dataset

**Status: ✅ Completed**

**Goal:** A small set of question / expected-answer pairs to evaluate the RAG
against. All three eval tools (06–08) read from this.

## Steps

- [x] Create `eval/dataset.yaml` with 12 cases. Each case:
      - `id`, `question`, `answerable`
      - `expected_answer` (ground truth) and `expected_contains` (deterministic substrings)
      - `expected_context` (a marker that should appear in retrieved chunks)
- [x] Base the cases on the sample `.md` files and anchor `expected_context` on a
      string that lives in the **same chunk** as the answer (e.g. `QCR-LAB-9847`
      for the quantum facts — the bottom-of-doc marker is split into another chunk).
- [x] Include 2 "should not answer" cases (info not in the docs) to test that the
      system doesn't make things up.

## Notes

- Validated: all 10 answerable cases reliably retrieve their `expected_context`
  marker in the top 3 chunks.
- Lesson captured: a unique marker only works as a retrieval check if chunking
  keeps it in the same chunk as the fact being asked about.

## Files

`eval/dataset.yaml`

## Done when

A reusable dataset file exists that the eval tasks can load.

> Keep all data synthetic — no real or private content (this repo is public).
