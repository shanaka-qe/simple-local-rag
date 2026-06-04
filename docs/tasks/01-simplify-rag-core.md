# 01 — Simplify the RAG core

**Status: ✅ Completed**

**Goal:** Strip the ingestion pipeline down to `.md` files only and remove unused
code/dependencies so the rest is easy to build on.

## Steps

- [x] In `utils/document_processor.py`, remove `load_pdf_file()` and the PDF branch.
- [x] Restrict `supported_extensions` to `['.md']`.
- [x] Replace the hardcoded `"./data/chroma_db"` paths with `settings.CHROMA_DIR`
      (in `clear_chroma_db`, `create_embeddings_and_save`, and `document_search.py`).
- [x] In `config/settings.py`, remove the unused `LLM_MODEL_PATH` and `LLM_DEVICE`
      (and the now-dead `get_llm_model_path()` getter).
- [x] In `pyproject.toml`, remove `faiss-cpu`, `pypdf`, `pymupdf`. Run `uv sync`.
- [x] Remove `data/documents/sample-document.pdf` and `sample-text.txt`; keep the
      `.md` sample (add 1–2 more `.md` files if you like).
- [x] Run `uv run python main.py` — it should ingest only `.md` and still search.

## Files

`utils/document_processor.py`, `utils/document_search.py`, `config/settings.py`,
`pyproject.toml`, `data/documents/`

## Done when

`main.py` runs end-to-end on `.md` files only, with no PDF/faiss code or deps left.
