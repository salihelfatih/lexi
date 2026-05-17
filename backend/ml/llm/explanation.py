"""Grounded explanation generation entrypoint."""

from backend.ml.llm.prompts import EXPLANATION_PROMPT


def build_grounded_explanation(context: str) -> dict[str, str]:
    """Return prompt payload for downstream LLM client integration."""
    return {
        "prompt": EXPLANATION_PROMPT,
        "context": context,
    }
