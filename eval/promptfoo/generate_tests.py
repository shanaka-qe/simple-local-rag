"""Generate promptfoo test cases from the shared golden dataset.

promptfoo calls `create_tests()` (referenced as
`tests: file://generate_tests.py:create_tests`) and expects a list of test dicts.
Reading eval/dataset.yaml here keeps that file the single source of truth.
"""

from pathlib import Path
import yaml

DATASET = Path(__file__).resolve().parents[1] / "dataset.yaml"


def create_tests():
    cases = yaml.safe_load(DATASET.read_text())["cases"]
    tests = []

    for case in cases:
        asserts = []

        if case["answerable"]:
            # Deterministic: the answer must contain the key fact(s).
            for substring in case.get("expected_contains", []):
                asserts.append({
                    "type": "icontains",
                    "value": substring,
                    "metric": "contains-fact",
                })
            # Model-graded: a local LLM judges whether the answer is grounded.
            asserts.append({
                "type": "llm-rubric",
                "value": (
                    "The answer is grounded in the provided documents and conveys "
                    f"this: {case['expected_answer']}"
                ),
                "metric": "grounded",
            })
        else:
            # Honesty check: the RAG should decline, not invent an answer.
            asserts.append({
                "type": "llm-rubric",
                "value": (
                    "The answer declines or states the information is not in the "
                    "documents. It must NOT invent a specific figure, name, or fact."
                ),
                "metric": "declines-unknown",
            })

        tests.append({
            "description": case["id"],
            "vars": {"question": case["question"]},
            "assert": asserts,
        })

    return tests
