# 02 — Make search return results

**Status: ✅ Completed**

**Goal:** `search_documents()` currently *prints* its results. Make it *return*
them so the UI and the eval tools can use the output programmatically.

## Steps

- [x] Change `search_documents()` to return a structured result:
      `{"query": str, "chunks": list[str]}` (the retrieved chunk texts).
- [x] Keep printing optional (a `verbose=True` flag) so it can still be inspected on the console.
- [x] Update `main.py` to use the returned value instead of relying on prints.

## Files

`utils/document_search.py`, `utils/__init__.py`, `main.py`

## Done when

Calling `search_documents("...")` returns the retrieved chunks as data, and
`main.py` still works.

> Why this matters: every later piece (chat UI, promptfoo, DeepEval, Ragas) needs
> the retrieved chunks as a return value, not console text.
