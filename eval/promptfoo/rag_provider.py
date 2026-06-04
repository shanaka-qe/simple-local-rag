"""promptfoo custom provider: run the local RAG and return its answer.

promptfoo calls `call_api` with the rendered prompt (here, the question). We run
the full RAG pipeline (retrieve + generate) and return the answer so promptfoo can
assert on the real system, not just the bare LLM.
"""

import os
import sys
from pathlib import Path

# Make the project importable and resolve relative paths (e.g. ./data/chroma_db),
# regardless of where promptfoo is invoked from.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

from utils import answer_question


def call_api(prompt, options, context):
    """Return the RAG answer for a question.

    Args:
        prompt: the rendered prompt — the question, from `prompts: ["{{question}}"]`.
        options: provider config from the YAML (unused here).
        context: test-case info including vars (unused here).
    """
    try:
        result = answer_question(prompt, n_results=3)
        return {
            "output": result["answer"],
            "metadata": {"contexts": result["contexts"]},
        }
    except Exception as exc:  # surface failures to promptfoo instead of crashing
        return {"output": "", "error": str(exc)}
