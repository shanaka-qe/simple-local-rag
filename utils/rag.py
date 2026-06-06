"""
RAG answer generation: retrieve context, then generate an answer with a local LLM.

For multi-turn chat this uses a simple two-step "prompt chain":
  1. condense  — rewrite a follow-up question into a standalone one (using history)
  2. retrieve + answer — search with the standalone question, then write the answer
"""

import sys
from pathlib import Path
from langchain_ollama import OllamaLLM

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import settings
from .document_search import search_documents


def _get_llm():
    """Create the local Ollama LLM used for both chain steps."""
    return OllamaLLM(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
    )


def _format_history(history) -> str:
    """Turn a list of {"role", "content"} messages into a readable transcript."""
    lines = []
    for message in history:
        speaker = "User" if message["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {message['content']}")
    return "\n".join(lines)


def condense_question(query: str, history) -> str:
    """Rewrite a follow-up question into a standalone one using the chat history.

    This is the first link in the prompt chain. It lets follow-ups like
    "how long is it?" become "how long is the standard warranty?" so that the
    document search below has enough to work with.
    """
    prompt = settings.format_condense_prompt(
        history=_format_history(history),
        question=query,
    )
    return _get_llm().invoke(prompt).strip()


def answer_question(query: str, n_results: int = 3, history=None) -> dict:
    """Answer a question using retrieved document context and a local LLM.

    If `history` (a list of {"role", "content"} messages) is given, the question
    is first condensed into a standalone query so follow-up questions still
    retrieve the right documents. With no history it behaves exactly as a
    single-turn RAG.

    Returns:
        dict: {"answer": <generated answer>, "contexts": <list of context chunks used>}
    """
    # Chain step 1: rewrite a follow-up into a standalone question (only when
    # there is prior conversation to resolve references like "it" or "that").
    search_query = condense_question(query, history) if history else query

    # Retrieve the most relevant chunks for the standalone question.
    result = search_documents(search_query, n_results=n_results)
    contexts = result["chunks"]

    # Chain step 2: generate an answer from the retrieved context.
    prompt = settings.format_rag_prompt(
        context="\n\n".join(contexts),
        question=search_query,
    )
    answer = _get_llm().invoke(prompt)

    # Return both the answer and the contexts it was based on.
    return {"answer": answer, "contexts": contexts}
