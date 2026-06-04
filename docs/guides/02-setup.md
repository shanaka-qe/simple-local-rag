# 02 — Setup

← [Concepts](01-concepts.md) · [Guides index](README.md) · next → [Codebase tour](03-codebase-tour.md)

## Prerequisites

| Need | Why | Check |
|------|-----|-------|
| Python 3.13+ | runtime | `python3 --version` |
| [uv](https://docs.astral.sh/uv/) | package manager | `uv --version` |
| [Ollama](https://ollama.com) | runs the local LLM (needed from task 03 on) | `ollama --version` |

### Install uv (if needed)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Install dependencies

```bash
uv sync
```

This creates a local virtual environment and installs everything from
`pyproject.toml`.

## Local model (for generation, task 03+)

```bash
ollama pull llama3.1:8b   # the default answer-writing model
ollama serve              # start the local model server (often already running)
```

## First run

```bash
uv run python main.py
```

> **The first run downloads the embedding model once** (~640 MB, HuggingFace
> `mxbai-embed-large-v1`). After that everything runs **offline** — no account, no
> API key, no cost.

## Under the hood

- **`uv sync`** resolves the dependencies in `pyproject.toml` against the pinned
  `uv.lock` and installs them into a project-local `.venv`. `uv run <cmd>` then runs
  inside that env without you activating it manually.
- The embedding model is cached by HuggingFace under `~/.cache/huggingface/hub/`
  (≈640 MB). It downloads once; delete that folder to force a re-download.
- Ollama runs a local HTTP server on `http://localhost:11434`. Verify it:
  ```bash
  curl -s http://localhost:11434/api/tags   # lists pulled models if the server is up
  ollama list                                # same, via the CLI
  ```
- After the first model downloads, nothing here needs the network — a quick way to
  confirm the "fully local" claim is to run with Wi-Fi off.

→ Next: [Codebase tour](03-codebase-tour.md)
