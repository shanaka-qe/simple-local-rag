# 02 — Make search return results

**Goal:** `search_documents()` currently *prints* its results. Make it *return*
them so the UI and the eval tools can use the output programmatically.

## Steps

- [ ] Change `search_documents()` to return a structured result, e.g.:
      `{"query": str, "chunks": list[str]}` (the retrieved chunk texts).
- [ ] Keep printing optional (e.g. a `verbose=True` flag) so `main.py` still reads nicely.
- [ ] Update `main.py` to use the returned value instead of relying on prints.

## Files

`utils/document_search.py`, `utils/__init__.py`, `main.py`

## Done when

Calling `search_documents("...")` returns the retrieved chunks as data, and
`main.py` still works.

> Why this matters: every later piece (chat UI, promptfoo, DeepEval, Ragas) needs
> the retrieved chunks as a return value, not console text.
