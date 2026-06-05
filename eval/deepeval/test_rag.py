"""
DeepEval tests for the local RAG — the traditional pytest-style approach.

The DeepEval pattern (the principles):
  1. run the system to get an output            -> answer_question(question)
  2. wrap it in an LLMTestCase                   -> input, actual_output, retrieval_context
  3. assert it against metrics                   -> assert_test(test_case, [metrics])
  4. run the file                                -> deepeval test run eval/deepeval/test_rag.py

Each metric is judged by a LOCAL Ollama model, configured in code (below) so the
suite is reproducible for anyone who clones the repo — no API key, no machine-global
setup.

Run from the repo root (build the index first if needed):
  uv run python -c "from utils import process_documents_folder; process_documents_folder()"
  uv run deepeval test run eval/deepeval/test_rag.py
"""

import os
import sys
from pathlib import Path
import pytest

# Make the project importable and resolve ./data/chroma_db regardless of CWD.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric
from deepeval.models import OllamaModel

from utils import answer_question

# The judge LLM: a local Ollama model. It GRADES the answers (it is not the RAG's
# own generator call). Passing it explicitly keeps the suite fully local.
JUDGE = OllamaModel(model="llama3.1:8b", base_url="http://localhost:11434")

# Questions to evaluate, written out explicitly (declarative — like the promptfoo
# config). Each is answerable from the sample documents.
QUESTIONS = [
    "What is the refund window in the returns policy?",
    "How long is the standard warranty?",
    "Who is the lead scientist on Project Meridian?",
    "What was the maximum dive depth recorded?",
    "Who is the research director of the Quantum Computing Research Laboratory?",
    "What is the laboratory's research focus?",
]


@pytest.mark.parametrize("question", QUESTIONS)
def test_rag(question):
    """Run the RAG, then grade the answer with two RAG metrics (local judge)."""
    result = answer_question(question, n_results=3)

    test_case = LLMTestCase(
        input=question,
        actual_output=result["answer"],
        retrieval_context=result["contexts"],
    )

    assert_test(test_case, metrics=[
        # Faithfulness: is the answer supported by the retrieved context?
        FaithfulnessMetric(threshold=0.7, model=JUDGE),
        # Answer relevancy: does the answer actually address the question?
        AnswerRelevancyMetric(threshold=0.7, model=JUDGE),
    ])
