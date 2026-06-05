"""
Ragas evaluation for the local RAG — RAG-specific metrics, fully local.

Ragas isn't pytest or YAML: you build an evaluation dataset, run `evaluate(...)`,
and read a scores table. The pattern (the principles):

  1. for each question, run the RAG to get the answer + retrieved contexts
  2. build a sample: user_input, response, retrieved_contexts, reference (ground truth)
  3. evaluate the dataset with metrics, using a LOCAL judge LLM + LOCAL embeddings
  4. print the scores

Why Ragas alongside promptfoo/DeepEval: its metrics separate RETRIEVAL quality
(did we fetch the right context?) from ANSWER quality (is the answer faithful and
relevant?).

Run from the repo root (build the index first if needed):
  uv run python -c "from utils import process_documents_folder; process_documents_folder()"
  uv run python eval/ragas/run_ragas.py
"""

import os
import sys
import warnings
from pathlib import Path

# Make the project importable and resolve ./data/chroma_db regardless of CWD.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

# Ragas 0.4 still ships the LangChain wrappers used here but warns that v1.0 will
# move to llm_factory / ragas.metrics.collections. We use the current, widely
# documented API and silence the migration noise.
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_ollama import ChatOllama
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithReference,
    LLMContextRecall,
)

from config.settings import settings
from utils import answer_question
from utils.document_search import get_embeddings_model

# Cases written out explicitly (declarative). `reference` is the ground-truth
# answer the retrieval/answer metrics are scored against.
CASES = [
    {
        "question": "What is the refund window in the returns policy?",
        "reference": "The refund window is 30 days from the delivery date.",
    },
    {
        "question": "Who is the lead scientist on Project Meridian?",
        "reference": "The lead scientist is Dr. Hana Okafor.",
    },
    {
        "question": "Who is the research director of the Quantum Computing Research Laboratory?",
        "reference": "The research director is Prof. Elena Rodriguez.",
    },
    {
        "question": "How long is the standard warranty?",
        "reference": "The standard warranty is 24 months from the date of purchase.",
    },
]


def build_dataset() -> EvaluationDataset:
    """Run the RAG for each case and assemble the Ragas evaluation dataset."""
    samples = []
    for case in CASES:
        result = answer_question(case["question"], n_results=3)
        samples.append({
            "user_input": case["question"],
            "response": result["answer"],
            "retrieved_contexts": result["contexts"],
            "reference": case["reference"],
        })
    return EvaluationDataset.from_list(samples)


def main():
    print("Building dataset (running the RAG for each case)...")
    dataset = build_dataset()

    # Local judge LLM and local embeddings — nothing leaves the machine.
    judge = LangchainLLMWrapper(
        ChatOllama(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL)
    )
    embeddings = LangchainEmbeddingsWrapper(get_embeddings_model())

    metrics = [
        # Retrieval quality (need the reference / ground truth)
        LLMContextPrecisionWithReference(),
        LLMContextRecall(),
        # Answer quality
        Faithfulness(),
        ResponseRelevancy(),
    ]

    print("Evaluating with the local judge (this takes a few minutes on CPU)...\n")
    result = evaluate(dataset=dataset, metrics=metrics, llm=judge, embeddings=embeddings)

    print("\n=== Aggregate scores ===")
    print(result)
    print("\n=== Per-case scores ===")
    print(result.to_pandas().to_string())


if __name__ == "__main__":
    main()
