"""
RAG answer generation: retrieve context, then generate an answer with a local LLM.
"""

import sys
from pathlib import Path
from langchain_ollama import OllamaLLM

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config.settings import settings
from .document_search import search_documents


def answer_question(query: str, n_results: int = 3) -> dict:
    """Answer a question using retrieved document context and a local LLM.

    Returns:
        dict: {"answer": <generated answer>, "contexts": <list of context chunks used>}
    """
    # Step 1: retrieve the most relevant chunks
    result = search_documents(query, n_results=n_results)
    contexts = result["chunks"]

    # Step 2: build the prompt with the chunks as context
    prompt = settings.format_rag_prompt(
        context="\n\n".join(contexts),
        question=query,
    )

    # Step 3: generate an answer with the local Ollama model
    llm = OllamaLLM(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
    )
    answer = llm.invoke(prompt)

    # Step 4: return both the answer and the contexts it was based on
    return {"answer": answer, "contexts": contexts}
