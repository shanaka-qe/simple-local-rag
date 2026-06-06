# 03 — Codebase tour

← [Setup](02-setup.md) · [Guides index](README.md) · next → [Using the RAG](04-using-the-rag.md)

The map first (architecture, layout, what each file does), then a line-by-line
walkthrough of every core file. Python idioms are explained as they appear.

## Architecture

```
  data/documents/*.md
        │  load
        ▼
     chunk (≈500 chars)
        │  embed  (HuggingFace mxbai — local, free)
        ▼
     ChromaDB  (local, persistent, cosine similarity)
        │
   question ──embed──► search ──► top matching chunks
        │                               │
        │                       prompt template
        ▼                               ▼
   Streamlit chat UI ◄──── answer ◄── local LLM (Ollama)
                                        │
            evaluation ─────────────────┘
            promptfoo · DeepEval · Ragas
```

Everything in this diagram runs locally.

## Folder layout

```
local-rag-solution/
├── main.py                      # interactive console (build index, search, ask, chat)
├── app.py                       # Streamlit web UI (browser chat)
├── config/
│   └── settings.py              # all settings in one place
├── utils/
│   ├── document_processor.py    # load → chunk → embed → store (builds the DB)
│   ├── document_search.py       # turn a question into a search over the DB
│   └── rag.py                   # retrieve + generate an answer (full RAG)
├── data/
│   ├── documents/               # put your .md files here
│   └── chroma_db/               # the vector database (auto-created, git-ignored)
└── docs/
    ├── guides/                  # these guides
    └── tasks/                   # the build roadmap
```

## What each file does

| File | Plain-English job |
|------|-------------------|
| `config/settings.py` | One place for every setting: embedding model, chunk size (500) / overlap (100), where ChromaDB lives, the collection name, prompt templates. |
| `utils/document_processor.py` | The ingestion pipeline: read files → split into chunks → create embeddings → save to ChromaDB. Rebuilds the collection each time you build the index. |
| `utils/document_search.py` | Takes a question, embeds it, asks ChromaDB for the closest chunks. |
| `utils/rag.py` | The full RAG: retrieve chunks, build the prompt, call the local LLM, return `{answer, contexts}`. |
| `main.py` | Interactive console: build the index, search, ask a question, or chat. |
| `app.py` | Streamlit web UI: a browser chat page over the same RAG. |

> The `utils/*.py` files are libraries imported by `main.py`. Running them directly
> does nothing on their own — use `main.py`.

## Where LangChain is used

LangChain handles three of the four RAG stages; ChromaDB is used through its own
native client (not LangChain's wrapper).

| Stage | LangChain piece |
|-------|-----------------|
| Chunking | `CharacterTextSplitter` (`document_processor.py`) |
| Embedding (docs + query) | `HuggingFaceEmbeddings` (`document_processor.py`, `document_search.py`) |
| Generation | `OllamaLLM` (`rag.py`) |
| Vector store | **not** LangChain — the raw `chromadb` client |

---

# Walkthrough (line by line)

Reading order — each file builds on the one before:

```
 settings.py        the config every file reads
   → document_processor.py   BUILD the index
   → document_search.py      RETRIEVE chunks
   → rag.py                  GENERATE an answer
   → __init__.py             the public API ("from utils import ...")
   → main.py                 the terminal console
   → app.py                  the browser UI
```

## 1. `config/settings.py` — the single config object

```python
class Settings:
    EMBEDDING_MODEL = "mixedbread-ai/mxbai-embed-large-v1"  # text → numbers model
    EMBEDDING_DEVICE = "cpu"                                # "cuda" with a GPU
    CHROMA_DIR = "./data/chroma_db"                         # where the vector DB lives
    COLLECTION_NAME = "documents"                           # the "table" inside it
    CHUNK_SIZE = 500                                        # characters per chunk
    CHUNK_OVERLAP = 100                                     # shared chars between chunks
    OLLAMA_MODEL = "llama3.1:8b"                            # local LLM for answers
    OLLAMA_BASE_URL = "http://localhost:11434"             # local Ollama server
    LLM_TEMPERATURE = 0.5                                   # 0 = strict, higher = creative
```

- A **class** groups related data and functions. These are class attributes — the
  default settings every file reads.

```python
    RAG_PROMPT = """Context: {context}

Question: {question}

Answer:"""
    QUERY_PROMPT = "Represent this sentence for searching relevant passages:"
```

- `RAG_PROMPT` is the **prompt template** sent to the LLM; `{context}` and
  `{question}` are placeholders filled in later.
- `QUERY_PROMPT` is a prefix the mxbai model wants in front of **search queries**
  (it was trained that way). Documents are embedded without it; questions with it.

```python
    def __init__(self):
        Path("./data").mkdir(exist_ok=True)
        Path("./data/chroma_db").mkdir(exist_ok=True)
        Path("./data/documents").mkdir(exist_ok=True)
```

- `__init__` is the **constructor** — it runs when the object is created. It makes
  the `data/` folders if missing (`exist_ok=True` = don't error if they exist).

```python
    def format_query(self, query):
        return f"{self.QUERY_PROMPT} {query}"               # adds the mxbai prefix

    def format_rag_prompt(self, context, question):
        return self.RAG_PROMPT.format(context=context, question=question)

settings = Settings()                                       # the ONE shared instance
```

- `f"..."` is an **f-string** — text with `{...}` placeholders filled in.
- The last line creates **one** `Settings` object named `settings`. Every other file
  does `from config.settings import settings` and shares this same object.

## 2. `utils/document_processor.py` — BUILD the index

```python
sys.path.append(str(Path(__file__).parent.parent))   # add the project root to the path
from config.settings import settings
```

- `__file__` is this file's path; `.parent.parent` is the project root. Adding it to
  `sys.path` lets `from config.settings import settings` work from anywhere.

### `clear_chroma_db()`

```python
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    try:
        client.delete_collection(settings.COLLECTION_NAME)
        print("🗑️ Deleted existing collection")
    except Exception:
        print("📁 No existing collection found")
```

- A **try/except**: try to delete the collection; if it doesn't exist, the `except`
  catches the error instead of crashing. We delete via the **client API** (not by
  removing files) so it stays consistent in the long-running Streamlit app, where
  the ChromaDB client is cached in memory.

### `load_documents_from_folder(folder_path)`

```python
    documents = []
    supported_extensions = ['.md']
    for file_path in folder.rglob('*'):                       # walk the folder recursively
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    documents.append(content)                 # one big string per file
```

- `rglob('*')` walks every file in every subfolder. Only `.md` files are read. Each
  file's text becomes one entry in the `documents` list.

### `chunk_documents(documents)`

```python
    text_splitter = CharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    all_chunks = []
    for doc in documents:
        chunks = text_splitter.split_text(doc)
        all_chunks.extend(chunks)                              # flatten into one list
```

- Splits each document into ~500-char chunks (100 shared) and flattens them into one
  list. (3 documents → 17 chunks for the sample data.)

### `create_embeddings_and_save(chunks, ...)` — the core

```python
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    try:
        client.delete_collection(collection_name)              # defensive clean rebuild
    except Exception:
        pass
    collection = client.create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"})  # cosine similarity + HNSW index

    embeddings_model = HuggingFaceEmbeddings(
        model_name=settings.get_embedding_model(),
        model_kwargs={"device": settings.EMBEDDING_DEVICE})
    chunk_embeddings = embeddings_model.embed_documents(chunks)   # 17 chunks → 17 vectors (1024 floats each)

    chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]        # list comprehension: chunk_0, chunk_1, ...
    collection.add(documents=chunks, embeddings=chunk_embeddings, ids=chunk_ids)  # store all three, aligned
```

- `pass` means "do nothing." A **list comprehension** is a compact loop that builds a
  list. `collection.add(...)` persists three aligned things per chunk: the **text**,
  its **vector**, and its **id**.

### `process_documents_folder(...)` — the orchestrator

```python
    clear_chroma_db()                                   # 1. wipe old collection
    documents = load_documents_from_folder(folder_path) # 2. read .md files
    if not documents:
        return None                                     #    nothing to build
    chunks = chunk_documents(documents)                 # 3. split
    collection = create_embeddings_and_save(chunks, ...) # 4. embed + store
    return collection
```

- The "build the index" button. Returns `None` if no documents were found (callers
  treat that as "nothing built").

## 3. `utils/document_search.py` — RETRIEVE chunks

```python
@lru_cache(maxsize=1)
def get_embeddings_model():
    return HuggingFaceEmbeddings(
        model_name=settings.get_embedding_model(),
        model_kwargs={"device": settings.EMBEDDING_DEVICE})
```

- `@lru_cache` is a **decorator** that remembers the function's result. `maxsize=1`
  stores one. Effect: the heavy embedding model loads **once** per process and is
  reused — this is what keeps the chat loop and UI responsive.

### `search_documents(query, n_results=3, verbose=False)`

```python
    client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
    collection = client.get_collection(settings.COLLECTION_NAME)  # read-only: get, not create

    embeddings_model = get_embeddings_model()                     # cached
    formatted_query = settings.format_query(query)                # add mxbai prefix
    query_embedding = embeddings_model.embed_query(formatted_query)  # question → 1024 numbers

    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    chunks = results["documents"][0]                              # the matched chunk texts, best first

    if verbose:
        ... print each chunk ...

    return {"query": query, "chunks": chunks}                     # RETURNS data, not prints
```

- Embeds the question into the same space as the chunks, asks ChromaDB for the
  closest `n_results`, and **returns** them. The return value is what the chat UI and
  the eval tools consume. `collection.query(...)` returns parallel lists batched per
  query; `results["documents"][0]` is the matched chunk texts (best first).

### `get_index_status()`

```python
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
        collection = client.get_collection(settings.COLLECTION_NAME)
        return {"exists": True, "count": collection.count()}
    except Exception:
        return {"exists": False, "count": 0}
```

- Reports whether the index exists and how many chunks it holds — used by the console
  and UI to decide whether to prompt you to build first.

## 4. `utils/rag.py` — GENERATE an answer (the full RAG loop)

```python
def answer_question(query: str, n_results: int = 3, history=None) -> dict:
    # CHAIN STEP 1: rewrite a follow-up into a standalone question (only if there
    # is prior conversation). With no history this is skipped — single-turn RAG.
    search_query = condense_question(query, history) if history else query

    result = search_documents(search_query, n_results=n_results)   # retrieve
    contexts = result["chunks"]

    prompt = settings.format_rag_prompt(                           # build the prompt
        context="\n\n".join(contexts), question=search_query)

    answer = _get_llm().invoke(prompt)                # CHAIN STEP 2: generate (local)
    return {"answer": answer, "contexts": contexts}   # return both
```

- `"\n\n".join(contexts)` glues the chunks into one text block for the `{context}`
  slot. `_get_llm().invoke(prompt)` sends the prompt to local Ollama and returns
  the answer (`_get_llm()` just builds the `OllamaLLM`, reused by both chain steps).
- **`history` and the chain:** when the caller passes recent chat turns,
  `condense_question` makes one extra LLM call that rewrites a vague follow-up
  ("how long is it?") into a standalone question before search. No history → the
  step is skipped and behaviour is unchanged (so the eval tools are unaffected).
  See [task 09](../tasks/09-conversational-rag.md).
- Returning `contexts` alongside `answer` is deliberate: the UI shows them as
  "sources," and the eval tools score the answer against them (faithfulness).

## 5. `utils/__init__.py` — the public API

```python
from .document_processor import (process_documents_folder, clear_chroma_db, load_documents_from_folder)
from .document_search import (search_documents, get_index_status)
from .rag import (answer_question)
__all__ = [ ... ]
```

- Runs on `import utils`. Re-exports the key functions so callers write
  `from utils import answer_question` instead of the longer module path. `__all__`
  lists the intended public names.

## 6. `main.py` — the terminal console

A plain input/print loop (no Streamlit here).

```python
def require_index() -> bool:                                 # guard for options 3/4/5
    if not get_index_status()["exists"]:
        print("⚠️ No index yet — choose option 1 to build it first.")
        return False
    return True
```

- A **guard**: search/ask/chat bail out early if no index exists.

```python
def chat():
    history = []
    while True:
        query = input("\nYou: ").strip()                     # input() reads what you type
        if not query or query.lower() in {"exit", "quit"}:
            break                                            # leave the loop
        result = print_answer(query, history)
        history.append({"role": "user", "content": query})  # remember this turn
        history.append({"role": "assistant", "content": result["answer"]})
        history = history[-6:]                               # keep only the last few
```

- `input(...)` pauses for your text. The loop repeats until you type `exit`/`quit` or
  leave it blank.
- The `history` list is what makes the console chat **conversational**: it is passed
  to `answer_question`, which condenses follow-ups against it ([task 09](../tasks/09-conversational-rag.md)).
  We keep only the last few turns to bound the prompt.

```python
def main():
    actions = {"1": build_index, "2": show_status, "3": do_search, "4": ask_once, "5": chat}
    while True:
        print(MENU)
        choice = input("Select an option: ").strip()
        if choice == "0":
            break
        action = actions.get(choice)                         # None if key not in dict
        if action:
            action()                                         # call the chosen function
        else:
            print("❓ Unknown option ...")

if __name__ == "__main__":                                   # run only when executed directly
    main()
```

- The `actions` **dictionary** maps a typed key to a function — cleaner than a long
  if/elif chain. `if __name__ == "__main__":` runs `main()` only when you execute the
  file directly (`uv run python main.py`), not when it's imported.

## 7. `app.py` — the browser UI (Streamlit)

The key Streamlit fact: **the whole script re-runs top to bottom on every
interaction.** State that must survive reruns lives in `st.session_state`.

```python
with st.sidebar:                                             # everything here goes in the left sidebar
    notice = st.session_state.pop("notice", None)            # read-and-remove a one-time message
    if notice:
        getattr(st, notice[0])(notice[1])                    # e.g. st.success("...") or st.error("...")

    status = get_index_status()
    st.success(...) if status["exists"] else st.warning(...) # green/amber status box

    if st.button("Build / rebuild index"):                  # True on the run it's clicked
        with st.spinner("Embedding documents…"):
            try:
                process_documents_folder()
                st.session_state["notice"] = ("success", "✅ Index rebuilt.")
            except Exception as exc:
                st.session_state["notice"] = ("error", f"Build failed: {exc}")
        st.rerun()                                           # reload so status/notice refresh
```

- `getattr(st, "success")` returns `st.success` — a trick to pick the message style
  dynamically. The `try/except` turns build failures into a friendly message.

```python
if not get_index_status()["exists"]:
    st.info("Add .md files ... then click Build / rebuild index ...")
    st.stop()                                                # halt here until an index exists
```

```python
if "messages" not in st.session_state:
    st.session_state.messages = []                           # init history once
for message in st.session_state.messages:                    # redraw the conversation each rerun
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("contexts"):
            render_sources(message["contexts"])
```

- The history loop is why the conversation stays on screen across reruns. The recent
  turns are **also sent to the model** (below) so follow-up questions are understood —
  that is the prompt chaining from [task 09](../tasks/09-conversational-rag.md).

```python
if query := st.chat_input("Ask a question about your documents"):  # walrus := assigns and tests
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            history = st.session_state.messages[:-1][-6:]    # recent turns, minus this one
            try:
                result = answer_question(query, n_results=3, history=history)
            except Exception as exc:
                st.error(f"Could not generate an answer: {exc}")
                st.stop()
        st.markdown(result["answer"])
        render_sources(result["contexts"])
    st.session_state.messages.append({"role": "assistant",
        "content": result["answer"], "contexts": result["contexts"]})
```

- `:=` is the **walrus operator** — it assigns `query` and checks it's non-empty in
  one expression. The new question is saved to history, then answered with the recent
  turns as `history` (so follow-ups get rewritten), guarded by try/except, shown with
  its sources, and the answer appended to history. `messages[:-1]` drops the question
  we just appended; `[-6:]` keeps the last few turns.

## Python idioms used here

| Idiom | Means |
|-------|-------|
| `f"{x}"` | f-string — insert `x` into text |
| `[f(x) for x in items]` | list comprehension — build a list with a compact loop |
| `try: ... except Exception:` | run code; handle errors instead of crashing |
| `@lru_cache` | decorator that caches a function's result |
| `:=` | walrus — assign and use a value in one expression |
| `with open(...) as f:` | context manager — auto-closes the file afterward |
| `if __name__ == "__main__":` | run this block only when the file is executed directly |
| `settings = Settings()` | create one shared object the whole app imports |

→ Next: [Using the RAG](04-using-the-rag.md)
